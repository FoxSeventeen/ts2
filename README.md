# 测试数据说明文档

## 📊 数据概览

本测试数据集包含15个快递单、15个用户、15个网点、10个快递员，涵盖中国11个主要城市，提供完整的业务场景测试。

---

## 📁 数据文件清单

### 1. User.csv - 用户表（15条）
**字段说明**：
- `uid`: 用户ID（唯一标识）
- `uname`: 姓名
- `utype`: 用户类型（普通用户/商家用户/快递员）
- `uphone`: 手机号（11位）
- `uprovince`: 省份
- `ucity`: 城市
- `uaddress`: 详细地址
- `uidcard`: 身份证号（18位）

**数据特点**：
- 包含3种用户类型：普通用户、商家用户、快递员
- 覆盖11个城市：北京、上海、广州、深圳、杭州、南京、成都、武汉、厦门、青岛、天津
- 手机号格式：138001380XX（测试号段）

**关键用户**：
- U001-U006: 主要寄件人/收件人
- U007-U008, U014-U015: 快递员（同时在Courier表中）
- U002, U005, U010, U013: 商家用户

---

### 2. ExpressBranch.csv - 快递网点表（15条）
**字段说明**：
- `branchId`: 网点ID
- `branchName`: 网点名称
- `branchType`: 网点类型（分拨中心/营业点）
- `coordinateRange`: 坐标范围（minLng,minLat,maxLng,maxLat）
- `province/city/address`: 地址信息

**坐标格式**：
```
格式：最小经度,最小纬度,最大经度,最大纬度
示例：116.43,39.91,116.47,39.95
说明：定义一个矩形区域，可视化时取中心点
```

**网点分布**：
- **分拨中心**（5个）：B001（北京）、B002（上海）、B006（南京）、B008（武汉）、B011（天津）
- **营业点**（10个）：覆盖各主要城区

**真实坐标参考**：
| 网点ID | 城市 | 经度 | 纬度 |
|--------|------|------|------|
| B001 | 北京朝阳 | 116.45 | 39.93 |
| B002 | 上海浦东 | 121.52 | 31.24 |
| B003 | 广州天河 | 113.34 | 23.14 |
| B004 | 深圳南山 | 113.95 | 22.55 |
| B005 | 杭州西湖 | 120.17 | 30.27 |

---

### 3. Courier.csv - 快递员表（10条）
**字段说明**：
- `courierId`: 快递员ID
- `courierName`: 姓名
- `courierPhone`: 手机号
- `branchId`: 所属网点
- `workStatus`: 工作状态（在职/休假）

**关联关系**：
- `courierPhone` 关联 `User.uphone`（快递员也是用户）
- `branchId` 关联 `ExpressBranch.branchId`

**分配情况**：
- B001（北京）: 2名快递员（C001, C005）
- B002（上海）: 2名快递员（C002, C006）
- 其他网点各1名

---

### 4. ExpressOrder.csv - 快递单表（15条）
**字段说明**：
- `orderId`: 快递单号
- `senderId`: 寄件人ID（关联User.uid）
- `receiverId`: 收件人ID（关联User.uid）
- `goodsName`: 物品名称
- `goodsWeight`: 物品重量（kg）
- `sendBranchId`: 寄件网点（关联ExpressBranch.branchId）
- `targetBranchId`: 目标网点
- `sendTime`: 寄件时间
- `estimatedTime`: 预计送达时间
- `orderStatus`: 快递状态（0-5）

**状态说明**：
```
0 - 待收件：EXP006
1 - 已收件：EXP004, EXP007, EXP015（3条）
2 - 中转中：EXP003, EXP005, EXP010, EXP012（4条）
3 - 派送中：EXP002, EXP009, EXP013（3条）
4 - 已签收：EXP001, EXP008, EXP011（3条）
5 - 异常：EXP014（1条）
```

**物流路线示例**：
- **EXP001**（已签收）: 北京B001 → 上海B002 → 南京B006 → 广州B003 → 深圳B004
- **EXP002**（派送中）: 上海B002 → 杭州B005
- **EXP008**（当日达）: 北京B001 → 上海B002（同城/快速）

**测试场景**：
1. 跨城长途：EXP001（5个站点）
2. 直达快递：EXP002（2个站点）
3. 异常件：EXP014（状态5）
4. 不同时间段：12月9日-14日

---

### 5. ExpressTrack.csv - 快递轨迹表（48条）
**字段说明**：
- `orderId`: 快递单号
- `operateBranchId`: 当前操作网点
- `prevBranchId`: 上个网点（NULL表示起点）
- `nextBranchId`: 下个网点（NULL表示终点）
- `operateType`: 操作类型（0-4）
- `operateTime`: 操作时间

**操作类型**：
```
0 - 收件：快递员上门揽件
1 - 中转入库：到达分拨中心/营业点
2 - 中转出库：从分拨中心发出
3 - 派送：派送员开始配送
4 - 签收：收件人签收
```

