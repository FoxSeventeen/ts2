#!/usr/bin/env python3
"""
测试数据验证脚本
检查数据完整性、格式正确性和关联关系
"""
import csv
import os


def check_file_exists(file_path):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {file_path} 存在")
        return True
    else:
        print(f"❌ {file_path} 不存在")
        return False


def count_records(file_path):
    """统计记录数量"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = len(list(reader))
        print(f"   └─ 记录数: {count}")
        return count
    except Exception as e:
        print(f"   └─ 读取失败: {e}")
        return 0


def validate_coordinates(file_path):
    """验证坐标格式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            records = list(reader)
        
        invalid_count = 0
        for record in records:
            coord = record.get('coordinateRange', '')
            parts = coord.split(',')
            if len(parts) != 4:
                print(f"   ⚠️  {record.get('branchId', 'Unknown')}: 坐标格式错误")
                invalid_count += 1
            else:
                try:
                    coords = [float(p) for p in parts]
                    # 检查经纬度范围（中国范围：73-135E, 18-54N）
                    if not (73 <= coords[0] <= 135 and 18 <= coords[1] <= 54):
                        print(f"   ⚠️  {record.get('branchId', 'Unknown')}: 坐标超出中国范围")
                        invalid_count += 1
                except ValueError:
                    print(f"   ⚠️  {record.get('branchId', 'Unknown')}: 坐标不是数字")
                    invalid_count += 1
        
        if invalid_count == 0:
            print(f"   ✅ 所有坐标格式正确")
        else:
            print(f"   ❌ 发现 {invalid_count} 个无效坐标")
        
        return invalid_count == 0
    except Exception as e:
        print(f"   ❌ 坐标验证失败: {e}")
        return False


def validate_foreign_keys():
    """验证外键关联"""
    data_dir = "database/data"
    
    print("\n🔗 外键关联验证")
    print("=" * 50)
    
    # 读取基础表
    try:
        with open(f"{data_dir}/User.csv", 'r', encoding='utf-8') as f:
            users = list(csv.DictReader(f))
        with open(f"{data_dir}/ExpressBranch.csv", 'r', encoding='utf-8') as f:
            branches = list(csv.DictReader(f))
        with open(f"{data_dir}/ExpressOrder.csv", 'r', encoding='utf-8') as f:
            orders = list(csv.DictReader(f))
        with open(f"{data_dir}/ExpressTrack.csv", 'r', encoding='utf-8') as f:
            tracks = list(csv.DictReader(f))
    except Exception as e:
        print(f"❌ 读取数据失败: {e}")
        return False
    
    # 构建ID集合
    user_ids = {u['uid'] for u in users}
    branch_ids = {b['branchId'] for b in branches}
    order_ids = {o['orderId'] for o in orders}
    
    errors = 0
    
    # 验证快递单中的用户ID
    print("\n1. 验证快递单中的用户ID...")
    for order in orders:
        if order['senderId'] not in user_ids:
            print(f"   ❌ {order['orderId']}: 寄件人ID {order['senderId']} 不存在")
            errors += 1
        if order['receiverId'] not in user_ids:
            print(f"   ❌ {order['orderId']}: 收件人ID {order['receiverId']} 不存在")
            errors += 1
    if errors == 0:
        print("   ✅ 所有用户ID关联正确")
    
    # 验证快递单中的网点ID
    print("\n2. 验证快递单中的网点ID...")
    branch_errors = 0
    for order in orders:
        if order['sendBranchId'] not in branch_ids:
            print(f"   ❌ {order['orderId']}: 寄件网点ID {order['sendBranchId']} 不存在")
            branch_errors += 1
            errors += 1
        if order['targetBranchId'] not in branch_ids:
            print(f"   ❌ {order['orderId']}: 目标网点ID {order['targetBranchId']} 不存在")
            branch_errors += 1
            errors += 1
    if branch_errors == 0:
        print("   ✅ 所有网点ID关联正确")
    
    # 验证轨迹中的快递单号
    print("\n3. 验证轨迹中的快递单号...")
    track_errors = 0
    for track in tracks:
        if track['orderId'] not in order_ids:
            print(f"   ❌ 轨迹记录: 快递单号 {track['orderId']} 不存在")
            track_errors += 1
            errors += 1
    if track_errors == 0:
        print("   ✅ 所有轨迹的快递单号关联正确")
    
    # 验证轨迹中的网点ID
    print("\n4. 验证轨迹中的网点ID...")
    branch_track_errors = 0
    for track in tracks:
        if track['operateBranchId'] not in branch_ids:
            print(f"   ❌ {track['orderId']}: 操作网点ID {track['operateBranchId']} 不存在")
            branch_track_errors += 1
            errors += 1
    if branch_track_errors == 0:
        print("   ✅ 所有轨迹的网点ID关联正确")
    
    print(f"\n{'✅' if errors == 0 else '❌'} 外键验证完成，发现 {errors} 个错误")
    return errors == 0


