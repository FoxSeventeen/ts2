# phone_search_example.py
# 手机号前缀查询功能示例

from trie_index import PhoneTrieIndex
from db_core import read_csv, DATA_DIR

def search_orders_by_phone_prefix(phone_prefix):
    """
    根据手机号前缀查询相关快递单
    
    参数:
        phone_prefix: 手机号前缀（如 "138", "13800138001"）
    
    返回:
        匹配的快递单详情列表
    """
    # 1. 加载或构建Trie索引
    trie_index = PhoneTrieIndex()
    if not trie_index.load():
        print("索引不存在，正在构建...")
        trie_index.build()
    
    # 2. 查询前缀对应的快递单ID
    order_ids = trie_index.search_prefix(phone_prefix)
    
    if not order_ids:
        print(f"未找到手机号前缀为 '{phone_prefix}' 的快递单")
        return []
    
    print(f"找到 {len(order_ids)} 个相关快递单: {', '.join(order_ids)}")
    
    # 3. 读取快递单详情
    orders = read_csv(f"{DATA_DIR}/ExpressOrder.csv")
    users = read_csv(f"{DATA_DIR}/User.csv")
    
    # 4. 构建结果集（包含寄件人和收件人信息）
    results = []
    for order in orders:
        if order['orderId'] in order_ids:
            # 查找寄件人和收件人信息
            sender = next((u for u in users if u['uid'] == order['senderId']), None)
            receiver = next((u for u in users if u['uid'] == order['receiverId']), None)
            
            results.append({
                '快递单号': order['orderId'],
                '寄件人': sender['uname'] if sender else '未知',
                '寄件人电话': sender['uphone'] if sender else '未知',
                '收件人': receiver['uname'] if receiver else '未知',
                '收件人电话': receiver['uphone'] if receiver else '未知',
                '物品名称': order['goodsName'],
                '物品重量': order['goodsWeight'],
                '寄件时间': order['sendTime'],
                '快递状态': order['orderStatus']
            })
    
    return results


def print_search_results(results):
    """格式化打印查询结果"""
    if not results:
        print("无查询结果")
        return
    
    print(f"\n{'='*80}")
    print(f"查询结果（共 {len(results)} 条）")
    print(f"{'='*80}\n")
    
    for idx, order in enumerate(results, 1):
        print(f"【快递 {idx}】")
        print(f"  快递单号: {order['快递单号']}")
        print(f"  寄件人: {order['寄件人']} ({order['寄件人电话']})")
        print(f"  收件人: {order['收件人']} ({order['收件人电话']})")
        print(f"  物品: {order['物品名称']} ({order['物品重量']}kg)")
        print(f"  寄件时间: {order['寄件时间']}")
        print(f"  状态: {order['快递状态']}")
        print()


# ==================== 使用示例 ====================
if __name__ == "__main__":
    print("手机号前缀查询示例\n")
    
    # 示例1: 查询手机号前缀为 "138" 的快递
    print("【示例1】查询手机号前缀为 '138' 的快递")
    results = search_orders_by_phone_prefix("138")
    print_search_results(results)
    
    # 示例2: 查询完整手机号
    print("\n【示例2】查询手机号为 '13800138001' 的快递")
    results = search_orders_by_phone_prefix("13800138001")
    print_search_results(results)
    
    # 示例3: 查询不存在的前缀
    print("\n【示例3】查询不存在的前缀 '999'")
    results = search_orders_by_phone_prefix("999")
    print_search_results(results)
    
    # 示例4: 重建索引（数据更新后调用）
    print("\n【示例4】重建索引")
    trie_index = PhoneTrieIndex()
    trie_index.rebuild()
    print("索引重建完成")
