# 快递轨迹可视化 - 快速启动指南

## 🚀 30秒快速体验

### 步骤1：安装依赖
```bash
pip install matplotlib
```

### 步骤2：测试可视化
```bash
python test_visualization.py
```
**效果**：自动查询快递单号 `EXP001` 的轨迹并弹出可视化窗口

### 步骤3：集成到系统（可选）
如果需要在完整系统中使用，需要确保以下文件存在：
```
项目目录/
├── visualization.py       # ✅ 已提供
├── gui.py                  # ✅ 已修改（含可视化按钮）
├── spatial_core.py         # 需要从原项目复制
├── db_core.py              # 需要从原项目复制
├── index_core.py           # 需要从原项目复制
└── database/
    └── data/
        ├── ExpressBranch.csv   # ✅ 已提供测试数据
        └── ExpressTrack.csv    # ✅ 已提供测试数据
```

---

## 📋 文件说明

### 核心文件（新增）
1. **visualization.py** - 可视化核心模块
   - `parse_coordinate()` - 坐标解析
   - `visualize_track_matplotlib()` - Matplotlib绘图
   - `visualize_track_window()` - 独立窗口展示

2. **gui.py**（已修改）
   - 在 `show_query_track()` 中新增 **"🗺️ 可视化轨迹"** 按钮
   - 自动检测matplotlib是否安装

3. **test_visualization.py** - 测试脚本
   - 查询快递单号 `EXP001` 的轨迹
   - 打印轨迹详情
   - 弹出可视化窗口

### 数据文件（测试用）
- **ExpressBranch.csv** - 5个测试网点（北京/上海/广州/深圳/杭州）
- **ExpressTrack.csv** - 2个快递的完整轨迹

---

## 🎯 使用场景

### 场景1：独立测试（推荐初学者）
```bash
python test_visualization.py
```
- 无需修改现有代码
- 快速验证功能

### 场景2：集成到GUI系统
1. 启动主程序：`python main.py`
2. 菜单操作：**快递管理 → 查询快递轨迹**
3. 输入单号：`EXP001`
4. 点击：**🗺️ 可视化轨迹**

### 场景3：编程调用
```python
from spatial_core import express_spatial_track
from visualization import visualize_track_window

# 查询轨迹
track_data = express_spatial_track("EXP001")

# 可视化
visualize_track_window(track_data)
```

---

## ⚙️ 配置说明

### 坐标格式要求
在 `ExpressBranch.csv` 中，坐标格式必须为：
```
coordinateRange: minLng,minLat,maxLng,maxLat
```
示例：`116.4,39.9,116.5,40.0`（经度范围116.4-116.5，纬度范围39.9-40.0）

### 支持的操作类型
在 `ExpressTrack.csv` 中：
- `0` = 收件
- `1` = 中转入库
- `2` = 中转出库
- `3` = 派送
- `4` = 签收

---

## 🐛 常见问题

### Q1: 运行时提示 "No module named 'matplotlib'"
**解决**：
```bash
pip install matplotlib
```

### Q2: 图表显示空白
**原因**：坐标数据格式错误或缺失
**检查**：
1. 打开 `database/data/ExpressBranch.csv`
2. 确认 `coordinateRange` 列为数字格式
3. 运行测试脚本查看控制台输出

### Q3: 中文显示乱码
**解决**：在代码开头添加
```python
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
```

### Q4: 测试数据不存在
**解决**：
```bash
# 确保目录结构正确
mkdir -p database/data
# 复制提供的CSV文件到该目录
```

---

## 📈 进阶方案

如果需要更强大的功能，可参考 `README_VISUALIZATION.md` 中的：
- **方案2：Folium真实地图**（交互式，需浏览器）
- **方案3：tkintermapview**（直接嵌入GUI，推荐生产环境）

---

## 📞 技术支持

遇到问题时：
1. 查看控制台错误信息
2. 检查数据文件格式
3. 确认依赖库已安装

**预期效果**：
- 蓝色折线连接各个站点
- 绿色圆点标记起点
- 红色圆点标记终点
- 黄色标签显示站点信息

---

**开发提示**：此方案基于Matplotlib，适合快速验证功能。生产环境推荐使用 tkintermapview 方案！
