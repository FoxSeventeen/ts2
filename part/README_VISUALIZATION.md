# 快递轨迹空间可视化实现指南

## 📦 方案1：Matplotlib静态路线图（已实现）

### 🎯 实现效果
- ✅ 绘制快递轨迹路线图（折线+标注）
- ✅ 标记起点（绿色）和终点（红色）
- ✅ 显示每个站点的操作类型
- ✅ 直接嵌入Tkinter GUI

### 🛠️ 安装依赖
```bash
pip install matplotlib
```

### 📂 文件说明
```
项目根目录/
├── visualization.py          # 可视化模块（新增）
├── gui.py                     # GUI界面（已修改）
├── spatial_core.py            # 空间数据处理
├── db_core.py                 # 数据库核心
├── index_core.py              # 索引引擎
├── test_visualization.py      # 测试脚本（新增）
└── database/
    └── data/
        ├── ExpressBranch.csv      # 网点数据（新增）
        └── ExpressTrack.csv       # 轨迹数据（新增）
```

### 🚀 使用方法

#### 方法1：通过GUI操作
1. 运行主程序：`python main.py`
2. 点击菜单：**快递管理 → 查询快递轨迹**
3. 输入快递单号（如：EXP001）
4. 点击 **🗺️ 可视化轨迹** 按钮
5. 自动弹出轨迹图窗口

#### 方法2：独立测试
```bash
python test_visualization.py
```

#### 方法3：编程调用
```python
from spatial_core import express_spatial_track
from visualization import visualize_track_window

# 查询轨迹数据
track_data = express_spatial_track("EXP001")

# 可视化展示
visualize_track_window(track_data)
```

### 📊 数据格式要求
确保 `ExpressBranch.csv` 包含网点坐标：
```csv
branchId,branchName,coordinateRange
B001,北京朝阳分拨中心,116.4,39.9,116.5,40.0
```
坐标格式：`minLng,minLat,maxLng,maxLat`（经纬度范围）

### 🔧 核心代码解析

#### 1. 坐标解析函数
```python
def parse_coordinate(coord_str):
    """将坐标字符串转为(经度,纬度)元组"""
    parts = coord_str.split(',')
    if len(parts) == 4:  # 范围坐标
        lng = (float(parts[0]) + float(parts[2])) / 2
        lat = (float(parts[1]) + float(parts[3])) / 2
    else:  # 点坐标
        lng, lat = float(parts[0]), float(parts[1])
    return (lng, lat)
```

#### 2. Matplotlib绘图核心
```python
# 绘制路线
ax.plot(lngs, lats, 'b-', linewidth=2, marker='o')

# 标记起点/终点
ax.plot(lngs[0], lats[0], 'go', markersize=15, label='起点')
ax.plot(lngs[-1], lats[-1], 'ro', markersize=15, label='终点')

# 添加站点标签
ax.annotate(label, (lng, lat), fontsize=8)
```

### ⚠️ 常见问题

**Q1: 图表显示空白或报错？**
- 检查坐标格式是否正确（必须是数字）
- 确保至少有2个有效坐标点
- 查看控制台错误信息

**Q2: 中文乱码？**
- 在`main.py`中添加：
```python
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
matplotlib.rcParams['axes.unicode_minus'] = False
```

**Q3: Tkinter窗口关闭后程序卡死？**
- 使用 `visualize_track_window()` 而非 `visualize_track_matplotlib()`
- 前者会自动创建独立窗口

---

## 🌐 方案2：Folium真实地图（进阶）

### 🎯 适用场景
- 需要显示真实地理地图
- 对外展示/演示系统
- 需要交互缩放功能

### 🛠️ 安装依赖
```bash
pip install folium
```

### 📝 实现代码
在 `visualization.py` 中添加：

