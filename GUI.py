# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from db_core import (insert_express_order, query_express_order, update_express_order,
                     join_courier_orders, query_view,update_user ,delete_user, delete_express_order)
from spatial_core import express_spatial_track
from index_core import HashIndex

# 补充导入
from db_core import (insert_express_order, query_express_order, update_express_order,
                     join_courier_orders, query_view, insert_user, query_user)  # 新增insert_user/query_user
from datetime import datetime  # 新增datetime导入

# 导入可视化模块
try:
    from visualization import visualize_track_window
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    def visualize_track_window(track_data):
        messagebox.showwarning("提示", "可视化模块未安装，请先安装matplotlib\n运行: pip install matplotlib")

class ExpressGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("快递管理信息系统")
        self.root.geometry("1200x700")

        # 初始化用户手机号散列索引（用于快速查询）
        self.user_phone_index = HashIndex("User", "uphone")

        # 菜单栏
        self.create_menu()

        # 主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 结果显示表格
        self.init_tree_view()

    # gui.py（修改create_menu函数，新增用户管理菜单）
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 新增用户管理菜单
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="新增用户", command=self.show_add_user)
        user_menu.add_command(label="查询用户", command=self.show_query_user)
        user_menu.add_command(label="修改用户", command=self.show_edit_user)  # 新增
        user_menu.add_command(label="删除用户", command=self.show_delete_user)  # 新增
        menubar.add_cascade(label="用户管理", menu=user_menu)

        # 原有快递管理菜单（不变）
        express_menu = tk.Menu(menubar, tearoff=0)
        express_menu.add_command(label="新增快递单", command=self.show_add_order)
        express_menu.add_command(label="查询快递单", command=self.show_query_order)
        express_menu.add_command(label="修改快递单", command=self.show_edit_order)
        express_menu.add_command(label="删除快递单", command=self.show_delete_order)
        express_menu.add_command(label="查询快递轨迹", command=self.show_query_track)
        express_menu.add_separator()
        express_menu.add_command(label="快递员派送统计", command=self.show_courier_stats)
        express_menu.add_command(label="网点寄件量统计", command=self.show_branch_stats)
        express_menu.add_command(label="手机号前缀查快递", command=self.show_query_order_by_phone_prefix)  # 新增
        menubar.add_cascade(label="快递管理", menu=express_menu)
        # ... 其他菜单不变

    # gui.py（新增新增用户对话框）
    def show_add_user(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新增用户（寄件人/收件人）")
        dialog.geometry("550x400")

        # 表单字段（对应User表的8个字段）
        fields = [
            ("用户ID（uid）", "uid"), ("姓名", "uname"), ("用户类型", "utype"),
            ("手机号", "uphone"), ("省份", "uprovince"), ("城市", "ucity"),
            ("详细地址", "uaddress"), ("身份证号（可选）", "uidcard")
        ]

        var_dict = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            var = tk.StringVar()
            # 用户类型用下拉框
            if key == 'utype':
                ttk.Combobox(dialog, textvariable=var, values=['普通用户', '商家用户', '快递员']).grid(row=i, column=1,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky=tk.EW)
            else:
                ttk.Entry(dialog, textvariable=var).grid(row=i, column=1, padx=10, pady=5, sticky=tk.EW)
            var_dict[key] = var

        def submit():
            user_data = {k: var.get().strip() for k, var in var_dict.items() if var.get().strip()}
            if insert_user(user_data):
                messagebox.showinfo("成功", "用户新增成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "新增失败，请检查字段格式！")

        ttk.Button(dialog, text="提交", command=submit).grid(row=len(fields), column=0, columnspan=2, pady=15)


    def init_tree_view(self):
        """初始化结果显示表格"""
        self.tree = ttk.Treeview(self.main_frame, show="headings", columns=[])
        self.scrollbar_y = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar_x = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # 布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    def update_tree_view(self, data):
        """更新表格数据（data为字典列表）"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not data:
            messagebox.showinfo("提示", "无匹配数据")
            return
        # 设置列名
        columns = list(data[0].keys())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        # 插入数据
        for row in data:
            self.tree.insert("", tk.END, values=[row[col] for col in columns])

    def show_edit_user(self):
        """修改用户对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("修改用户信息")
        dialog.geometry("550x400")

        # 先输入用户ID查询待修改用户
        ttk.Label(dialog, text="用户ID（uid）：").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        uid_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=uid_var).grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        # 存储表单变量的字典
        var_dict = {}
        fields = [
            ("姓名", "uname"), ("用户类型", "utype"), ("手机号", "uphone"),
            ("省份", "uprovince"), ("城市", "ucity"), ("详细地址", "uaddress"), ("身份证号（可选）", "uidcard")
        ]

        # 初始化表单（先禁用，查询到用户后启用）
        for i, (label, key) in enumerate(fields, start=2):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            var = tk.StringVar()
            if key == 'utype':
                widget = ttk.Combobox(dialog, textvariable=var, values=['普通用户', '商家用户', '快递员'],
                                      state="disabled")
            else:
                widget = ttk.Entry(dialog, textvariable=var, state="disabled")
            widget.grid(row=i, column=1, padx=10, pady=5, sticky=tk.EW)
            var_dict[key] = (var, widget)

        # 查询用户信息并填充表单
        def query_user_for_edit():
            uid = uid_var.get().strip()
            if not uid:
                messagebox.showwarning("警告", "请输入用户ID！")
                return
            user = query_user({"uid": uid})
            if not user:
                messagebox.showinfo("提示", "未找到用户")
                # 清空并禁用表单
                for var, widget in var_dict.values():
                    var.set("")
                    widget.config(state="disabled")
                return
            # 填充表单并启用编辑
            user_data = user[0]
            for key, (var, widget) in var_dict.items():
                var.set(user_data.get(key, ""))
                widget.config(state="readonly" if key == 'uid' else "normal")  # uid不可改

        # 提交修改
        def submit_edit():
            uid = uid_var.get().strip()
            if not uid:
                messagebox.showwarning("警告", "请输入用户ID！")
                return
            # 收集修改后的数据
            update_data = {}
            for key, (var, _) in var_dict.items():
                val = var.get().strip()
                if val:
                    update_data[key] = val
            # 调用更新函数
            if update_user(uid, update_data):
                messagebox.showinfo("成功", "用户信息更新成功！")
                # 重建手机号索引（确保查询一致性）
                self.user_phone_index.rebuild()
                dialog.destroy()
            else:
                messagebox.showerror("失败", "更新失败，请检查数据格式！")

        # 按钮布局
        ttk.Button(dialog, text="查询用户", command=query_user_for_edit).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(dialog, text="提交修改", command=submit_edit).grid(row=len(fields) + 2, column=0, columnspan=2,
                                                                      pady=15)

    def show_delete_user(self):
        """删除用户对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("删除用户")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="用户ID（uid）：").grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        uid_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=uid_var).grid(row=0, column=1, padx=10, pady=20, sticky=tk.EW)

        def confirm_delete():
            uid = uid_var.get().strip()
            if not uid:
                messagebox.showwarning("警告", "请输入用户ID！")
                return
            # 二次确认
            if not messagebox.askyesno("确认", f"确定要删除用户 {uid} 吗？\n关联的快递单会导致删除失败！"):
                return
            # 调用删除函数
            if delete_user(uid):
                messagebox.showinfo("成功", "用户删除成功！")
                # 重建手机号索引
                self.user_phone_index.rebuild()
                dialog.destroy()
            else:
                messagebox.showerror("失败", "删除失败（用户不存在或有关联快递单）！")

        ttk.Button(dialog, text="删除", command=confirm_delete).grid(row=1, column=0, columnspan=2, pady=10)

    # -------------------------- 快递单操作对话框 --------------------------
    def show_add_order(self):
        """新增快递单对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("新增快递单")
        dialog.geometry("550x400")

        # 表单字段
        fields = [
            ("快递单号", "orderId"), ("寄件人ID", "senderId"), ("收件人ID", "receiverId"),
            ("物品名称", "goodsName"), ("物品重量(kg)", "goodsWeight"), ("寄件网点ID", "sendBranchId"),
            ("目标网点ID", "targetBranchId"), ("预计送达时间(YYYY-MM-DD HH:MM:SS)", "estimatedTime")
        ]

        var_dict = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            var = tk.StringVar()
            ttk.Entry(dialog, textvariable=var).grid(row=i, column=1, padx=10, pady=5, sticky=tk.EW)
            var_dict[key] = var

        # 提交按钮
        # 提交按钮
        def submit():
            order_data = {k: var.get().strip() for k, var in var_dict.items() if var.get().strip()}
            if insert_express_order(order_data):
                # 新增快递单成功后，自动生成初始轨迹（收件记录）
                order_id = order_data.get('orderId')  # 获取新增的快递单号
                send_branch_id = order_data.get('sendBranchId')  # 获取寄件网点ID
                if order_id and send_branch_id:
                    # 调用轨迹生成函数，创建"收件"类型轨迹（operate_type="0"）
                    from spatial_core import generate_express_track
                    generate_express_track(
                        order_id=order_id,
                        current_branch_id=send_branch_id,
                        operate_type="0",  # 0表示"收件"
                        prev_branch_id=None,  # 收件时无上一网点
                        next_branch_id=None  # 初始收件时下一网点可留空
                    )
                messagebox.showinfo("成功", "快递单新增成功，已自动创建初始轨迹！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "新增失败，请检查必填字段！")

        ttk.Button(dialog, text="提交", command=submit).grid(row=len(fields), column=0, columnspan=2, pady=15)

    def show_query_user(self):
        """查询用户对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("查询用户")
        dialog.geometry("400x200")

        # 按手机号查询（利用哈希索引）
        ttk.Label(dialog, text="手机号：").grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        phone_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=phone_var).grid(row=0, column=1, padx=10, pady=20, sticky=tk.EW)

        def query():
            phone = phone_var.get().strip()
            if not phone:
                messagebox.showwarning("警告", "请输入手机号！")
                return
            # 先通过哈希索引快速定位，再查询详情（示例）
            row_nums = self.user_phone_index.search(phone)
            if not row_nums:
                messagebox.showinfo("提示", "无匹配用户")
                return
            # 调用db_core的query_user
            results = query_user({"uphone": phone})
            self.update_tree_view(results)
            dialog.destroy()

        ttk.Button(dialog, text="查询", command=query).grid(row=1, column=0, columnspan=2, pady=10)
        
    def show_query_order(self):
        """查询快递单对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("查询快递单")
        dialog.geometry("400x300")

        # 查询条件：快递单号、状态、寄件网点
        ttk.Label(dialog, text="快递单号：").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        order_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=order_id_var).grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        ttk.Label(dialog, text="快递状态：").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        status_var = tk.StringVar(value="全部")
        ttk.Combobox(dialog, textvariable=status_var,
                     values=["全部", "0(待收件)", "1(已收件)", "2(中转中)", "3(派送中)", "4(已签收)", "5(异常)"]).grid(
            row=1, column=1, padx=10, pady=10, sticky=tk.EW)

        # 查询按钮
        def query():
            condition = {}
            if order_id_var.get().strip():
                condition['orderId'] = order_id_var.get().strip()
            if status_var.get() != "全部":
                condition['orderStatus'] = status_var.get().split('(')[0]
            # 执行查询
            results = query_express_order(condition, use_index=True)
            self.update_tree_view(results)
            dialog.destroy()

        ttk.Button(dialog, text="查询", command=query).grid(row=2, column=0, columnspan=2, pady=15)

    def show_query_track(self):
        """查询快递轨迹对话框（新增可视化按钮）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("查询快递轨迹")
        dialog.geometry("400x200")

        ttk.Label(dialog, text="快递单号：").grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        order_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=order_id_var).grid(row=0, column=1, padx=10, pady=20, sticky=tk.EW)

        def query_text():
            """查询文本轨迹"""
            order_id = order_id_var.get().strip()
            if not order_id:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            # 查询空间轨迹
            track_data = express_spatial_track(order_id)
            self.update_tree_view(track_data)
            dialog.destroy()

        def query_visual():
            """查询并可视化轨迹"""
            order_id = order_id_var.get().strip()
            if not order_id:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            # 查询轨迹数据
            track_data = express_spatial_track(order_id)
            if not track_data:
                messagebox.showinfo("提示", "无轨迹数据")
                return
            # 调用可视化函数
            visualize_track_window(track_data)
            dialog.destroy()

        # 按钮布局：文本查询 + 可视化查询
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="文本查询", command=query_text).pack(side=tk.LEFT, padx=10)
        
        if VISUALIZATION_AVAILABLE:
            ttk.Button(button_frame, text="🗺️ 可视化轨迹", command=query_visual).pack(side=tk.LEFT, padx=10)
        else:
            ttk.Label(button_frame, text="(需安装matplotlib)", foreground="gray").pack(side=tk.LEFT, padx=10)

    def show_edit_order(self):
        """修改快递单对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("修改快递单信息")
        dialog.geometry("550x400")

        # 1. 输入快递单号查询
        ttk.Label(dialog, text="快递单号：").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        order_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=order_id_var).grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        # 2. 定义表单字段（排除不可修改的字段，如寄件时间）
        fields = [
            ("寄件人ID", "senderId"), ("收件人ID", "receiverId"),
            ("物品名称", "goodsName"), ("物品重量(kg)", "goodsWeight"),
            ("寄件网点ID", "sendBranchId"), ("目标网点ID", "targetBranchId"),
            ("预计送达时间", "estimatedTime"), ("订单状态", "orderStatus")
        ]
        var_dict = {}  # 存储表单变量和控件

        # 3. 初始化表单（先禁用，查询到后启用）
        for i, (label, key) in enumerate(fields, start=2):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            var = tk.StringVar()
            if key == "orderStatus":
                # 状态使用下拉框（限制合法值）
                widget = ttk.Combobox(
                    dialog,
                    textvariable=var,
                    values=["0(待收件)", "1(已收件)", "2(中转中)", "3(派送中)", "4(已签收)", "5(异常)"],
                    state="disabled"
                )
            else:
                widget = ttk.Entry(dialog, textvariable=var, state="disabled")
            widget.grid(row=i, column=1, padx=10, pady=5, sticky=tk.EW)
            var_dict[key] = (var, widget)

        # 4. 查询快递单并填充表单
        def query_order_for_edit():
            order_id = order_id_var.get().strip()
            if not order_id:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            # 调用查询函数
            orders = query_express_order({"orderId": order_id})
            if not orders:
                messagebox.showinfo("提示", "未找到快递单")
                # 清空并禁用表单
                for var, widget in var_dict.values():
                    var.set("")
                    widget.config(state="disabled")
                return
            # 填充表单并启用编辑

            order_data = orders[0]
            for key, (var, widget) in var_dict.items():
                # 状态显示处理（如"0" -> "0(待收件)"）
                if key == "orderStatus":
                    status_text = next(
                        (v for v in ["0(待收件)", "1(已收件)", "2(中转中)", "3(派送中)", "4(已签收)", "5(异常)"] if
                         v.startswith(order_data.get(key, ""))), "")
                    var.set(status_text)
                else:
                    var.set(order_data.get(key, ""))
                widget.config(state="normal")  # 启用编辑

            # 在query_order_for_edit函数中添加调试打印
            print("查询的快递单号：", order_id)
            print("查询结果：", orders)

        # 5. 提交修改
        def submit_edit():
            order_id = order_id_var.get().strip()
            if not order_id:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            # 收集修改后的数据（处理状态值，提取数字部分）
            update_data = {}
            for key, (var, _) in var_dict.items():
                val = var.get().strip()
                if not val:
                    continue
                if key == "orderStatus":
                    # 从"0(待收件)"中提取"0"
                    update_data[key] = val.split("(")[0]
                else:
                    update_data[key] = val
            # 调用更新函数
            if update_express_order(order_id, update_data):
                messagebox.showinfo("成功", "快递单更新成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "更新失败（可能状态流转不合法）！")

        # 6. 按钮布局
        ttk.Button(dialog, text="查询快递单", command=query_order_for_edit).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(dialog, text="提交修改", command=submit_edit).grid(row=len(fields) + 2, column=0, columnspan=2,
                                                                      pady=15)

    def show_delete_order(self):
        """删除快递单对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("删除快递单")
        dialog.geometry("300x150")

        # 输入快递单号
        ttk.Label(dialog, text="快递单号：").grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        order_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=order_id_var).grid(row=0, column=1, padx=10, pady=20, sticky=tk.EW)

        def confirm_delete():
            order_id = order_id_var.get().strip()
            if not order_id:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            # 二次确认
            if not messagebox.askyesno("确认", f"确定要删除快递单 {order_id} 吗？\n关联的轨迹记录可能残留！"):
                return
            # 调用删除函数
            if delete_express_order(order_id):
                messagebox.showinfo("成功", "快递单删除成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "删除失败（快递单不存在或已被删除）！")

        # 删除按钮
        ttk.Button(dialog, text="删除", command=confirm_delete).grid(row=1, column=0, columnspan=2, pady=10)


    def show_query_order_by_phone_prefix(self):
        """通过手机号前缀查询快递单"""
        dialog = tk.Toplevel(self.root)
        dialog.title("手机号前缀查询快递单")
        dialog.geometry("400x200")

        ttk.Label(dialog, text="手机号前缀：").grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        prefix_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=prefix_var).grid(row=0, column=1, padx=10, pady=20, sticky=tk.EW)

        def query():
            prefix = prefix_var.get().strip()
            if not prefix or not prefix.isdigit():
                messagebox.showwarning("警告", "请输入有效的手机号前缀！")
                return

            # 加载或构建Trie索引
            from trie_index import PhoneTrieIndex
            trie_index = PhoneTrieIndex()
            if not trie_index.load():
                trie_index.build()

            # 查询匹配的快递单ID
            order_ids = trie_index.search_prefix(prefix)
            if not order_ids:
                messagebox.showinfo("提示", "无匹配的快递单")
                return

            # 查询快递单详情并显示
            from db_core import query_express_order
            results = []
            for order_id in order_ids:
                orders = query_express_order({"orderId": order_id})
                results.extend(orders)
            self.update_tree_view(results)
            dialog.destroy()

        ttk.Button(dialog, text="查询", command=query).grid(row=1, column=0, columnspan=2, pady=10)

    # -------------------------- 统计分析功能 --------------------------
    def show_courier_stats(self):
        """快递员派送统计对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("快递员派送统计")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="快递员ID：").grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        courier_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=courier_id_var).grid(row=0, column=1, padx=10, pady=20, sticky=tk.EW)

        def query():
            courier_id = courier_id_var.get().strip()
            if not courier_id:
                messagebox.showwarning("警告", "请输入快递员ID！")
                return
            # 查询今日派送记录（默认今日，可扩展日期选择）
            today = datetime.now().strftime("%Y-%m-%d")
            stats_data = join_courier_orders(courier_id, today)
            self.update_tree_view(stats_data)
            dialog.destroy()

        ttk.Button(dialog, text="查询", command=query).grid(row=1, column=0, columnspan=2, pady=10)

    def show_branch_stats(self):
        """网点寄件量统计（视图查询）"""
        stats_data = query_view("BranchMonthlySend")
        self.update_tree_view(stats_data)
