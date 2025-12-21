# db_core.py


import csv
import os
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
    """通用写入CSV文件（支持单条/批量写入，默认追加模式，自动检测编码）"""
    import csv
    import time
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    # 确保records是可迭代对象
    if not isinstance(records, list):
        records = [records]
    
    # 步骤1：尝试多种编码读取列名，并记录成功的编码
    columns = None
    file_encoding = None
    f = None
    for encoding in encodings:
        try:
            f = open(file_path, 'r', encoding=encoding)
            columns = csv.DictReader(f).fieldnames
            file_encoding = encoding  # 记录成功的编码
            f.close()
            f = None
            break
        except (UnicodeDecodeError, FileNotFoundError):
            if f:
                f.close()
                f = None
            continue
        except Exception as e:
            if f:
                f.close()
                f = None
            print(f"读取列名失败（编码{encoding}）：{e}")
            continue
    
    if columns is None or file_encoding is None:
        print(f"错误：无法读取文件{file_path}的列名（所有编码都失败）")
        return False
    
    # 步骤2：补全缺失字段为NULL
    full_records = []
    for record in records:
        full_record = {col: record.get(col, 'NULL') for col in columns}
        full_records.append(full_record)
    
    # 步骤3：使用相同编码写入文件（添加重试机制）
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with open(file_path, mode, newline='', encoding=file_encoding) as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                if mode == 'w':  # 覆盖模式需重新写入列名
                    writer.writeheader()
                writer.writerows(full_records)  # 批量写入
            return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"文件被占用，正在重试（{attempt + 1}/{max_retries}）...")
                time.sleep(0.5)  # 等待0.5秒后重试
            else:
                print(f"写入CSV失败（权限被拒绝）：{e}")
                print("提示：请确保文件未被其他程序（如Excel）打开")
                return False
        except Exception as e:
            print(f"写入CSV失败（编码{file_encoding}）：{e}")
            return False
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
            if 0 <= row_num - 2 < len(orders)  # 确保索引有效
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
    if user_data['utype'] not in ['普通用户', '商家用户']:
        print("错误：用户类型只能是「普通用户」「商家用户」（快递员请使用insert_courier函数）")
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



# ------------------快递员管理---------------------------------

def insert_courier(courier_data):
    """插入快递员"""
    file_path = f"{DATA_DIR}/Courier.csv"
    
    # 验证必填字段
    required_fields = ['courierId', 'courierName', 'courierPhone', 'branchId']
    if not all(field in courier_data for field in required_fields):
        print("错误：缺少必填字段（courierId/courierName/courierPhone/branchId）")
        return False
    
    # 格式验证：手机号
    if not courier_data['courierPhone'].isdigit() or len(courier_data['courierPhone']) != 11:
        print("错误：手机号必须是11位数字")
        return False
    
    # 验证courierId唯一性
    couriers = read_csv(file_path)
    if any(c['courierId'] == courier_data['courierId'] for c in couriers):
        print("错误：courierId已存在（快递员ID必须唯一）")
        return False
    
    # 验证网点是否存在
    branches = read_csv(f"{DATA_DIR}/ExpressBranch.csv")
    if not any(b['branchId'] == courier_data['branchId'] for b in branches):
        print("错误：所属网点不存在（branchId未在ExpressBranch表中）")
        return False
    
    success = write_csv(file_path, courier_data)
    if success:
        print("快递员添加成功")
    return success


def query_courier(condition=None):
    """查询快递员（支持按ID、姓名、手机号、网点等条件）"""
    file_path = f"{DATA_DIR}/Courier.csv"
    couriers = read_csv(file_path)
    if not couriers or not condition:
        return couriers
    
    # 条件过滤
    results = []
    for courier in couriers:
        match = True
        for key, value in condition.items():
            if courier.get(key) != value:
                match = False
                break
        if match:
            results.append(courier)
    return results


def update_courier(courier_id, update_data):
    """更新快递员信息"""
    file_path = f"{DATA_DIR}/Courier.csv"
    couriers = read_csv(file_path)
    if not couriers:
        return False
    
    # 查找目标快递员
    updated = False
    for courier in couriers:
        if courier['courierId'] == courier_id:
            # 验证更新字段（如手机号格式）
            if 'courierPhone' in update_data:
                phone = update_data['courierPhone']
                if not (phone.isdigit() and len(phone) == 11):
                    print("错误：手机号必须是11位数字")
                    return False
            # 验证网点是否存在
            if 'branchId' in update_data:
                branches = read_csv(f"{DATA_DIR}/ExpressBranch.csv")
                if not any(b['branchId'] == update_data['branchId'] for b in branches):
                    print("错误：所属网点不存在")
                    return False
            # 执行更新
            for key, value in update_data.items():
                if key in courier:
                    courier[key] = value
            updated = True
            break
    
    if updated:
        return write_csv(file_path, couriers, mode='w')
    else:
        print("未找到目标快递员")
        return False


