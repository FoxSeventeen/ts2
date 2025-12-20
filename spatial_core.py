# spatial_core.py
"""
快递管理系统 - 空间数据处理核心模块（重写版）
提供快递轨迹查询、配送区域查询、坐标计算等空间数据功能

主要功能：
1. 快递轨迹查询与可视化数据生成
2. 配送区域空间范围查询
3. 坐标解析与计算
4. 轨迹记录生成与维护

作者：重写优化版
版本：v2.0
日期：2024-12-14
"""

import os
import datetime
from typing import List, Dict, Tuple, Optional
from db_core import DATA_DIR, write_csv, read_csv


# ==================== 坐标处理工具函数 ====================

def parse_coordinate(coord_str: str) -> Optional[Tuple[float, float]]:
    """
    解析坐标字符串，返回经纬度元组
    
    支持两种格式：
    1. 点坐标：lng,lat（如：116.45,39.93）
    2. 矩形范围：minLng,minLat,maxLng,maxLat（如：116.43,39.91,116.47,39.95）
    
    Args:
        coord_str: 坐标字符串
        
    Returns:
        (经度, 纬度) 元组，解析失败返回None
        
    Examples:
        >>> parse_coordinate("116.45,39.93")
        (116.45, 39.93)
        >>> parse_coordinate("116.43,39.91,116.47,39.95")
        (116.45, 39.93)  # 返回中心点
    """
    # 空值检查
    if not coord_str or coord_str.strip() in ('', 'NULL', '未知坐标'):
        return None
    
    try:
        # 分割坐标字符串
        parts = coord_str.strip().split(',')
        
        if len(parts) == 2:
            # 点坐标格式：lng,lat
            lng, lat = float(parts[0]), float(parts[1])
        elif len(parts) == 4:
            # 矩形范围格式：minLng,minLat,maxLng,maxLat
            # 返回中心点坐标
            min_lng, min_lat, max_lng, max_lat = map(float, parts)
            lng = (min_lng + max_lng) / 2
            lat = (min_lat + max_lat) / 2
        else:
            print(f"⚠️  坐标格式错误：{coord_str}（应为2或4个数字）")
            return None
        
        # 坐标范围验证（中国境内：73-135°E, 18-54°N）
        if not (73 <= lng <= 135):
            print(f"⚠️  经度超出范围：{lng}（应在73-135°E）")
            return None
        if not (18 <= lat <= 54):
            print(f"⚠️  纬度超出范围：{lat}（应在18-54°N）")
            return None
        
        return (lng, lat)
    
    except (ValueError, TypeError) as e:
        print(f"⚠️  坐标解析失败：{coord_str}，错误：{e}")
        return None


