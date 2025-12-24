import random

class ExpressOrderTreapNode:
    def __init__(self, order_id, order_data):
        self.order_id = order_id  # 快递单号（作为键值）
        self.order_data = order_data  # 存储完整快递单信息
        self.priority = random.randint(0, 100000)  # 随机优先级（维护堆性质）
        self.left = None  # 左子树
        self.right = None  # 右子树
        self.size = 1  # 子树大小（用于排名计算）

class ExpressOrderTreap:
    def __init__(self):
        self.root = None  # 根节点
        # 初始化时从CSV加载数据（简化版）
        self._load_from_csv()
    
    def _load_from_csv(self):
        """从CSV加载快递单数据到Treap（实际项目中调用read_csv）"""
        # 模拟数据：实际应替换为db_core.read_csv的结果
        mock_orders = [
            {"orderId": "1001", "senderId": "u001", "orderStatus": "1"},
            {"orderId": "1003", "senderId": "u002", "orderStatus": "2"},
            {"orderId": "1002", "senderId": "u003", "orderStatus": "3"}
        ]
        for order in mock_orders:
            self.insert(order["orderId"], order)
    
    def _update_size(self, node):
        """更新节点的子树大小"""
        if node:
            node.size = 1
            if node.left:
                node.size += node.left.size
            if node.right:
                node.size += node.right.size
    
    def _rotate_left(self, node):
        """左旋操作（维护平衡）"""
        right_child = node.right
        node.right = right_child.left
        right_child.left = node
        self._update_size(node)
        self._update_size(right_child)
        return right_child
    
    def _rotate_right(self, node):
        """右旋操作（维护平衡）"""
        left_child = node.left
        node.left = left_child.right
        left_child.right = node
        self._update_size(node)
        self._update_size(left_child)
        return left_child
    
    def insert(self, order_id, order_data):
        """插入快递单"""
        self.root = self._insert_recursive(self.root, order_id, order_data)
    
    def _insert_recursive(self, node, order_id, order_data):
        if not node:
            return ExpressOrderTreapNode(order_id, order_data)
        
        # 按order_id进行二叉搜索树插入
        if order_id < node.order_id:
            node.left = self._insert_recursive(node.left, order_id, order_data)
            # 维护堆性质：如果左子树优先级更高则右旋
            if node.left.priority > node.priority:
                node = self._rotate_right(node)
        else:
            node.right = self._insert_recursive(node.right, order_id, order_data)
            # 维护堆性质：如果右子树优先级更高则左旋
            if node.right.priority > node.priority:
                node = self._rotate_left(node)
        
        self._update_size(node)
        return node
    
    def search(self, order_id):
        """查询快递单"""
        return self._search_recursive(self.root, order_id)
    
    def _search_recursive(self, node, order_id):
        if not node:
            return None  # 未找到
        if order_id == node.order_id:
            return node.order_data  # 返回完整快递单信息
        elif order_id < node.order_id:
            return self._search_recursive(node.left, order_id)
        else:
            return self._search_recursive(node.right, order_id)
    
    def delete(self, order_id):
        """删除快递单"""
        self.root = self._delete_recursive(self.root, order_id)
    
    def _delete_recursive(self, node, order_id):
        if not node:
            return None  # 未找到要删除的节点
        
        if order_id < node.order_id:
            node.left = self._delete_recursive(node.left, order_id)
        elif order_id > node.order_id:
            node.right = self._delete_recursive(node.right, order_id)
        else:
            # 找到目标节点，开始删除
            if not node.left:  # 左子树为空，直接返回右子树
                return node.right
            elif not node.right:  # 右子树为空，直接返回左子树
                return node.left
            else:
                # 左右子树都存在，选择优先级高的子树旋转
                if node.left.priority > node.right.priority:
                    node = self._rotate_right(node)
                    node.right = self._delete_recursive(node.right, order_id)
                else:
                    node = self._rotate_left(node)
                    node.left = self._delete_recursive(node.left, order_id)
        
        self._update_size(node)
        return node
    
    def range_query(self, start_id, end_id):
        """查询order_id在[start_id, end_id]范围内的快递单"""
        result = []
        self._range_query_recursive(self.root, start_id, end_id, result)
        return result
    
    def _range_query_recursive(self, node, start_id, end_id, result):
        if not node:
            return
        if start_id <= node.order_id <= end_id:
            result.append(node.order_data)  # 包含当前节点
        if start_id < node.order_id:
            self._range_query_recursive(node.left, start_id, end_id, result)
        if end_id > node.order_id:
            self._range_query_recursive(node.right, start_id, end_id, result)


# 使用示例
if __name__ == "__main__":
    treap = ExpressOrderTreap()
    
    # 1. 查询快递单
    print("查询1001:", treap.search("1001"))
    
    # 2. 插入新快递单
    new_order = {"orderId": "1004", "senderId": "u004", "orderStatus": "0"}
    treap.insert("1004", new_order)
    print("插入后查询1004:", treap.search("1004"))
    
    # 3. 范围查询
    print("查询1002-1004:", treap.range_query("1002", "1004"))
    
    # 4. 删除快递单
    treap.delete("1003")
    print("删除1003后查询:", treap.search("1003"))