import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # 确保使用Tkinter兼容后端

# 配置Matplotlib支持中文（Windows/macOS/Linux通用）
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]  # 优先选系统已有的中文字体
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


def parse_coordinate(coord_str):
    """
    解析坐标字符串为经纬度元组
    :param coord_str: 格式 "minLng,minLat,maxLng,maxLat" 或 "lng,lat"
    :return: (经度, 纬度)
    """
    try:
        # print(coord_str,"\n")
        if ',' not in coord_str or coord_str == '未知坐标':
            return None
        parts = coord_str.split(',')
        # 取中心点坐标（若为范围则取平均值）
        if len(parts) == 4:
            lng = (float(parts[0]) + float(parts[2])) / 2
            lat = (float(parts[1]) + float(parts[3])) / 2
        else:
            lng, lat = float(parts[0]), float(parts[1])
        return (lng, lat)
    except (ValueError, IndexError):
        return None


def visualize_track_matplotlib(track_data, parent_frame):
    """
    在Tkinter框架中绘制快递轨迹路线图（Matplotlib版）
    :param track_data: express_spatial_track返回的轨迹数据列表
    :param parent_frame: Tkinter父容器（用于嵌入图表）
    """
    if not track_data:
        return None
    
    # 解析所有站点坐标
    points = []
    labels = []
    for idx, track in enumerate(track_data):
        coord = parse_coordinate(track.get('当前网点坐标', ''))
        if coord:
            points.append(coord)
            labels.append(f"{idx+1}. {track['当前网点名称']}\n{track['操作类型']}")
    
    if len(points) < 2:
        print("警告：有效坐标点少于2个，无法绘制路线")
        return None
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制路线（折线）
    lngs, lats = zip(*points)
    ax.plot(lngs, lats, 'b-', linewidth=2, marker='o', markersize=8, label='物流路线')
    
    # 标注起点和终点
    ax.plot(lngs[0], lats[0], 'go', markersize=15, label='起点')
    ax.plot(lngs[-1], lats[-1], 'ro', markersize=15, label='终点')
    
    # 添加站点标签
    for (lng, lat), label in zip(points, labels):
        ax.annotate(label, (lng, lat), fontsize=8, ha='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # 设置坐标轴
    ax.set_xlabel('经度', fontsize=12)
    ax.set_ylabel('纬度', fontsize=12)
    ax.set_title(f'快递轨迹可视化（共{len(points)}个站点）', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 嵌入Tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    return canvas


def visualize_track_window(track_data):
    """
    独立窗口展示轨迹图（不依赖父容器）
    :param track_data: 轨迹数据列表
    """
    import tkinter as tk
    from tkinter import ttk
    
    window = tk.Toplevel()
    window.title("快递轨迹可视化")
    window.geometry("1000x700")
    
    # 创建容器
    frame = ttk.Frame(window)
    frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # 绘制图表
    visualize_track_matplotlib(track_data, frame)
    
    # 添加关闭按钮
    ttk.Button(window, text="关闭", command=window.destroy).pack(pady=10)