def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    计算两点间的直线距离（简化版，单位：千米）
    使用简单的欧几里得距离公式（适用于短距离）
    
    Args:
        coord1: 第一个坐标 (经度, 纬度)
        coord2: 第二个坐标 (经度, 纬度)
        
    Returns:
        距离（千米）
        
    Note:
        这是简化算法，精确计算应使用Haversine公式
    """
    lng1, lat1 = coord1
    lng2, lat2 = coord2
    
    # 1度经度/纬度约等于111千米（简化计算）
    km_per_degree = 111.0
    
    # 计算经纬度差异
    delta_lng = (lng2 - lng1) * km_per_degree
    delta_lat = (lat2 - lat1) * km_per_degree
    
    # 欧几里得距离
    distance = (delta_lng ** 2 + delta_lat ** 2) ** 0.5
    
    return round(distance, 2)


def is_coordinate_in_range(coord: Tuple[float, float], 
                          min_lng: float, min_lat: float,
                          max_lng: float, max_lat: float) -> bool:
    """
    判断坐标是否在指定矩形范围内
    
    Args:
        coord: 待检测坐标 (经度, 纬度)
        min_lng, min_lat, max_lng, max_lat: 矩形范围
        
    Returns:
        True表示在范围内，False表示不在
    """
    lng, lat = coord
    return (min_lng <= lng <= max_lng) and (min_lat <= lat <= max_lat)


# ==================== 快递轨迹查询 ====================

def express_spatial_track(order_id: str) -> List[Dict[str, str]]:
    """
    查询快递的空间轨迹（完整版，包含站点信息和坐标）
    
    返回格式化的轨迹数据，包含：
    - 操作时间、操作类型
    - 当前站点ID、名称、坐标
    - 上一站点ID、名称
    - 下一站点ID、名称
    
    Args:
        order_id: 快递单号
        
    Returns:
        轨迹数据列表，按时间排序
        
    Example:
        >>> tracks = express_spatial_track("EXP001")
        >>> print(f"共{len(tracks)}条轨迹")
        >>> for track in tracks:
        ...     print(f"{track['操作时间']} | {track['当前网点名称']}")
    """
    print(f"🔍 查询快递单号：{order_id} 的轨迹...")
    
    # 1. 读取数据文件
    track_path = os.path.join(DATA_DIR, "ExpressTrack.csv")
    branch_path = os.path.join(DATA_DIR, "ExpressBranch.csv")
    
    try:
        tracks = read_csv(track_path)
        branches = read_csv(branch_path)
    except FileNotFoundError as e:
        print(f"❌ 数据文件不存在：{e}")
        return []
    except Exception as e:
        print(f"❌ 读取数据失败：{e}")
        return []
    
    # 2. 筛选目标快递的轨迹
    target_tracks = [t for t in tracks if t.get('orderId') == order_id]
    
    if not target_tracks:
        print(f"⚠️  未找到快递单号 {order_id} 的轨迹数据")
        return []
    
    # 3. 按操作时间排序
    def safe_sort_key(track_record):
        """安全的排序键函数，处理空时间"""
        return track_record.get('operateTime', '1970-01-01 00:00:00')
    
    target_tracks.sort(key=safe_sort_key)
    
    # 4. 构建网点信息映射表
    branch_info = {}
    for branch in branches:
        branch_id = branch.get('branchId')
        if branch_id:
            branch_info[branch_id] = {
                'name': branch.get('branchName', '未知网点'),
                'coordinate': branch.get('coordinateRange', '未知坐标'),
                'city': branch.get('city', '未知城市'),
                'address': branch.get('address', '未知地址')
            }
    
    # 5. 操作类型映射表
    operate_type_map = {
        '0': '收件',
        '1': '中转入库', 
        '2': '中转出库',
        '3': '派送',
        '4': '签收'
    }
    
    # 6. 格式化轨迹数据
    spatial_tracks = []
    
    for idx, track in enumerate(target_tracks, 1):
        # 获取网点ID（处理空值）
        current_branch_id = track.get('operateBranchId', 'UNKNOWN')
        prev_branch_id = track.get('prevBranchId')
        next_branch_id = track.get('nextBranchId')
        
        # 处理NULL标记
        if prev_branch_id in (None, '', 'NULL'):
            prev_branch_id = 'NULL'
        if next_branch_id in (None, '', 'NULL'):
            next_branch_id = 'NULL'
        
        # 获取网点信息（带默认值）
        current_info = branch_info.get(current_branch_id, {
            'name': f'未知网点({current_branch_id})',
            'coordinate': '未知坐标',
            'city': '未知城市',
            'address': '未知地址'
        })
        
        prev_info = branch_info.get(prev_branch_id, {
            'name': 'NULL',
            'coordinate': 'NULL'
        }) if prev_branch_id != 'NULL' else {'name': 'NULL', 'coordinate': 'NULL'}
        
        next_info = branch_info.get(next_branch_id, {
            'name': 'NULL',
            'coordinate': 'NULL'
        }) if next_branch_id != 'NULL' else {'name': 'NULL', 'coordinate': 'NULL'}
        
        # 获取操作类型
        operate_type = track.get('operateType', '未知')
        operate_type_name = operate_type_map.get(operate_type, f'未知类型({operate_type})')
        
        # 构建轨迹记录
        spatial_track = {
            '序号': str(idx),
            '操作时间': track.get('operateTime', '未知时间'),
            '操作类型': operate_type_name,
            '当前网点ID': current_branch_id,
            '当前网点名称': current_info['name'],
            '当前网点坐标': current_info['coordinate'],
            '当前网点城市': current_info['city'],
            '当前网点地址': current_info['address'],
            '上个网点ID': prev_branch_id,
            '上个网点名称': prev_info['name'],
            '下个网点ID': next_branch_id,
            '下个网点名称': next_info['name']
        }
        
        spatial_tracks.append(spatial_track)
    
    print(f"✅ 查询成功，共 {len(spatial_tracks)} 条轨迹记录")
    return spatial_tracks


def get_track_summary(order_id: str) -> Optional[Dict[str, any]]:
    """
    获取快递轨迹摘要信息
    
    Args:
        order_id: 快递单号
        
    Returns:
        轨迹摘要字典，包含起点、终点、站点数、总距离等
    """
    tracks = express_spatial_track(order_id)
    
    if not tracks:
        return None
    
    # 提取有效坐标的站点
    stations = []
    for track in tracks:
        coord = parse_coordinate(track.get('当前网点坐标', ''))
        if coord:
            stations.append({
                'name': track['当前网点名称'],
                'city': track['当前网点城市'],
                'coord': coord,
                'time': track['操作时间']
            })
    
    if len(stations) < 2:
        return {
            'order_id': order_id,
            'total_stations': len(tracks),
            'valid_coords': len(stations),
            'start_station': tracks[0]['当前网点名称'],
            'end_station': tracks[-1]['当前网点名称'],
            'total_distance': 0,
            'start_time': tracks[0]['操作时间'],
            'end_time': tracks[-1]['操作时间']
        }
    
    # 计算总距离
    total_distance = 0
    for i in range(1, len(stations)):
        distance = calculate_distance(stations[i-1]['coord'], stations[i]['coord'])
        total_distance += distance
    
    return {
        'order_id': order_id,
        'total_stations': len(tracks),
        'valid_coords': len(stations),
        'start_station': stations[0]['name'],
        'start_city': stations[0]['city'],
        'end_station': stations[-1]['name'],
        'end_city': stations[-1]['city'],
        'total_distance': round(total_distance, 2),
        'start_time': stations[0]['time'],
        'end_time': stations[-1]['time']
    }


# ==================== 配送区域查询 ====================

def spatial_zone_query(branch_id: str, 
                      min_lng: float, min_lat: float, 
                      max_lng: float, max_lat: float) -> List[Dict]:
    """
    查询某网点下指定坐标范围内的配送区域（矩形相交判断）
    
    Args:
        branch_id: 网点ID
        min_lng, min_lat: 查询范围左下角坐标
        max_lng, max_lat: 查询范围右上角坐标
        
    Returns:
        匹配的配送区域列表
        
    Example:
        >>> # 查询北京朝阳网点在指定范围的配送区域
        >>> zones = spatial_zone_query("B001", 116.43, 39.88, 116.50, 40.02)
        >>> print(f"找到 {len(zones)} 个配送区域")
    """
    zone_file = os.path.join(DATA_DIR, "DeliveryZone.csv")
    
    try:
        zones = read_csv(zone_file)
    except FileNotFoundError:
        print(f"⚠️  配送区域文件不存在：{zone_file}")
        return []
    except Exception as e:
        print(f"❌ 读取配送区域失败：{e}")
        return []
    
    results = []
    
    for zone in zones:
        # 筛选指定网点的配送区域
        if zone.get('branchId') != branch_id:
            continue
        
        # 解析配送区域坐标范围
        coord_range = zone.get('coordinateRange', '')
        try:
            parts = coord_range.split(',')
            if len(parts) != 4:
                print(f"⚠️  配送区域 {zone.get('zoneId')} 坐标格式错误")
                continue
            
            z_min_lng, z_min_lat, z_max_lng, z_max_lat = map(float, parts)
        except (ValueError, AttributeError) as e:
            print(f"⚠️  配送区域 {zone.get('zoneId')} 坐标解析失败：{e}")
            continue
        
        # 判断两个矩形是否相交
        # 相交条件：NOT (矩形1在矩形2左侧 OR 矩形1在矩形2右侧 OR 矩形1在矩形2下方 OR 矩形1在矩形2上方)
        if not (z_max_lng < min_lng or  # 配送区域在查询范围左侧
                z_min_lng > max_lng or  # 配送区域在查询范围右侧
                z_max_lat < min_lat or  # 配送区域在查询范围下方
                z_min_lat > max_lat):   # 配送区域在查询范围上方
            results.append(zone)
    
    print(f"✅ 找到 {len(results)} 个匹配的配送区域")
    return results


def get_branch_coverage(branch_id: str) -> Optional[Dict]:
    """
    获取网点的配送覆盖范围统计
    
    Args:
        branch_id: 网点ID
        
    Returns:
        覆盖范围统计信息
    """
    zone_file = os.path.join(DATA_DIR, "DeliveryZone.csv")
    
    try:
        zones = read_csv(zone_file)
    except:
        return None
    
    branch_zones = [z for z in zones if z.get('branchId') == branch_id]
    
    if not branch_zones:
        return None
    
    # 统计覆盖范围
    total_area = 0
    all_coords = []
    
    for zone in branch_zones:
        coord_range = zone.get('coordinateRange', '')
        try:
            parts = list(map(float, coord_range.split(',')))
            if len(parts) == 4:
                min_lng, min_lat, max_lng, max_lat = parts
                # 简化面积计算（度数×度数）
                area = (max_lng - min_lng) * (max_lat - min_lat)
                total_area += area
                all_coords.extend([min_lng, min_lat, max_lng, max_lat])
        except:
            continue
    
    if all_coords:
        coverage_bounds = {
            'min_lng': min(all_coords[::2]),
            'max_lng': max(all_coords[::2]),
            'min_lat': min(all_coords[1::2]),
            'max_lat': max(all_coords[1::2])
        }
    else:
        coverage_bounds = None
    
    return {
        'branch_id': branch_id,
        'zone_count': len(branch_zones),
        'total_area': round(total_area, 4),
        'coverage_bounds': coverage_bounds,
        'zone_names': [z.get('zoneName', '未知') for z in branch_zones]
    }


# ==================== 轨迹生成与维护 ====================

def generate_express_track(order_id: str, 
                          current_branch_id: str, 
                          operate_type: str,
                          prev_branch_id: Optional[str] = None,
                          next_branch_id: Optional[str] = None) -> bool:
    """
    生成快递轨迹记录（自动维护站点关联关系）
    
    Args:
        order_id: 快递单号
        current_branch_id: 当前操作网点ID
        operate_type: 操作类型（0-4）
        prev_branch_id: 上个网点ID（可选）
        next_branch_id: 下个网点ID（可选）
        
    Returns:
        True表示成功，False表示失败
        
    Example:
        >>> # 记录快递在北京收件
        >>> generate_express_track("EXP001", "B001", "0")
        >>> # 记录快递从北京发往上海
        >>> generate_express_track("EXP001", "B001", "1", next_branch_id="B002")
    """
    # 1. 参数验证
    if not all([order_id, current_branch_id, operate_type]):
        print("❌ 缺少必填参数（order_id/current_branch_id/operate_type）")
        return False
    
    # 验证操作类型
    if operate_type not in ['0', '1', '2', '3', '4']:
        print(f"❌ 操作类型错误：{operate_type}（应为0-4）")
        return False
    
    # 2. 构建轨迹数据
    track_data = {
        'orderId': order_id,
        'operateBranchId': current_branch_id,
        'prevBranchId': prev_branch_id if prev_branch_id else 'NULL',
        'nextBranchId': next_branch_id if next_branch_id else 'NULL',
        'operateType': operate_type,
        'operateTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 3. 写入轨迹文件
    track_path = os.path.join(DATA_DIR, "ExpressTrack.csv")
    
    try:
        success = write_csv(track_path, track_data)
        
        if success:
            print(f"✅ 轨迹记录已写入：{track_path}")
            
            # 可选：重建轨迹表索引
            try:
                from index_core import HashIndex
                track_index = HashIndex("ExpressTrack", "orderId")
                track_index.rebuild()
                print("✅ 轨迹索引已更新")
            except ImportError:
                pass  # 索引模块不存在，跳过
            
            return True
        else:
            print(f"❌ 轨迹写入失败")
            return False
    
    except Exception as e:
        print(f"❌ 写入轨迹时发生错误：{e}")
        return False


def get_latest_track(order_id: str) -> Optional[Dict]:
    """
    获取快递的最新轨迹记录
    
    Args:
        order_id: 快递单号
        
    Returns:
        最新轨迹记录字典，未找到返回None
    """
    tracks = express_spatial_track(order_id)
    
    if not tracks:
        return None
    
    # 返回最后一条轨迹
    return tracks[-1]
