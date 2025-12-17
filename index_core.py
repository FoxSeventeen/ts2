# index_core.py
import pickle
import os
from db_core import read_csv, DATA_DIR, INDEX_DIR  # 导入核心模块和路径常量


# -------------------------- 有序索引（快递单号）--------------------------
def build_order_index():
    """构建快递单号有序索引（基于B+树简化）"""
    file_path = "database/data/ExpressOrder.csv"
    index_path = "database/index/ExpressOrder_orderId.idx"
    orders = read_csv(file_path)

    # 生成索引：{快递单号: [行号1, 行号2,...]}（行号从2开始，首行为列名）
    index_dict = {}
    for row_num, order in enumerate(orders, start=2):
        order_id = order['orderId']
        if order_id not in index_dict:
            index_dict[order_id] = []
        index_dict[order_id].append(row_num)

    # 保存索引到文件（文本格式，便于查看）
    with open(index_path, 'w', encoding='utf-8') as f:
        for order_id, row_nums in index_dict.items():
            f.write(f"{order_id},{','.join(map(str, row_nums))}\n")
    print("快递单号有序索引构建完成")


def search_order_index(order_id):
    """查询快递单号有序索引，返回匹配行号"""
    index_path = "database/index/ExpressOrder_orderId.idx"
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if parts[0] == order_id:
                    return list(map(int, parts[1:]))
        return []
    except FileNotFoundError:
        print("索引文件不存在，请先构建索引")
        build_order_index()
        return search_order_index(order_id)


# -------------------------- 散列索引（用户手机号）--------------------------


class HashIndex:
    def __init__(self, table_name, index_col, bucket_count=200):
        """
        初始化哈希索引
        :param table_name: 表名（如"User"、"ExpressOrder"）
        :param index_col: 索引字段（如"uphone"、"orderId"）
        :param bucket_count: 哈希桶数量（默认200，可根据数据量调整）
        """
        self.table_name = table_name
        self.index_col = index_col
        self.bucket_count = bucket_count
        self.buckets = [[] for _ in range(bucket_count)]  # 链地址法存储 (索引值, 行号)
        self.loaded = False  # 标记索引是否已加载

    def build(self):
        """从数据表构建索引（核心方法）"""
        # 1. 读取数据表
        table_path = f"{DATA_DIR}/{self.table_name}.csv"
        data = read_csv(table_path)
        if not data:
            print(f"警告：{self.table_name}.csv 无数据，索引构建为空")
            return False

        # 2. 校验索引字段是否存在
        if self.index_col not in data[0]:
            print(f"错误：表{self.table_name}中不存在字段{self.index_col}，索引构建失败")
            return False

        # 3. 构建哈希索引（链地址法处理冲突）
        self.buckets = [[] for _ in range(self.bucket_count)]  # 重置桶
        for row_num, record in enumerate(data, start=2):  # 行号从2开始（首行为列名）
            index_val = record[self.index_col]
            # 计算哈希值并取模（确保桶索引在有效范围）
            bucket_idx = hash(index_val) % self.bucket_count
            self.buckets[bucket_idx].append((index_val, row_num))

        # 4. 保存索引到文件
        self.save()
        self.loaded = True  # 标记为已加载
        print(f"✅ 索引构建完成：{self.table_name}_{self.index_col}（{len(data)}条数据）")
        return True

    def save(self):
        """将索引保存到文件（二进制格式，高效读写）"""
        # 确保索引目录存在
        os.makedirs(INDEX_DIR, exist_ok=True)
        index_path = f"{INDEX_DIR}/{self.table_name}_{self.index_col}_hash.idx"

        # 保存桶数量和桶数据（便于加载时恢复）
        with open(index_path, 'wb') as f:
            pickle.dump((self.bucket_count, self.buckets), f)

    def load(self):
        """加载已保存的索引文件（若不存在则自动构建）"""
        if self.loaded:
            return True  # 已加载，直接返回

        index_path = f"{INDEX_DIR}/{self.table_name}_{self.index_col}_hash.idx"
        try:
            # 读取索引文件
            with open(index_path, 'rb') as f:
                self.bucket_count, self.buckets = pickle.load(f)
            self.loaded = True
            print(f"✅ 索引加载成功：{self.table_name}_{self.index_col}")
            return True
        except FileNotFoundError:
            # 索引文件不存在，自动构建
            print(f"⚠️ 索引文件不存在，自动构建...")
            return self.build()
        except Exception as e:
            print(f"❌ 索引加载失败：{e}，尝试重新构建...")
            return self.build()

    def search(self, index_val):
        """
        查询索引，返回匹配的行号列表
        :param index_val: 要查询的索引值（如手机号"13800138000"）
        :return: 匹配的行号列表（行号对应数据表中的实际行）
        """
        # 确保索引已加载
        if not self.load():
            return []

        # 计算目标桶索引
        bucket_idx = hash(index_val) % self.bucket_count
        # 从桶中筛选匹配的行号
        match_rows = [row_num for (val, row_num) in self.buckets[bucket_idx] if val == index_val]
        print(f"🔍 索引查询结果：{self.index_col}={index_val} 匹配{len(match_rows)}条记录")
        return match_rows

    def rebuild(self):
        """强制重建索引（用于数据更新后同步）"""
        print(f"🔄 开始重建索引：{self.table_name}_{self.index_col}")
        return self.build()
# 使用示例（后续在main.py或GUI中调用）
if __name__ == "__main__":
    # 构建快递单号有序索引
    build_order_index()
    # 构建用户手机号散列索引
    user_phone_index = HashIndex("User", "phone")
    user_phone_index.build()