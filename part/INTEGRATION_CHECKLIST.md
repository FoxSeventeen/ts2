# 集成清单 - 需要从原项目复制的文件

## ✅ 已提供的新增/修改文件

### 新增文件
- ✅ `visualization.py` - 可视化核心模块
- ✅ `test_visualization.py` - 测试脚本
- ✅ `README_VISUALIZATION.md` - 详细文档
- ✅ `QUICKSTART.md` - 快速启动指南
- ✅ `database/data/ExpressBranch.csv` - 测试网点数据
- ✅ `database/data/ExpressTrack.csv` - 测试轨迹数据

### 修改文件
- ✅ `gui.py` - 已添加可视化按钮（完整版本）

---

## 📦 需要从原项目保留的文件

### 核心模块（必须）
请从您的原项目中复制以下文件到新项目目录：

1. **db_core.py** - 数据库核心层
   - 包含 `read_csv()`, `write_csv()` 等函数
   - 定义了 `DATA_DIR`, `INDEX_DIR` 常量

2. **spatial_core.py** - 空间数据处理
   - 包含 `express_spatial_track()` 函数（可视化依赖）
   - 包含 `generate_express_track()` 等函数

3. **index_core.py** - 索引引擎
   - 包含 `HashIndex` 类（GUI需要）

4. **main.py** - 主程序入口
   - 系统初始化和启动逻辑

### 数据文件（生产环境）
如果需要在生产数据上测试，需复制：

```
database/
├── data/
│   ├── User.csv              # 用户表（GUI需要）
│   ├── ExpressOrder.csv       # 快递单表
│   ├── ExpressBranch.csv      # 网点表（可视化核心依赖）⭐
│   ├── ExpressTrack.csv       # 轨迹表（可视化核心依赖）⭐
│   └── Courier.csv            # 快递员表（可选）
└── index/
    └── *.idx                  # 索引文件（自动生成）
```

**注意**：如果只想测试可视化功能，使用提供的测试数据即可，无需复制生产数据。

---

## 🔧 集成步骤

### 方案A：完全替换（推荐）
1. 备份原项目
2. 用提供的 `gui.py` 替换原文件
3. 将 `visualization.py` 放到项目根目录
4. 安装依赖：`pip install matplotlib`
5. 运行测试：`python test_visualization.py`

### 方案B：手动合并（适合已修改过gui.py）
如果您已经修改过 `gui.py`，可以只复制关键代码：

#### 步骤1：在文件头部导入
```python
# 在 gui.py 顶部添加
try:
    from visualization import visualize_track_window
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
```

#### 步骤2：修改 `show_query_track()` 方法
找到原来的 `show_query_track()` 函数，修改为：

```python
def show_query_track(self):
    """查询快递轨迹对话框（新增可视化按钮）"""
    dialog = tk.Toplevel(self.root)
    dialog.title("查询快递轨迹")
    dialog.geometry("400x200")

    ttk.Label(dialog, text="快递单号：").grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
    order_id_var = tk.StringVar()
    ttk.Entry(dialog, textvariable=order_id_var).grid(row=0, column=1, padx=10, pady=20, sticky=tk.EW)

    def query_text():
        """原有的文本查询功能"""
        order_id = order_id_var.get().strip()
        if not order_id:
            messagebox.showwarning("警告", "请输入快递单号！")
            return
        track_data = express_spatial_track(order_id)
        self.update_tree_view(track_data)
        dialog.destroy()

    def query_visual():
        """新增：可视化查询"""
        order_id = order_id_var.get().strip()
        if not order_id:
            messagebox.showwarning("警告", "请输入快递单号！")
            return
        track_data = express_spatial_track(order_id)
        if not track_data:
            messagebox.showinfo("提示", "无轨迹数据")
            return
        visualize_track_window(track_data)
        dialog.destroy()

    # 按钮布局
    button_frame = ttk.Frame(dialog)
    button_frame.grid(row=1, column=0, columnspan=2, pady=20)
    ttk.Button(button_frame, text="文本查询", command=query_text).pack(side=tk.LEFT, padx=10)
    
    if VISUALIZATION_AVAILABLE:
        ttk.Button(button_frame, text="�图 可视化轨迹", command=query_visual).pack(side=tk.LEFT, padx=10)
```

---

## 🎯 验证清单

完成集成后，按以下步骤验证：

### ✅ 测试1：独立测试
```bash
python test_visualization.py
```
**预期**：弹出轨迹图，显示5个站点的路线

### ✅ 测试2：GUI集成
```bash
python main.py
```
1. 点击 **快递管理 → 查询快递轨迹**
2. 输入 `EXP001`
3. 点击 **🗺️ 可视化轨迹**
4. **预期**：弹出独立窗口显示轨迹图

### ✅ 测试3：数据完整性
检查以下文件是否存在且格式正确：
- `database/data/ExpressBranch.csv`（必须包含 `coordinateRange` 列）
- `database/data/ExpressTrack.csv`（必须包含快递单号对应的轨迹）

---

## 🚨 常见集成问题

### 问题1：导入错误 "No module named 'db_core'"
**原因**：缺少核心模块文件
**解决**：从原项目复制 `db_core.py`

### 问题2：可视化按钮不显示
**原因**：matplotlib未安装
**检查**：
```python
import matplotlib  # 如果报错则需安装
```

### 问题3：查询不到轨迹数据
**原因**：数据文件路径错误或数据格式问题
**检查**：
1. 确认 `database/data/` 目录存在
2. 打开CSV文件查看列名和格式
3. 运行 `test_visualization.py` 查看控制台输出

### 问题4：坐标解析失败
**症状**：图表显示"有效坐标点少于2个"
**解决**：
1. 检查 `ExpressBranch.csv` 的 `coordinateRange` 列
2. 确保格式为：`经度1,纬度1,经度2,纬度2`
3. 示例：`116.4,39.9,116.5,40.0`

---

## 📊 最终文件结构

完成集成后，项目结构应该是：

```
项目根目录/
├── main.py                    # 从原项目保留
├── gui.py                     # ⭐ 使用新版本
├── db_core.py                 # 从原项目保留
├── spatial_core.py            # 从原项目保留
├── index_core.py              # 从原项目保留
├── visualization.py           # ⭐ 新增文件
├── test_visualization.py      # ⭐ 新增文件（测试用）
├── README_VISUALIZATION.md    # ⭐ 新增文档
├── QUICKSTART.md              # ⭐ 新增文档
└── database/
    ├── data/
    │   ├── User.csv
    │   ├── ExpressOrder.csv
    │   ├── ExpressBranch.csv      # ⭐ 必须包含坐标
    │   ├── ExpressTrack.csv       # ⭐ 必须包含轨迹
    │   └── Courier.csv
    └── index/
        └── *.idx
```

---

## 🎓 下一步建议

完成基础集成后，可以考虑：
1. 参考 `README_VISUALIZATION.md` 实现 Folium 真实地图方案
2. 添加轨迹动画效果
3. 集成热力图分析配送密度
4. 实现3D时空轨迹图

---

**重要提示**：
- 核心依赖：`visualization.py` + `spatial_core.py` + 正确的CSV数据
- 最小化测试：只需 `test_visualization.py` + 测试数据
- 生产环境：需完整的文件和数据结构

有问题请参考 `QUICKSTART.md` 或 `README_VISUALIZATION.md`！
