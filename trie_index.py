# trie_index.py
import os
import pickle
from db_core import DATA_DIR, INDEX_DIR

class TrieNode:
    def __init__(self):
        self.children = {}  # 子节点：{字符: TrieNode}
        self.order_ids = set()  # 该前缀对应的快递单ID集合


class PhoneTrieIndex:
    def __init__(self):
        self.root = TrieNode()
        self.index_path = os.path.join(INDEX_DIR, "phone_order_trie.idx")  # 索引保存路径

    def insert(self, phone: str, order_id: str):
        """插入手机号与快递单的关联关系"""
        node = self.root
        for char in phone:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.order_ids.add(order_id)  # 每个前缀都关联订单ID

    def search_prefix(self, prefix: str) -> set:
        """查询前缀对应的所有快递单ID"""
        if not prefix:  # 严格处理空前缀
            return set()
        node = self.root
        for char in prefix:
            if char not in node.children:
                return set()  # 前缀不存在，返回空
            node = node.children[char]
        return node.order_ids.copy()  # 返回副本，避免外部修改
    def build(self):
        """从用户表和快递单表构建Trie索引"""
        # 1. 读取用户表（手机号与用户ID映射，过滤无效数据）
        user_path = os.path.join(DATA_DIR, "User.csv")
        from db_core import read_csv
        users = read_csv(user_path)
        # 过滤掉手机号为空或无效的用户
        phone_to_uid = {}
        for user in users:
            uphone = user.get('uphone', '').strip()
            uid = user.get('uid', '').strip()
            if uphone and uid and uphone.isdigit() and len(uphone) == 11:  # 验证手机号有效性
                phone_to_uid[uphone] = uid

        # 2. 读取快递单表（关联寄件人/收件人）
        order_path = os.path.join(DATA_DIR, "ExpressOrder.csv")
        orders = read_csv(order_path)

        # 3. 清空现有索引（避免累积旧数据）
        self.root = TrieNode()  # 关键修复：重建前清空根节点

        # 4. 建立手机号与快递单的关联
        for order in orders:
            order_id = order.get('orderId', '').strip()
            if not order_id:
                continue  # 跳过无订单ID的记录

            # 关联寄件人手机号
            sender_id = order.get('senderId', '').strip()
            sender_phone = next((p for p, uid in phone_to_uid.items() if uid == sender_id), None)
            if sender_phone:
                self.insert(sender_phone, order_id)

            # 关联收件人手机号
            receiver_id = order.get('receiverId', '').strip()
            receiver_phone = next((p for p, uid in phone_to_uid.items() if uid == receiver_id), None)
            if receiver_phone:
                self.insert(receiver_phone, order_id)

        # 5. 保存索引
        self.save()
        print("手机号前缀-Trie索引构建完成")
        return True

    def save(self):
        """保存索引到文件"""
        os.makedirs(INDEX_DIR, exist_ok=True)
        with open(self.index_path, 'wb') as f:
            pickle.dump(self, f)

    def load(self) -> bool:
        """从文件加载索引"""
        if os.path.exists(self.index_path):
            with open(self.index_path, 'rb') as f:
                loaded = pickle.load(f)
                self.root = loaded.root
                return True
        return False

    def rebuild(self):
        """重建索引（数据更新后调用）"""
        return self.build()