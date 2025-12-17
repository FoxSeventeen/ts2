# visualization_advanced.py
"""
快递轨迹可视化 - 进阶方案
包含Folium真实地图和tkintermapview嵌入方案
"""

# ==================== 方案2：Folium真实地图 ====================

def visualize_track_folium(track_data, order_id):
    """
    使用Folium生成交互式真实地图
    :param track_data: express_spatial_track返回的轨迹数据
    :param order_id: 快递单号
    :return: folium.Map对象
    """
    try:
        import folium
        import webbrowser
        import tempfile
    except ImportError:
        print("请先安装folium: pip install folium")
        return None
    
    if not track_data:
        print("轨迹数据为空")
        return None
    
    # 从visualization.py导入坐标解析函数（或在此处重复定义）
    def parse_coordinate(coord_str):
        try:
            if ',' not in coord_str or coord_str == '未知坐标':
                return None
            parts = coord_str.split(',')
            if len(parts) == 4:
                lng = (float(parts[0]) + float(parts[2])) / 2
                lat = (float(parts[1]) + float(parts[3])) / 2
            else:
                lng, lat = float(parts[0]), float(parts[1])
            return (lng, lat)
        except (ValueError, IndexError):
            return None
    
    # 解析所有站点坐标
    points = []
    for track in track_data:
        coord = parse_coordinate(track.get('当前网点坐标', ''))
        if coord:
            points.append({
                'coord': coord,
                'name': track['当前网点名称'],
                'time': track['操作时间'],
                'type': track['操作类型']
            })
    
    if len(points) < 2:
        print("有效坐标点少于2个，无法生成地图")
        return None
    
    # 计算地图中心点
    center_lat = sum(p['coord'][1] for p in points) / len(points)
    center_lng = sum(p['coord'][0] for p in points) / len(points)
    
    # 创建地图（使用OpenStreetMap底图）
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=6,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # 绘制路线（注意：folium使用[纬度,经度]顺序）
    route = [[p['coord'][1], p['coord'][0]] for p in points]
    folium.PolyLine(
        route,
        color='#2E86AB',
        weight=4,
        opacity=0.8,
        popup=f'快递单号：{order_id}',
        tooltip='点击查看快递单号'
    ).add_to(m)
    
    # 添加站点标记
    for idx, point in enumerate(points):
        # 确定标记颜色：起点绿色、终点红色、中间蓝色
        if idx == 0:
            icon_color = 'green'
            icon = 'play'
        elif idx == len(points) - 1:
            icon_color = 'red'
            icon = 'stop'
        else:
            icon_color = 'blue'
            icon = 'info-sign'
        
        # 创建标记
        folium.Marker(
            location=[point['coord'][1], point['coord'][0]],
            popup=folium.Popup(f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #2E86AB;">站点 {idx + 1}</h4>
                    <p style="margin: 5px 0;"><b>网点：</b>{point['name']}</p>
                    <p style="margin: 5px 0;"><b>操作：</b>{point['type']}</p>
                    <p style="margin: 5px 0;"><b>时间：</b>{point['time']}</p>
                </div>
            """, max_width=250),
            tooltip=f"{idx + 1}. {point['name']}",
            icon=folium.Icon(color=icon_color, icon=icon, prefix='glyphicon')
        ).add_to(m)
    
    # 添加全屏按钮
    folium.plugins.Fullscreen(
        position='topright',
        title='全屏显示',
        title_cancel='退出全屏',
        force_separate_button=True
    ).add_to(m)
    
    # 添加鼠标坐标显示
    folium.plugins.MousePosition().add_to(m)
    
    # 保存为HTML并在浏览器中打开
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
        html_path = f.name
        m.save(html_path)
    
    print(f"✅ 地图已生成：{html_path}")
    webbrowser.open('file://' + html_path)
    
    return m


# ==================== 方案3：tkintermapview嵌入方案 ====================

def visualize_track_mapview_window(track_data, order_id):
    """
    使用tkintermapview在独立窗口中显示真实地图
    :param track_data: express_spatial_track返回的轨迹数据
    :param order_id: 快递单号
    """
    try:
        import tkintermapview
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("请先安装tkintermapview: pip install tkintermapview")
        return None
    
    if not track_data:
        print("轨迹数据为空")
        return None
    
    # 坐标解析函数
    def parse_coordinate(coord_str):
        try:
            if ',' not in coord_str or coord_str == '未知坐标':
                return None
            parts = coord_str.split(',')
            if len(parts) == 4:
                lng = (float(parts[0]) + float(parts[2])) / 2
                lat = (float(parts[1]) + float(parts[3])) / 2
            else:
                lng, lat = float(parts[0]), float(parts[1])
            return (lng, lat)
        except (ValueError, IndexError):
            return None
    
    # 解析坐标
    points = []
    for track in track_data:
        coord = parse_coordinate(track.get('当前网点坐标', ''))
        if coord:
            points.append({
                'lat': coord[1],
                'lng': coord[0],
                'name': track['当前网点名称'],
                'type': track['操作类型'],
                'time': track['操作时间']
            })
    
    if len(points) < 2:
        print("有效坐标点少于2个，无法生成地图")
        return None
    
    # 创建窗口
    window = tk.Toplevel()
    window.title(f"快递轨迹地图 - {order_id}")
    window.geometry("1000x700")
    
    # 创建信息面板
    info_frame = ttk.Frame(window, height=50)
    info_frame.pack(fill='x', padx=10, pady=5)
    
    ttk.Label(info_frame, text=f"快递单号：{order_id}",
             font=('Arial', 12, 'bold')).pack(side='left', padx=10)
    ttk.Label(info_frame, text=f"共{len(points)}个站点",
             font=('Arial', 10)).pack(side='left', padx=10)
    
    # 创建地图控件
    map_widget = tkintermapview.TkinterMapView(window, width=980, height=600, corner_radius=0)
    map_widget.pack(fill='both', expand=True, padx=10, pady=5)
    
    # 设置地图类型（OpenStreetMap）
    map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
    
    # 计算并设置中心点
    center_lat = sum(p['lat'] for p in points) / len(points)
    center_lng = sum(p['lng'] for p in points) / len(points)
    map_widget.set_position(center_lat, center_lng)
    map_widget.set_zoom(8)
    
    # 绘制路线
    coords = [(p['lat'], p['lng']) for p in points]
    path = map_widget.set_path(coords, color='#2E86AB', width=4)
    
    # 添加标记点
    markers = []
    for idx, point in enumerate(points):
        marker_color = 'green' if idx == 0 else ('red' if idx == len(points)-1 else 'blue')
        marker_text = f"{idx+1}. {point['name']}\n{point['type']}\n{point['time']}"
        
        marker = map_widget.set_marker(
            point['lat'],
            point['lng'],
            text=marker_text,
            marker_color_circle=marker_color,
            marker_color_outside=marker_color
        )
        markers.append(marker)
    
    # 创建控制按钮
    button_frame = ttk.Frame(window)
    button_frame.pack(fill='x', padx=10, pady=5)
    
    def zoom_in():
        map_widget.set_zoom(map_widget.zoom + 1)
    
    def zoom_out():
        map_widget.set_zoom(map_widget.zoom - 1)
    
    def reset_view():
        map_widget.set_position(center_lat, center_lng)
        map_widget.set_zoom(8)
    
    ttk.Button(button_frame, text="放大 +", command=zoom_in).pack(side='left', padx=5)
    ttk.Button(button_frame, text="缩小 -", command=zoom_out).pack(side='left', padx=5)
    ttk.Button(button_frame, text="重置视图", command=reset_view).pack(side='left', padx=5)
    ttk.Button(button_frame, text="关闭", command=window.destroy).pack(side='right', padx=5)
    
    print(f"✅ 地图窗口已创建（共{len(points)}个站点）")
    return window


# ==================== 测试函数 ====================

def test_advanced_visualization():
    """测试进阶可视化方案"""
    from spatial_core import express_spatial_track
    
    # 查询测试数据
    test_order_id = "EXP001"
    track_data = express_spatial_track(test_order_id)
    
    if not track_data:
        print("❌ 未找到测试数据")
        return
    
    print(f"\n✅ 查询到 {len(track_data)} 条轨迹记录")
    
    # 提示用户选择方案
    print("\n请选择可视化方案：")
    print("1. Folium真实地图（浏览器打开）")
    print("2. tkintermapview地图（GUI嵌入）")
    choice = input("请输入选项（1或2）：").strip()
    
    if choice == '1':
        print("\n启动Folium方案...")
        visualize_track_folium(track_data, test_order_id)
    elif choice == '2':
        print("\n启动tkintermapview方案...")
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        visualize_track_mapview_window(track_data, test_order_id)
        root.mainloop()
    else:
        print("无效选项")


if __name__ == "__main__":
    test_advanced_visualization()
