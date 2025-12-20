#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_all_fixes.py
# 测试所有修复功能的完整脚本

print("="*70)
print("快递管理系统 - 功能测试脚本")
print("="*70)

# 测试1：快递员派送统计
print("\n【测试1】快递员派送统计功能")
print("-"*70)
try:
    from db_core import join_courier_orders
    
    # 测试快递员C001在2024-12-13的派送记录
    results = join_courier_orders('C001', '2024-12-13')
    
    if results:
        print(f"✅ 成功！快递员C001在2024-12-13共派送 {len(results)} 个快递")
        print("\n详细信息：")
        for i, record in enumerate(results[:3], 1):  # 只显示前3条
            print(f"  [{i}] 快递单号: {record['快递单号']}")
            print(f"      收件人: {record['收件人姓名']} ({record['收件人电话']})")
            print(f"      物品: {record['物品名称']}")
            print(f"      状态: {record['状态']}")
            print()
        if len(results) > 3:
            print(f"  ... 还有 {len(results)-3} 条记录")
    else:
        print("⚠️  未找到派送记录（可能该快递员当天无派送任务）")
        print("   提示：可以尝试其他日期，如 '2024-12-10' 或 '2024-12-11'")
    
except Exception as e:
    print(f"❌ 失败：{e}")
    print("   请检查 db_core.py 是否已更新到最新版本")

# 测试2：网点寄件量统计
print("\n【测试2】网点寄件量统计功能")
print("-"*70)
try:
    from db_core import query_view
    
    # 测试网点月度寄件量统计
    results = query_view("BranchMonthlySend")
    
    if results:
        print(f"✅ 成功！共找到 {len(results)} 条网点统计记录")
        print("\n详细信息：")
        for i, stat in enumerate(results[:5], 1):  # 只显示前5条
            print(f"  [{i}] 网点: {stat['sendBranchId']}, "
                  f"月份: {stat['month']}, "
                  f"寄件量: {stat['sendCount']}件")
        if len(results) > 5:
            print(f"  ... 还有 {len(results)-5} 条记录")
    else:
        print("⚠️  未找到统计记录")
        print("   提示：检查 database/data/ExpressOrder.csv 是否有数据")
    
    # 测试快递状态分布统计
    print("\n  额外测试：快递状态分布统计")
    status_results = query_view("OrderStatusStats")
    if status_results:
        print("  ✅ 成功！快递状态分布：")
        for stat in status_results:
            print(f"      {stat['statusName']}: {stat['count']}件")
    
except Exception as e:
    print(f"❌ 失败：{e}")
    print("   请检查：")
    print("   1. db_core.py 是否已添加 'import os'")
    print("   2. query_view 函数是否已完整更新")

# 测试3：手机号前缀查询
print("\n【测试3】手机号前缀查询功能（Trie索引）")
print("-"*70)
try:
    from trie_index import PhoneTrieIndex
    from db_core import read_csv, DATA_DIR
    
    # 初始化Trie索引
    trie_index = PhoneTrieIndex()
    
    # 尝试加载索引，如果不存在则构建
    if not trie_index.load():
        print("  索引文件不存在，正在构建Trie索引...")
        trie_index.build()
        print("  ✅ Trie索引构建完成！")
    else:
        print("  ✅ Trie索引加载成功！")
    
    # 测试前缀查询
    test_prefixes = ["138", "13800138001", "139"]
    
    for prefix in test_prefixes:
        order_ids = trie_index.search_prefix(prefix)
        
        if order_ids:
            print(f"\n  查询前缀 '{prefix}': 找到 {len(order_ids)} 个快递单")
            print(f"      快递单号: {', '.join(sorted(list(order_ids))[:5])}")
            if len(order_ids) > 5:
                print(f"      ... 还有 {len(order_ids)-5} 个快递单")
            
            # 显示第一个快递的详细信息
            orders = read_csv(f"{DATA_DIR}/ExpressOrder.csv")
            users = read_csv(f"{DATA_DIR}/User.csv")
            
            first_order_id = sorted(list(order_ids))[0]
            order = next((o for o in orders if o['orderId'] == first_order_id), None)
            
            if order:
                sender = next((u for u in users if u['uid'] == order['senderId']), None)
                receiver = next((u for u in users if u['uid'] == order['receiverId']), None)
                
                print(f"\n      【示例快递详情】{first_order_id}")
                if sender:
                    print(f"      寄件人: {sender['uname']} ({sender['uphone']})")
                if receiver:
                    print(f"      收件人: {receiver['uname']} ({receiver['uphone']})")
                print(f"      物品: {order['goodsName']} ({order['goodsWeight']}kg)")
        else:
            print(f"\n  查询前缀 '{prefix}': 未找到匹配的快递单")
    
    print("\n  ✅ 手机号前缀查询功能正常！")
    
except ImportError as e:
    print(f"❌ 导入失败：{e}")
    print("   请检查：")
    print("   1. trie_index.py 文件是否存在于项目根目录")
    print("   2. 文件名和类名是否正确")
except Exception as e:
    print(f"❌ 失败：{e}")
    print("   请检查：")
    print("   1. database/data/ 目录下是否有 User.csv 和 ExpressOrder.csv")
    print("   2. CSV文件格式是否正确")

# 总结
print("\n" + "="*70)
print("测试完成总结")
print("="*70)
print("""
✅ 如果以上三个测试都通过，说明所有功能已修复成功！

📋 下一步操作：
1. 运行主程序: python main.py 或 python GUI.py
2. 在图形界面中测试各项功能
3. 使用示例脚本: python phone_search_example.py

📚 详细文档：
- README.md - 完整的项目文档和使用指南
- 快速修复指南.md - 详细的修复说明
- 修复说明.md - 技术细节和问题分析

⚠️ 如果测试失败，请按照错误提示检查相应的文件和配置。
""")
