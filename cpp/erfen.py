class UIDManager:
    def __init__(self, entity_type="user"):
        """初始化UID管理器（支持user/courier两种实体类型）"""
        self.entity_type = entity_type
        self.uid_list = []  # 存储有序的UID列表

    def _bubble_sort(self):
        """冒泡排序维护UID列表的有序性"""
        n = len(self.uid_list)
        for i in range(n):
            # 标记本轮是否发生交换，优化已排序情况
            swapped = False
            for j in range(0, n-i-1):
                if self.uid_list[j] > self.uid_list[j+1]:
                    # 交换位置
                    self.uid_list[j], self.uid_list[j+1] = self.uid_list[j+1], self.uid_list[j]
                    swapped = True
            if not swapped:
                break  # 无交换说明已排序完成，提前退出

    def _binary_search(self, target_uid):
        """二分查找目标UID，返回索引（-1表示不存在）"""
        left, right = 0, len(self.uid_list) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.uid_list[mid] == target_uid:
                return mid  # 找到目标，返回索引
            elif self.uid_list[mid] < target_uid:
                left = mid + 1
            else:
                right = mid - 1
        return -1  # 未找到

    def add_uid(self, uid):
        """添加UID并重新排序"""
        # 先检查是否已存在（利用二分查找优化）
        if self._binary_search(uid) != -1:
            print(f"错误：{self.entity_type}的UID {uid} 已存在")
            return False
        self.uid_list.append(uid)
        self._bubble_sort()  # 新增后保持有序
        return True

    def remove_uid(self, uid):
        """删除UID并保持有序"""
        index = self._binary_search(uid)
        if index == -1:
            print(f"错误：未找到{self.entity_type}的UID {uid}")
            return False
        del self.uid_list[index]
        # 删除后列表仍有序，无需重新排序
        return True

    def get_uid_list(self):
        """获取当前有序的UID列表"""
        return self.uid_list.copy()

    def exists(self, uid):
        """检查UID是否存在（基于二分查找）"""
        return self._binary_search(uid) != -1


# 使用示例
if __name__ == "__main__":
    # 初始化用户UID管理器
    user_manager = UIDManager(entity_type="user")
    
    # 添加用户UID
    user_manager.add_uid("U1003")
    user_manager.add_uid("U1001")
    user_manager.add_uid("U1002")
    print("用户UID列表（有序）：", user_manager.get_uid_list())  # ['U1001', 'U1002', 'U1003']
    
    # 检查UID是否存在
    print("U1002是否存在？", user_manager.exists("U1002"))  # True
    
    # 删除UID
    user_manager.remove_uid("U1002")
    print("删除后用户UID列表：", user_manager.get_uid_list())  # ['U1001', 'U1003']
    
    # 初始化快递员UID管理器
    courier_manager = UIDManager(entity_type="courier")
    courier_manager.add_uid("C002")
    courier_manager.add_uid("C001")
    print("快递员UID列表（有序）：", courier_manager.get_uid_list())  # ['C001', 'C002']