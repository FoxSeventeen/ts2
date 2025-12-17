#!/usr/bin/env python3
"""
功能演示脚本
展示系统各项核心功能的使用方法
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("快递管理系统 - 功能演示")
print("=" * 60)

# ==================== 1. 用户查询演示 ====================
print("\n【演示1】用户查询")
print("-" * 50)

try:
    from db_core import query_user
    
    # 按手机号查询
    print("查询手机号: 13800138001")
    users = query_user({"uphone": "13800138001"})
    if users:
        user = users[0]
        print(f"✅ 找到用户: {user['uname']}, {user['ucity']}, {user['uaddress']}")
    else:
        print("❌ 未找到用户")
    
    # 按城市查询
    print("\n查询城市: 北京市")
    beijing_users = query_user({"ucity": "北京市"})
    print(f"✅ 找到 {len(beijing_users)} 个北京用户")
    for u in beijing_users[:3]:  # 只显示前3个
        print(f"   - {u['uname']} ({u['utype']})")

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保db_core.py在当前目录")

# ==================== 2. 快递单查询演示 ====================
print("\n【演示2】快递单查询")
print("-" * 50)

try:
    from db_core import query_express_order
    
    # 按单号查询
    print("查询快递单号: EXP001")
    orders = query_express_order({"orderId": "EXP001"})
    if orders:
        order = orders[0]
        print(f"✅ 找到快递: {order['goodsName']}, "
              f"状态={order['orderStatus']}, "
              f"寄件时间={order['sendTime']}")
    
    # 按状态查询
    print("\n查询派送中的快递（状态=3）")
    delivering = query_express_order({"orderStatus": "3"})
    print(f"✅ 找到 {len(delivering)} 个派送中的快递")
    for o in delivering:
        print(f"   - {o['orderId']}: {o['goodsName']}")
    
    # 查询异常件
    print("\n查询异常快递（状态=5）")
    abnormal = query_express_order({"orderStatus": "5"})
    print(f"✅ 找到 {len(abnormal)} 个异常快递")
    for o in abnormal:
        print(f"   - {o['orderId']}: {o['goodsName']} (寄件时间: {o['sendTime']})")

except ImportError as e:
    print(f"❌ 导入失败: {e}")

# ==================== 3. 快递轨迹查询演示 ====================
print("\n【演示3】快递轨迹查询")
print("-" * 50)

try:
    from spatial_core import express_spatial_track
    
    print("查询快递单号: EXP001 的轨迹")
    tracks = express_spatial_track("EXP001")
    
    if tracks:
        print(f"✅ 找到 {len(tracks)} 条轨迹记录\n")
        for i, track in enumerate(tracks, 1):
            print(f"{i}. {track['操作时间']} | {track['操作类型']} | {track['当前网点名称']}")
            if track['上个网点ID'] != 'NULL':
                print(f"   ← 来自: {track['上个网点名称']}")
            if track['下个网点ID'] != 'NULL':
                print(f"   → 去往: {track['下个网点名称']}")
    else:
        print("❌ 未找到轨迹")

except ImportError as e:
    print(f"❌ 导入失败: {e}")

# ==================== 4. 网点查询演示 ====================
print("\n【演示4】网点查询")
print("-" * 50)

try:
    from db_core import read_csv
    
    branches = read_csv("database/data/ExpressBranch.csv")
    
    # 统计网点类型
    types = {}
    for branch in branches:
        btype = branch['branchType']
        types[btype] = types.get(btype, 0) + 1
    
    print(f"✅ 共 {len(branches)} 个网点")
    for btype, count in types.items():
        print(f"   - {btype}: {count} 个")
    
    # 显示分拨中心
    print("\n分拨中心列表：")
    centers = [b for b in branches if b['branchType'] == '分拨中心']
    for center in centers:
        print(f"   - {center['branchId']}: {center['branchName']} ({center['city']})")

except Exception as e:
    print(f"❌ 查询失败: {e}")

# ==================== 5. 多表连接查询演示 ====================
print("\n【演示5】多表连接查询")
print("-" * 50)

try:
    from db_core import read_csv
    
    # 查询EXP001的寄件人和收件人
    orders = read_csv("database/data/ExpressOrder.csv")
    users = read_csv("database/data/User.csv")
    
    order = [o for o in orders if o['orderId'] == 'EXP001'][0]
    sender = [u for u in users if u['uid'] == order['senderId']][0]
    receiver = [u for u in users if u['uid'] == order['receiverId']][0]
    
    print(f"快递单号: {order['orderId']}")
    print(f"物品名称: {order['goodsName']}")
    print(f"寄件人: {sender['uname']} ({sender['uphone']})")
    print(f"       {sender['ucity']} {sender['uaddress']}")
    print(f"收件人: {receiver['uname']} ({receiver['uphone']})")
    print(f"       {receiver['ucity']} {receiver['uaddress']}")

except Exception as e:
    print(f"❌ 查询失败: {e}")

# ==================== 6. 统计分析演示 ====================
print("\n【演示6】统计分析")
print("-" * 50)

try:
    from db_core import read_csv
    
    orders = read_csv("database/data/ExpressOrder.csv")
    
    # 按状态统计
    status_map = {'0': '待收件', '1': '已收件', '2': '中转中', 
                  '3': '派送中', '4': '已签收', '5': '异常'}
    status_count = {}
    for order in orders:
        status = order['orderStatus']
        status_count[status] = status_count.get(status, 0) + 1
    
    print("快递状态分布：")
    for status, name in status_map.items():
        count = status_count.get(status, 0)
        percentage = (count / len(orders) * 100) if orders else 0
        bar = "█" * int(percentage / 5)
        print(f"   {name:8s} ({status}): {count:2d} 条 {bar} {percentage:.1f}%")
    
    # 寄件城市统计
    print("\n寄件城市TOP5：")
    branches = read_csv("database/data/ExpressBranch.csv")
    city_count = {}
    for order in orders:
        branch = [b for b in branches if b['branchId'] == order['sendBranchId']][0]
        city = branch['city']
        city_count[city] = city_count.get(city, 0) + 1
    
    sorted_cities = sorted(city_count.items(), key=lambda x: x[1], reverse=True)
    for i, (city, count) in enumerate(sorted_cities[:5], 1):
        print(f"   {i}. {city}: {count} 条")

except Exception as e:
    print(f"❌ 统计失败: {e}")

# ==================== 7. 索引性能演示 ====================
print("\n【演示7】索引查询演示")
print("-" * 50)

try:
    from index_core import HashIndex
    import time
    
    # 构建用户手机号索引
    print("构建用户手机号索引...")
    start = time.time()
    user_index = HashIndex("User", "uphone")
    user_index.build()
    build_time = time.time() - start
    print(f"✅ 索引构建完成，耗时: {build_time:.4f}秒")
    
    # 使用索引查询
    print("\n使用索引查询手机号: 13800138003")
    start = time.time()
    rows = user_index.search("13800138003")
    search_time = time.time() - start
    print(f"✅ 查询完成，找到 {len(rows)} 条记录，耗时: {search_time:.4f}秒")

except ImportError as e:
    print(f"❌ 导入失败: {e}")

# ==================== 总结 ====================
print("\n" + "=" * 60)
print("✅ 功能演示完成！")
print("=" * 60)
print("\n下一步:")
print("1. 运行可视化测试: python test_visualization.py")
print("2. 验证数据完整性: python validate_data.py")
print("3. 启动GUI系统: python main.py")
print("\n推荐可视化测试快递单号: EXP001, EXP011, EXP002")