def validate_order_status():
    """验证快递单状态合理性"""
    print("\n📊 快递单状态验证")
    print("=" * 50)
    
    try:
        with open("database/data/ExpressOrder.csv", 'r', encoding='utf-8') as f:
            orders = list(csv.DictReader(f))
        
        status_map = {'0': '待收件', '1': '已收件', '2': '中转中', '3': '派送中', '4': '已签收', '5': '异常'}
        status_count = {}
        
        for order in orders:
            status = order['orderStatus']
            if status not in status_map:
                print(f"   ❌ {order['orderId']}: 状态码 {status} 无效")
            else:
                status_count[status] = status_count.get(status, 0) + 1
        
        print("\n状态分布：")
        for status, name in status_map.items():
            count = status_count.get(status, 0)
            print(f"   {status} ({name}): {count} 条")
        
        print("\n✅ 状态验证完成")
        return True
    except Exception as e:
        print(f"❌ 状态验证失败: {e}")
        return False


def validate_track_continuity():
    """验证轨迹连续性"""
    print("\n🛤️  轨迹连续性验证（抽检EXP001）")
    print("=" * 50)
    
    try:
        with open("database/data/ExpressTrack.csv", 'r', encoding='utf-8') as f:
            tracks = list(csv.DictReader(f))
        
        # 筛选EXP001的轨迹
        exp001_tracks = [t for t in tracks if t['orderId'] == 'EXP001']
        exp001_tracks.sort(key=lambda x: x['operateTime'])
        
        print(f"\n找到 {len(exp001_tracks)} 条轨迹记录：")
        
        for i, track in enumerate(exp001_tracks, 1):
            print(f"{i}. {track['operateTime']} | {track['operateBranchId']} | "
                  f"类型{track['operateType']} | prev={track['prevBranchId']} | next={track['nextBranchId']}")
        
        # 检查时间连续性
        errors = 0
        for i in range(1, len(exp001_tracks)):
            prev_time = exp001_tracks[i-1]['operateTime']
            curr_time = exp001_tracks[i]['operateTime']
            if prev_time >= curr_time:
                print(f"   ❌ 时间倒序: {prev_time} -> {curr_time}")
                errors += 1
        
        if errors == 0:
            print("\n✅ 轨迹时间连续性正确")
        else:
            print(f"\n❌ 发现 {errors} 个时间错误")
        
        return errors == 0
    except Exception as e:
        print(f"❌ 轨迹验证失败: {e}")
        return False


def main():
    """主验证流程"""
    print("=" * 60)
    print("快递管理系统 - 测试数据验证")
    print("=" * 60)
    
    # 1. 文件存在性检查
    print("\n📁 文件存在性检查")
    print("=" * 50)
    
    files = [
        "database/data/User.csv",
        "database/data/ExpressBranch.csv",
        "database/data/Courier.csv",
        "database/data/ExpressOrder.csv",
        "database/data/ExpressTrack.csv",
        "database/data/DeliveryZone.csv",
        "database/views.meta"
    ]
    
    all_exist = True
    for file in files:
        exists = check_file_exists(file)
        if exists:
            count_records(file)
        all_exist = all_exist and exists
    
    if not all_exist:
        print("\n❌ 部分文件缺失，请检查数据目录")
        return
    
    # 2. 坐标格式验证
    print("\n📍 坐标格式验证")
    print("=" * 50)
    validate_coordinates("database/data/ExpressBranch.csv")
    
    # 3. 外键关联验证
    validate_foreign_keys()
    
    # 4. 快递单状态验证
    validate_order_status()
    
    # 5. 轨迹连续性验证
    validate_track_continuity()
    
    # 总结
    print("\n" + "=" * 60)
    print("✅ 数据验证完成！")
    print("=" * 60)
    print("\n建议:")
    print("1. 运行可视化测试: python test_visualization.py")
    print("2. 查询EXP001轨迹验证可视化效果")
    print("3. 启动GUI系统: python main.py")


if __name__ == "__main__":
    main()