**完整轨迹示例（EXP001）**：
```
2024-12-10 08:30 | B001 | 收件
2024-12-10 10:15 | B001 | 中转入库
2024-12-11 06:20 | B002 | 中转出库（发往B006）
2024-12-11 14:30 | B006 | 中转出库（发往B003）
2024-12-12 09:45 | B003 | 中转出库（发往B004）
2024-12-13 11:30 | B004 | 派送
2024-12-13 15:00 | B004 | 签收
```

**可视化重点数据**：
- **EXP001**: 7条轨迹，5个城市（北京→上海→南京→广州→深圳）
- **EXP011**: 5条轨迹，上海→广州（经过徐汇中转）
- **EXP002**: 3条轨迹，上海→杭州（简单路线）

---

### 6. DeliveryZone.csv - 配送区域表（15条）
**字段说明**：
- `zoneId`: 区域ID
- `branchId`: 所属网点
- `zoneName`: 区域名称
- `coordinateRange`: 覆盖范围（经纬度矩形）
- `coverageArea`: 覆盖区域描述

**用途**：
- 空间范围查询（`spatial_zone_query`）
- 配送区域规划
- 热力图分析

**示例**：
- Z001: 北京朝阳北部区（望京、太阳宫）
- Z002: 北京朝阳南部区（国贸、CBD）

---

### 7. views.meta - 视图元数据（3个）
**定义的视图**：
1. **BranchMonthlySend**: 网点月度寄件量统计
2. **CourierDailyStats**: 快递员每日派送统计
3. **OrderStatusStats**: 快递状态分布统计

---

## 🔗 数据关联关系

### 核心关联图
```
User (寄件人/收件人)
  ↓ senderId/receiverId
ExpressOrder (快递单)
  ↓ orderId
ExpressTrack (轨迹)
  ↓ operateBranchId
ExpressBranch (网点)
  ↓ branchId
DeliveryZone (配送区域)

User (快递员)
  ↓ courierPhone = uphone
Courier (快递员)
  ↓ branchId
ExpressBranch (网点)
```

### 外键约束
- `ExpressOrder.senderId` → `User.uid`
- `ExpressOrder.receiverId` → `User.uid`
- `ExpressOrder.sendBranchId` → `ExpressBranch.branchId`
- `ExpressOrder.targetBranchId` → `ExpressBranch.branchId`
- `ExpressTrack.orderId` → `ExpressOrder.orderId`
- `ExpressTrack.operateBranchId` → `ExpressBranch.branchId`
- `Courier.branchId` → `ExpressBranch.branchId`
- `DeliveryZone.branchId` → `ExpressBranch.branchId`

---

## 🧪 测试场景

### 场景1：可视化完整物流路线
**测试数据**: EXP001
**预期效果**: 
- 显示5个站点的地图路线
- 起点绿色（北京B001）
- 终点红色（深圳B004）
- 中间站点蓝色（上海、南京、广州）

**测试命令**:
```bash
python test_visualization.py
# 输入快递单号: EXP001
```

### 场景2：查询用户信息
**测试数据**: 手机号 13800138001
**预期结果**: 查询到张三，北京朝阳区
```python
from db_core import query_user
results = query_user({"uphone": "13800138001"})
```

### 场景3：统计快递员派送量
**测试数据**: 快递员C001（周九）
**预期结果**: 查询今日派送记录（需修改日期）
```python
from db_core import join_courier_orders
stats = join_courier_orders("C001", "2024-12-13")
```

### 场景4：不同状态快递查询
```python
from db_core import query_express_order

# 查询待收件快递
pending = query_express_order({"orderStatus": "0"})  # EXP006

# 查询派送中快递
delivering = query_express_order({"orderStatus": "3"})  # EXP002, EXP009, EXP013

# 查询异常快递
abnormal = query_express_order({"orderStatus": "5"})  # EXP014
```

### 场景5：空间范围查询
```python
from spatial_core import spatial_zone_query

# 查询北京朝阳区的配送区域
zones = spatial_zone_query("B001", 116.43, 39.88, 116.50, 40.02)
# 预期返回: Z001, Z002
```

### 场景6：多表连接查询
**测试场景**: 查询快递EXP001的寄件人和收件人信息
```python
from db_core import read_csv

orders = read_csv("database/data/ExpressOrder.csv")
users = read_csv("database/data/User.csv")

order = [o for o in orders if o['orderId'] == 'EXP001'][0]
sender = [u for u in users if u['uid'] == order['senderId']][0]
receiver = [u for u in users if u['uid'] == order['receiverId']][0]

print(f"寄件人: {sender['uname']}, {sender['uphone']}")
print(f"收件人: {receiver['uname']}, {receiver['uphone']}")
# 预期输出: 寄件人: 张三, 13800138001
#          收件人: 赵六, 13800138004
```

---

## 📈 数据统计

### 按状态统计
| 状态 | 数量 | 快递单号 |
|------|------|----------|
| 待收件(0) | 1 | EXP006 |
| 已收件(1) | 3 | EXP004, EXP007, EXP015 |
| 中转中(2) | 4 | EXP003, EXP005, EXP010, EXP012 |
| 派送中(3) | 3 | EXP002, EXP009, EXP013 |
| 已签收(4) | 3 | EXP001, EXP008, EXP011 |
| 异常(5) | 1 | EXP014 |

