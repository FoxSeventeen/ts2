# db_core.py


import csv
from datetime import datetime


# 新增常量定义（文件顶部）
DATA_DIR = "database/data"
INDEX_DIR = "database/index"
VIEWS_META_PATH = "database/views.meta"

# 快递单状态映射（替代硬编码）
ORDER_STATUS_MAP = {
    '0': '待收件',
    '1': '已收件',
    '2': '中转中',
    '3': '派送中',
    '4': '已签收',
    '5': '异常'
}

# db_core.py 中修改 read_csv 函数
def read_csv(file_path):
    """通用读取CSV文件，返回字典列表（增加编码兼容）"""
    # 定义常见编码列表（按优先级尝试）
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                return list(reader)
        except UnicodeDecodeError:
            continue  # 该编码失败，尝试下一个
        except FileNotFoundError:
            print(f"错误：文件{file_path}不存在")
            return []
        except Exception as e:
            print(f"读取CSV失败（编码{encoding}）：{e}")
            continue
    
    # 所有编码都失败
    print(f"错误：文件{file_path}不支持常见编码（UTF-8/GBK/GB2312）")
    return []
"""
# 文件读写
def read_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)  # 转换为列表，便于后续操作
    except FileNotFoundError:
        print(f"错误：文件{file_path}不存在")
        return []
    except Exception as e:
        print(f"读取CSV失败：{e}")
        return []

"""
def write_csv(file_path, records, mode='a'):
    # 通用写入CSV文件（支持单条/批量写入，默认追加模式
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    try:
        # 确保records是可迭代对象
        if not isinstance(records, list):
            records = [records]

        # 读取列名（首行）
        with open(file_path, 'r', encoding='utf-8') as f:
            columns = csv.DictReader(f).fieldnames

        # 补全缺失字段为NULL
        full_records = []
        for record in records:
            full_record = {col: record.get(col, 'NULL') for col in columns}
            full_records.append(full_record)

        # 写入文件
        with open(file_path, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            if mode == 'w':  # 覆盖模式需重新写入列名
                writer.writeheader()
            writer.writerows(full_records)  # 批量写入
        return True
    except Exception as e:
        print(f"写入CSV失败：{e}")
        return False

# ----------快递单号----------
# db_core.py 续
# db_core.py（修改insert_express_order）
def insert_express_order(order_data):
    file_path = f"{DATA_DIR}/ExpressOrder.csv"
    # 补全默认字段
    order_data.setdefault('sendTime', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    order_data.setdefault('orderStatus', '0')  # 0=待收件
    # 验证必填字段（senderId和receiverId对应User表的uid）
    required_fields = ['orderId', 'senderId', 'receiverId', 'goodsName', 'goodsWeight', 'sendBranchId',
                       'targetBranchId']
    if not all(field in order_data for field in required_fields):
        print("错误：缺少必填字段（senderId/receiverId对应User表的uid）")
        return False

    # 额外验证：寄件人/收件人是否存在（关联User表）
    users = read_csv(f"{DATA_DIR}/User.csv")
    user_ids = [user['uid'] for user in users]
    if order_data['senderId'] not in user_ids or order_data['receiverId'] not in user_ids:
        print("错误：寄件人或收件人不存在（uid未在User表中）")
        return False
    success = write_csv(file_path, order_data)
    if success:
        # 新增：重建orderId索引
        from index_core import HashIndex
        order_index = HashIndex("ExpressOrder", "orderId")  # 表名+字段名
        order_index.rebuild()  # 强制同步新数据到索引
        print("快递单添加成功，索引已更新")
    return success

def query_express_order(condition=None, use_index=False):
    """查询快递单，支持条件过滤和索引查询"""
    file_path = f"{DATA_DIR}/ExpressOrder.csv"
    orders = read_csv(file_path)
    if not orders:
        return []

    # 索引查询优先（若启用且条件包含orderId）
    if use_index and condition and 'orderId' in condition:
        # 修复：使用HashIndex类查询，而非search_order_index
        from index_core import HashIndex
        # 初始化orderId索引
        order_index = HashIndex(table_name="ExpressOrder", index_col="orderId")
        # 查询索引，获取匹配的行号（行号从2开始）
        match_rows = order_index.search(condition['orderId'])
        # 映射到列表索引（行号-2 = 列表索引，因为orders[0]对应行号2）
        index_matched = [
            row_num - 2
            for row_num in match_rows
            if 2 <= row_num - 2 < len(orders)  # 确保索引有效
        ]
        # 过滤出匹配的快递单
        orders = [orders[i] for i in index_matched]
        print(f"索引查询到{len(orders)}条匹配的快递单")

    # 条件过滤（处理其他条件，如状态、网点等）
    if condition:
        # 排除已通过索引查询的orderId条件
        filter_cond = {k: v for k, v in condition.items() if k != 'orderId'}
        if filter_cond:
            orders = [
                order for order in orders
                if all(order.get(k) == v for k, v in filter_cond.items())
            ]

    return orders

def update_express_order(order_id, update_data):
    """更新快递单信息（增强状态变更校验）"""
    file_path = f"{DATA_DIR}/ExpressOrder.csv"
    orders = read_csv(file_path)
    if not orders:
        return False

    # 定义合法状态流转（0->1->2->3->4，0/1/2/3->5）
    valid_transitions = {
        '0': ['1', '5'],    # 待收件 -> 已收件/异常
        '1': ['2', '5'],    # 已收件 -> 中转中/异常
        '2': ['3', '5'],    # 中转中 -> 派送中/异常
        '3': ['4', '5'],    # 派送中 -> 已签收/异常
        '4': [],            # 已签收不能变更
        '5': []             # 异常不能变更
    }

    # 查找目标快递单并校验状态
    updated = False
    for order in orders:
        if order['orderId'] == order_id:
            # 状态变更校验
            if 'orderStatus' in update_data:
                current_status = order['orderStatus']
                new_status = update_data['orderStatus']
                if new_status not in valid_transitions[current_status]:
                    print(f"错误：状态从{current_status}到{new_status}的流转不合法")
                    return False
            # 执行更新
            for key, value in update_data.items():
                if key in order:
                    order[key] = value
            updated = True
            break

    if updated:
        return write_csv(file_path, orders, mode='w')
    else:
        print("未找到目标快递单")
        return False

def delete_express_order(order_id):
    """删除快递单"""
    file_path = f"{DATA_DIR}/ExpressOrder.csv"
    orders = read_csv(file_path)
    if not orders:
        return False

    # 过滤掉待删除记录
    remaining_orders = [order for order in orders if order['orderId'] != order_id]
    if len(remaining_orders) == len(orders):
        print("未找到目标快递单")
        return False

    # 批量写入优化
    return write_csv(file_path, remaining_orders, mode='w')


# ----------------------快递轨迹--------------------------



# ------------------用户---------------------------------

# db_core.py（新增用户表操作函数）
def insert_user(user_data):
    """插入用户（寄件人/收件人）"""
    file_path = f"{DATA_DIR}/User.csv"
    # 验证必填字段
    required_fields = ['uid', 'uname', 'utype', 'uphone', 'uprovince', 'ucity', 'uaddress']
    if not all(field in user_data for field in required_fields):
        print("错误：缺少必填字段（uid/姓名/手机号/地址等）")
        return False

    # 格式验证（用户自定义完整性约束）
    if not user_data['uphone'].isdigit() or len(user_data['uphone']) != 11:
        print("错误：手机号必须是11位数字")
        return False
    if user_data['utype'] not in ['普通用户', '商家用户', '快递员']:
        print("错误：用户类型只能是「普通用户」「商家用户」「快递员」")
        return False
    if user_data.get('uidcard') and (len(user_data['uidcard']) != 18 or not user_data['uidcard'][:-1].isdigit()):
        print("错误：身份证号格式错误（18位，最后一位可为X）")
        return False

    # 验证uid唯一
    users = read_csv(file_path)
    if any(user['uid'] == user_data['uid'] for user in users):
        print("错误：uid已存在（用户ID必须唯一）")
        return False

    success = write_csv(file_path, user_data)
    if success:
        # 数据添加成功后，重建uphone索引
        from index_core import HashIndex
        user_phone_index = HashIndex("User", "uphone")  # 表名+索引字段
        user_phone_index.build()  # 重建索引（自动读取最新数据）
        print("用户添加成功，索引已同步更新")
    return success


def query_user(condition=None):
    """查询用户（支持按手机号、省份、城市等条件）"""
    file_path = f"{DATA_DIR}/User.csv"
    users = read_csv(file_path)
    if not users or not condition:
        return users

    # 条件过滤（如{"uphone": "13800138000", "ucity": "北京市"}）
    results = []
    for user in users:
        match = True
        for key, value in condition.items():
            if user[key] != value:
                match = False
                break
        if match:
            results.append(user)
    return results

def update_user(uid, update_data):
    """更新用户信息"""
    file_path = f"{DATA_DIR}/User.csv"
    users = read_csv(file_path)
    if not users:
        return False


    # 查找目标用户
    updated = False
    for user in users:
        if user['uid'] == uid:
            # 验证更新字段（如手机号格式）
            if 'uphone' in update_data:
                phone = update_data['uphone']
                if not (phone.isdigit() and len(phone) == 11):
                    print("错误：手机号必须是11位数字")
                    return False
            # 执行更新
            for key, value in update_data.items():
                if key in user:
                    user[key] = value
            updated = True
            break

    if updated:
        return write_csv(file_path, users, mode='w')
    else:
        print("未找到目标用户")
        return False


def delete_user(uid):
    """删除用户"""
    file_path = f"{DATA_DIR}/User.csv"
    users = read_csv(file_path)
    if not users:
        return False

    # 过滤掉待删除用户
    remaining_users = [user for user in users if user['uid'] != uid]
    if len(remaining_users) == len(users):
        print("未找到目标用户")
        return False

    # 检查用户是否有关联快递单（外键约束简化版）
    orders = read_csv(f"{DATA_DIR}/ExpressOrder.csv")
    if any(order['senderId'] == uid or order['receiverId'] == uid for order in orders):
        print("错误：用户存在关联快递单，无法删除")
        return False

    return write_csv(file_path, remaining_users, mode='w')



# db_core.py 续
def join_courier_orders(courier_id, date):
    """多表连接：查询快递员今日派送的快递（Courier + ExpressOrder + User）"""
    # 读取三张表数据
    courier_path = f"{DATA_DIR}/Courier.csv"
    order_path = f"{DATA_DIR}/ExpressOrder.csv"
    user_path = f"{DATA_DIR}/User.csv"
    couriers = read_csv(courier_path )
    orders = read_csv(order_path)
    users = read_csv(user_path)

    results = []
    # 嵌套循环连接（简化版，适合小数据量）
    for courier in couriers:
        if courier['courierId'] != courier_id:
            continue
        # 匹配快递员所属网点的快递
        for order in orders:
            if (order['targetBranchId'] != courier['branchId'] or
                    order['orderStatus'] not in ['3', '4'] or  # 派送中/已签收
                    not order['sendTime'].startswith(date)):
                continue
            # 匹配收件人信息
            for user in users:
                if user['uId'] == order['receiverId']:
                    results.append({
                        '快递单号': order['orderId'],
                        '收件人姓名': user['uName'],
                        '收件人电话': user['uphone'],
                        '物品名称': order['goodsName'],
                        '状态': ORDER_STATUS_MAP[order['orderStatus']],
                        '寄件时间': order['sendTime']
                    })
    return results


# -------------------------- 视图功能（视图消解法）--------------------------
def create_view(view_name, define_sql, creator_id):
    """创建视图，存储定义到views.meta"""
    meta_path = VIEWS_META_PATH
    # 验证视图名唯一性
    with open(meta_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().split('|')[0] == view_name:
                print("视图已存在")
                return False
    # 写入视图元数据
    create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(meta_path, 'a', encoding='utf-8') as f:
        f.write(f"{view_name}|{define_sql}|{create_time}|{creator_id}\n")
    return True


def query_view(view_name, condition=None):
    """查询视图：解析SQL并执行基础表查询"""
    meta_path = VIEWS_META_PATH
    define_sql = None
    # 读取视图定义
    with open(meta_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if parts[0] == view_name:
                define_sql = parts[1]
                break
    if not define_sql:
        print("视图不存在")
        return []

    # 简化SQL解析（实际可扩展为完整解析器）
    if "BranchMonthlySend" in view_name:
        # 网点月度寄件量统计视图
        orders = read_csv(f"{DATA_DIR}/ExpressOrder.csv")
        stats = {}
        for order in orders:
            key = (order['sendBranchId'], order['sendTime'][:7])  # 网点ID+年月
            stats[key] = stats.get(key, 0) + 1
        # 转换为结果集并过滤条件
        results = []
        for (branch_id, month), count in stats.items():
            res = {'sendBranchId': branch_id, 'month': month, 'sendCount': str(count)}
            if condition and all(res[k] == v for k, v in condition.items()):
                results.append(res)
        return results
    else:
        print("不支持的视图类型")
        return []