def delete_courier(courier_id):
    """删除快递员"""
    file_path = f"{DATA_DIR}/Courier.csv"
    couriers = read_csv(file_path)
    if not couriers:
        return False
    
    # 过滤掉待删除快递员
    remaining_couriers = [c for c in couriers if c['courierId'] != courier_id]
    if len(remaining_couriers) == len(couriers):
        print("未找到目标快递员")
        return False
    
    return write_csv(file_path, remaining_couriers, mode='w')


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
                if user['uid'] == order['receiverId']:
                    results.append({
                        '快递单号': order['orderId'],
                        '收件人姓名': user['uname'],
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
    
    # 检查views.meta文件是否存在
    if not os.path.exists(meta_path):
        print(f"错误：视图元数据文件不存在: {meta_path}")
        return []
    
    define_sql = None
    # 读取视图定义
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if parts[0] == view_name:
                    define_sql = parts[1]
                    break
    except Exception as e:
        print(f"读取视图元数据失败: {e}")
        return []
    
    if not define_sql:
        print(f"视图不存在: {view_name}")
        return []

    # 简化SQL解析（实际可扩展为完整解析器）
    if "BranchMonthlySend" in view_name:
        # 网点月度寄件量统计视图
        orders = read_csv(f"{DATA_DIR}/ExpressOrder.csv")
        if not orders:
            print("警告：快递单表为空")
            return []
        
        stats = {}
        for order in orders:
            # 确保sendTime字段存在且有效
            send_time = order.get('sendTime', '')
            if len(send_time) >= 7:  # 至少包含 "YYYY-MM"
                key = (order['sendBranchId'], send_time[:7])  # 网点ID+年月
                stats[key] = stats.get(key, 0) + 1
        
        # 转换为结果集并过滤条件
        results = []
        for (branch_id, month), count in stats.items():
            res = {'sendBranchId': branch_id, 'month': month, 'sendCount': str(count)}
            # 如果有条件，检查是否匹配；否则返回所有结果
            if condition is None:
                results.append(res)
            elif all(res.get(k) == v for k, v in condition.items()):
                results.append(res)
        return results
    
    elif "CourierDailyStats" in view_name:
        # 快递员每日派送统计视图
        from datetime import datetime
        couriers = read_csv(f"{DATA_DIR}/Courier.csv")
        orders = read_csv(f"{DATA_DIR}/ExpressOrder.csv")
        
        stats = {}
        for order in orders:
            # 统计派送中和已签收的快递
            if order.get('orderStatus') in ['3', '4']:
                send_date = order.get('sendTime', '')[:10]  # 取日期部分
                target_branch = order.get('targetBranchId', '')
                
                # 找到该网点的快递员
                for courier in couriers:
                    if courier.get('branchId') == target_branch:
                        key = (courier['courierId'], send_date)
                        stats[key] = stats.get(key, 0) + 1
        
        results = []
        for (courier_id, date), count in stats.items():
            res = {'courierId': courier_id, 'date': date, 'deliveryCount': str(count)}
            if condition is None:
                results.append(res)
            elif all(res.get(k) == v for k, v in condition.items()):
                results.append(res)
        return results
    
    elif "OrderStatusStats" in view_name:
        # 快递状态分布统计视图
        orders = read_csv(f"{DATA_DIR}/ExpressOrder.csv")
        stats = {}
        for order in orders:
            status = order.get('orderStatus', '')
            status_name = ORDER_STATUS_MAP.get(status, '未知')
            stats[status] = stats.get(status, 0) + 1
        
        results = []
        for status, count in stats.items():
            res = {
                'orderStatus': status, 
                'statusName': ORDER_STATUS_MAP.get(status, '未知'),
                'count': str(count)
            }
            if condition is None:
                results.append(res)
            elif all(res.get(k) == v for k, v in condition.items()):
                results.append(res)
        return results
    
    else:
        print(f"不支持的视图类型: {view_name}")
        return []