### 按城市统计
| 城市 | 网点数 | 快递员数 | 快递单数（寄出） |
|------|--------|----------|------------------|
| 北京 | 2 | 2 | 3 |
| 上海 | 2 | 2 | 2 |
| 广州 | 2 | 1 | 2 |
| 深圳 | 2 | 1 | 1 |
| 杭州 | 1 | 1 | 2 |
| 其他 | 6 | 3 | 5 |

### 按物流距离统计
| 快递单号 | 站点数 | 距离类型 |
|----------|--------|----------|
| EXP001 | 5 | 超长途 |
| EXP011 | 4 | 长途 |
| EXP003, EXP005 | 3 | 中途 |
| EXP002, EXP008 | 2 | 短途/直达 |

---

## 🎯 关键测试点

### ✅ 数据完整性
- 所有外键关联正确
- 时间戳连续合理
- 坐标格式统一

### ✅ 业务逻辑
- 状态流转符合规则（0→1→2→3→4）
- 轨迹记录连续（prevBranchId/nextBranchId链接正确）
- 异常件（EXP014）有轨迹但未送达

### ✅ 可视化测试
- **推荐测试**: EXP001（5站点，跨城）
- **备选测试**: EXP011（4站点，包含上海中转）
- **简单测试**: EXP002（2站点，直达）

---

## 🔧 数据维护

### 新增快递单模板
```csv
EXP016,U001,U005,测试物品,1.0,B001,B005,2024-12-15 08:00:00,2024-12-17 18:00:00,0
```

### 新增轨迹模板
```csv
EXP016,B001,NULL,B005,0,2024-12-15 08:00:00
EXP016,B001,NULL,B005,1,2024-12-15 09:30:00
```

### 坐标格式转换
```python
# 点坐标 → 范围坐标
lng, lat = 116.45, 39.93
offset = 0.04  # 约4公里
coord_range = f"{lng-offset},{lat-offset},{lng+offset},{lat+offset}"
# 输出: 116.41,39.89,116.49,39.97
```

---

## 📞 数据说明

- **测试环境**: 所有数据为虚构测试数据
- **手机号**: 采用测试号段 138001380XX
- **身份证号**: 采用测试格式，非真实数据
- **坐标精度**: 保留小数点后2位（约1公里精度）
- **时间范围**: 2024年12月9日-14日
- **数据量**: 小规模数据，适合功能验证

**重要提示**: 
1. 生产环境请使用真实数据
2. 坐标可使用高德/百度地图API获取
3. 手机号需符合运营商规则
4. 身份证号需通过校验算法

---

## 🚀 快速上手

### 验证数据完整性
```bash
# 检查文件是否存在
ls database/data/*.csv

# 统计数据量
wc -l database/data/*.csv

# 预期输出:
# 16 User.csv (15条数据+1行表头)
# 16 ExpressBranch.csv
# 11 Courier.csv
# 16 ExpressOrder.csv
# 49 ExpressTrack.csv
# 16 DeliveryZone.csv
```

### 测试可视化
```bash
python test_visualization.py
# 推荐测试快递单号: EXP001, EXP011, EXP002
```

### 测试GUI
```bash
python main.py
# 1. 用户管理 → 查询用户 → 手机号: 13800138001
# 2. 快递管理 → 查询快递单 → 单号: EXP001
# 3. 快递管理 → 查询快递轨迹 → 可视化: EXP001
```

---

**数据版本**: v1.0  
**创建日期**: 2024-12-14  
**适用系统**: 快递管理信息系统 v1.0





# 基本过程

1.维护快递员和用户的UID使用了冒泡排序和二分查找
	具体就是在增删直接添加和删除，而后执行冒泡排序，每次$O(n^2)$
	改在这个有序的基础上二分查找，然后删除$O(\log n)$

2.查询快递员和用户两种

​	二分，直接在冒泡排序有序的基础上，直接二分查找$O(\log n)$
​	每个用户和快递员加入时自动创建哈希映射，每次查找直接在对应映射位置查询即可。$O(1)$

3.快递轨迹可视化。

​	对于每一个快递，维护一个邻接矩阵，在快递单状态变化时，从当前出发的快递站点向下一个快递站点连接一条边，维护好快递路径$O(1)$
​	当查询可视化时，从最初的站点出发开始遍历。

4.使用高级数据结构平衡树Treap维护快递单UI，在有增删需求下进行快速修改和查询操作

在快递单管理系统中，Treap作为一种平衡二叉搜索树，可用于高效维护快递单数据，主要发挥以下作用：

1. **快速查询**：通过快递单号（orderId）建立索引，支持 O (logN) 时间复杂度的查询操作，比线性扫描 CSV 文件更高效
2. **动态维护**：在快递单新增 / 删除时，能保持树结构平衡，确保增删操作仍为 O (logN) 复杂度
3. **范围查询**：支持按时间范围、状态等条件进行范围查询，例如查询某时间段内的所有快递单
4. **排序功能**：天然支持按快递单号或时间排序，方便展示和统计分析
