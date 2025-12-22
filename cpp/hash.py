class HashIndex:
    def __init__(self, table_name, index_col, bucket_count=200):
        # 初始化：设定表名、索引字段、桶数量
        self.table_name = table_name
        self.index_col = index_col
        self.bucket_count = bucket_count  # 哈希桶数量
        self.buckets = [[] for _ in range(bucket_count)]  # 桶列表（链地址法）

    def build(self, data):
        """核心：从数据构建哈希索引"""
        for row_num, record in enumerate(data, start=2):  # 行号从2开始（表头为1）
            index_val = record[self.index_col]  # 获取索引字段值
            
            # 核心步骤1：计算哈希值并取模，确定桶位置
            bucket_idx = hash(index_val) % self.bucket_count
            
            # 核心步骤2：将(索引值, 行号)存入对应桶（解决冲突）
            self.buckets[bucket_idx].append((index_val, row_num))

    def search(self, index_val):
        """核心：查询哈希索引"""
        # 核心步骤1：计算目标桶位置（与构建时算法一致）
        bucket_idx = hash(index_val) % self.bucket_count
        
        # 核心步骤2：在目标桶中匹配索引值，返回行号
        return [row_num for (val, row_num) in self.buckets[bucket_idx] 
                if val == index_val]


# 演示逻辑
if __name__ == "__main__":
    # 模拟数据：[{索引字段: 值, ...}, ...]
    mock_data = [{"phone": "13800138000", "name": "张三"},
                 {"phone": "13900139000", "name": "李四"}]
    
    # 1. 构建哈希索引（以手机号为索引）
    phone_index = HashIndex("User", "phone")
    phone_index.build(mock_data)
    
    # 2. 查询索引
    result = phone_index.search("13800138000")
    print(f"查询结果行号：{result}")  # 输出：[2]