```python
import folium
import webbrowser
import tempfile

def visualize_track_folium(track_data, order_id):
    """使用Folium生成交互式地图"""
    if not track_data:
        return None
    
    # 解析坐标
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
        print("坐标点不足，无法生成地图")
        return None
    
    # 创建地图（中心点为路线中点）
    center_lat = sum(p['coord'][1] for p in points) / len(points)
    center_lng = sum(p['coord'][0] for p in points) / len(points)
    
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # 绘制路线
    route = [p['coord'][::-1] for p in points]  # 注意：folium需要[纬度,经度]
    folium.PolyLine(
        route,
        color='blue',
        weight=3,
        opacity=0.8,
        popup=f'快递单号：{order_id}'
    ).add_to(m)
    
    # 添加站点标记
    for idx, point in enumerate(points):
        icon_color = 'green' if idx == 0 else ('red' if idx == len(points)-1 else 'blue')
        folium.Marker(
            location=point['coord'][::-1],
            popup=f"""
            <b>{point['name']}</b><br>
            操作：{point['type']}<br>
            时间：{point['time']}
            """,
            icon=folium.Icon(color=icon_color, icon='info-sign')
        ).add_to(m)
    
    # 保存并打开
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
        m.save(f.name)
        webbrowser.open('file://' + f.name)
        print(f"✅ 地图已生成：{f.name}")
    
    return m
```

### 🚀 使用方法
在 `gui.py` 的 `show_query_track()` 中添加按钮：
```python
def query_folium():
    order_id = order_id_var.get().strip()
    track_data = express_spatial_track(order_id)
    from visualization import visualize_track_folium
    visualize_track_folium(track_data, order_id)

ttk.Button(button_frame, text="🌍 真实地图", command=query_folium).pack(side=tk.LEFT)
```

---

## 🏆 方案3：tkintermapview（最佳）

### 🎯 优势
- ✅ 直接嵌入Tkinter，无需浏览器
- ✅ 显示真实地图（OpenStreetMap）
- ✅ 支持交互操作（缩放、拖动）

### 🛠️ 安装依赖
```bash
pip install tkintermapview
```

### 📝 实现代码
在 `visualization.py` 中添加：

```python
try:
    import tkintermapview
    MAPVIEW_AVAILABLE = True
except ImportError:
    MAPVIEW_AVAILABLE = False

def visualize_track_mapview(track_data, parent_frame):
    """使用tkintermapview嵌入真实地图"""
    if not MAPVIEW_AVAILABLE:
        print("请先安装: pip install tkintermapview")
        return None
    
    if not track_data:
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
                'type': track['操作类型']
            })
    
    if len(points) < 2:
        return None
    
    # 创建地图控件
    map_widget = tkintermapview.TkinterMapView(parent_frame, width=900, height=600)
    map_widget.pack(fill='both', expand=True)
    
    # 设置中心点
    center_lat = sum(p['lat'] for p in points) / len(points)
    center_lng = sum(p['lng'] for p in points) / len(points)
    map_widget.set_position(center_lat, center_lng)
    map_widget.set_zoom(8)
    
    # 绘制路线
    coords = [(p['lat'], p['lng']) for p in points]
    map_widget.set_path(coords, color='blue', width=3)
    
    # 添加标记点
    for idx, point in enumerate(points):
        marker_text = f"{idx+1}. {point['name']}\n{point['type']}"
        map_widget.set_marker(
            point['lat'], 
            point['lng'],
            text=marker_text
        )
    
    return map_widget
```

### 🚀 使用方法
在 `gui.py` 中创建新窗口：
```python
def show_track_mapview(track_data):
    window = tk.Toplevel()
    window.title("快递轨迹地图")
    window.geometry("1000x700")
    
    from visualization import visualize_track_mapview
    visualize_track_mapview(track_data, window)
```

---

## 📊 功能对比表

| 特性 | Matplotlib | Folium | tkintermapview |
|------|-----------|--------|----------------|
| 安装难度 | ⭐ | ⭐⭐ | ⭐⭐ |
| 真实地图 | ❌ | ✅ | ✅ |
| GUI集成 | ✅ | ❌ | ✅ |
| 交互性 | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 网络依赖 | ❌ | ✅ | ✅ |
| 推荐指数 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎓 扩展功能建议

### 1. 实时轨迹动画
```python
import matplotlib.animation as animation

def animate_track(frame):
    # 逐帧绘制轨迹点
    pass

ani = animation.FuncAnimation(fig, animate_track, frames=len(points))
```

### 2. 热力图分析
```python
from folium.plugins import HeatMap

# 分析配送区域密度
HeatMap(branch_coords).add_to(m)
```

### 3. 3D轨迹图
```python
from mpl_toolkits.mplot3d import Axes3D

ax = fig.add_subplot(111, projection='3d')
ax.plot(lngs, lats, times)  # 时间作为Z轴
```

---

## 📞 技术支持
- 遇到问题请检查控制台输出
- 确保CSV数据格式正确
- 坐标必须为有效数字

**开发建议**：先用方案1快速验证功能，生产环境推荐方案3（tkintermapview）！
