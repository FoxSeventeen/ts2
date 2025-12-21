# gui.py - 美化版
import tkinter as tk
from tkinter import ttk, messagebox
from db_core import (insert_express_order, query_express_order, update_express_order,
                     join_courier_orders, query_view, update_user, delete_user, delete_express_order,
                     insert_user, query_user,
                     insert_courier, query_courier, update_courier, delete_courier)
from spatial_core import express_spatial_track
from index_core import HashIndex
from datetime import datetime

# 导入可视化模块
try:
    from visualization import visualize_track_window
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    def visualize_track_window(track_data):
        messagebox.showwarning("提示", "可视化模块未安装，请先安装matplotlib\n运行: pip install matplotlib")


# ==================== 主题和样式配置 ====================
class ThemeConfig:
    """主题配置类"""
    # 主色调
    PRIMARY_COLOR = "#2563eb"       # 蓝色主色
    PRIMARY_DARK = "#1d4ed8"        # 深蓝色
    PRIMARY_LIGHT = "#3b82f6"       # 浅蓝色
    
    # 功能色
    SUCCESS_COLOR = "#10b981"       # 绿色-成功
    WARNING_COLOR = "#f59e0b"       # 橙色-警告
    DANGER_COLOR = "#ef4444"        # 红色-危险
    INFO_COLOR = "#06b6d4"          # 青色-信息
    
    # 中性色
    BG_COLOR = "#f8fafc"            # 背景色
    CARD_BG = "#ffffff"             # 卡片背景
    BORDER_COLOR = "#e2e8f0"        # 边框色
    TEXT_PRIMARY = "#1e293b"        # 主文字
    TEXT_SECONDARY = "#64748b"      # 次要文字
    TEXT_MUTED = "#94a3b8"          # 淡化文字
    
    # 表格颜色
    TABLE_HEADER_BG = "#f1f5f9"
    TABLE_ROW_ODD = "#ffffff"
    TABLE_ROW_EVEN = "#f8fafc"
    TABLE_SELECT = "#dbeafe"
    
    # 字体
    FONT_FAMILY = "Microsoft YaHei UI"
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_TITLE = 16
    FONT_SIZE_HEADER = 24


def setup_styles():
    """配置ttk样式"""
    style = ttk.Style()
    
    # 尝试使用clam主题作为基础
    try:
        style.theme_use('clam')
    except:
        pass
    
    # 配置通用样式
    style.configure(".", 
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                    background=ThemeConfig.BG_COLOR)
    
    # 主框架样式
    style.configure("Main.TFrame", background=ThemeConfig.BG_COLOR)
    style.configure("Card.TFrame", background=ThemeConfig.CARD_BG, relief="flat")
    
    # 标签样式
    style.configure("TLabel", 
                    background=ThemeConfig.CARD_BG,
                    foreground=ThemeConfig.TEXT_PRIMARY,
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL))
    
    style.configure("Title.TLabel",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_HEADER, "bold"),
                    foreground=ThemeConfig.PRIMARY_COLOR,
                    background=ThemeConfig.CARD_BG)
    
    style.configure("Subtitle.TLabel",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE),
                    foreground=ThemeConfig.TEXT_SECONDARY,
                    background=ThemeConfig.CARD_BG)
    
    style.configure("Header.TLabel",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_LARGE, "bold"),
                    foreground=ThemeConfig.TEXT_PRIMARY,
                    background=ThemeConfig.CARD_BG)
    
    style.configure("Muted.TLabel",
                    foreground=ThemeConfig.TEXT_MUTED,
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL))
    
    # 按钮样式
    style.configure("TButton",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                    padding=(20, 10))
    
    style.configure("Primary.TButton",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL, "bold"))
    
    style.configure("Success.TButton",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL))
    
    style.configure("Danger.TButton",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL))
    
    # 输入框样式
    style.configure("TEntry",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                    padding=8)
    
    # 下拉框样式
    style.configure("TCombobox",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                    padding=8)
    
    # 表格样式
    style.configure("Treeview",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                    rowheight=32,
                    background=ThemeConfig.TABLE_ROW_ODD,
                    fieldbackground=ThemeConfig.TABLE_ROW_ODD,
                    foreground=ThemeConfig.TEXT_PRIMARY)
    
    style.configure("Treeview.Heading",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL, "bold"),
                    background=ThemeConfig.TABLE_HEADER_BG,
                    foreground=ThemeConfig.TEXT_PRIMARY,
                    padding=10)
    
    style.map("Treeview",
              background=[("selected", ThemeConfig.TABLE_SELECT)],
              foreground=[("selected", ThemeConfig.PRIMARY_COLOR)])
    
    # LabelFrame样式
    style.configure("TLabelframe",
                    background=ThemeConfig.CARD_BG,
                    foreground=ThemeConfig.TEXT_PRIMARY)
    
    style.configure("TLabelframe.Label",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL, "bold"),
                    foreground=ThemeConfig.PRIMARY_COLOR,
                    background=ThemeConfig.CARD_BG)
    
    # Notebook样式
    style.configure("TNotebook",
                    background=ThemeConfig.BG_COLOR)
    
    style.configure("TNotebook.Tab",
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                    padding=(20, 10))


# ==================== 自定义组件 ====================
class ModernButton(tk.Button):
    """现代风格按钮"""
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        # 根据样式设置颜色
        colors = {
            "primary": (ThemeConfig.PRIMARY_COLOR, "#ffffff", ThemeConfig.PRIMARY_DARK),
            "success": (ThemeConfig.SUCCESS_COLOR, "#ffffff", "#059669"),
            "danger": (ThemeConfig.DANGER_COLOR, "#ffffff", "#dc2626"),
            "warning": (ThemeConfig.WARNING_COLOR, "#ffffff", "#d97706"),
            "secondary": (ThemeConfig.BORDER_COLOR, ThemeConfig.TEXT_PRIMARY, "#cbd5e1"),
        }
        
        bg, fg, hover_bg = colors.get(style, colors["primary"])
        
        super().__init__(parent, 
                        text=text,
                        command=command,
                        font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                        bg=bg,
                        fg=fg,
                        activebackground=hover_bg,
                        activeforeground=fg,
                        relief="flat",
                        cursor="hand2",
                        padx=20,
                        pady=8,
                        **kwargs)
        
        self.default_bg = bg
        self.hover_bg = hover_bg
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, e):
        self.configure(bg=self.default_bg)


class IconLabel(ttk.Label):
    """带图标的标签"""
    ICONS = {
        "user": "👤",
        "users": "👥",
        "courier": "🚚",
        "package": "📦",
        "search": "🔍",
        "add": "➕",
        "edit": "✏️",
        "delete": "🗑️",
        "chart": "📊",
        "track": "📍",
        "success": "✅",
        "warning": "⚠️",
        "info": "ℹ️",
        "tip": "💡",
    }
    
    def __init__(self, parent, icon, text, **kwargs):
        icon_char = self.ICONS.get(icon, "")
        super().__init__(parent, text=f"{icon_char} {text}", **kwargs)


# ==================== 主界面类 ====================
class ExpressGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 快递管理信息系统")
        self.root.geometry("1300x800")
        self.root.minsize(1000, 600)
        
        # 设置窗口背景色
        self.root.configure(bg=ThemeConfig.BG_COLOR)
        
        # 配置样式
        setup_styles()
        
        # 初始化用户手机号散列索引
        self.user_phone_index = HashIndex("User", "uphone")
        
        # 创建主布局
        self.create_layout()
        
        # 创建菜单栏
        self.create_menu()
        
        # 显示欢迎信息
        self.show_welcome()
    
    def create_layout(self):
        """创建主布局"""
        # 顶部标题栏
        self.header_frame = tk.Frame(self.root, bg=ThemeConfig.CARD_BG, height=80)
        self.header_frame.pack(fill=tk.X, padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        # 标题
        title_container = tk.Frame(self.header_frame, bg=ThemeConfig.CARD_BG)
        title_container.pack(side=tk.LEFT, padx=30, pady=15)
        
        tk.Label(title_container, 
                text="📦 快递管理信息系统",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_HEADER, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(anchor="w")
        
        tk.Label(title_container,
                text="Express Management System",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                fg=ThemeConfig.TEXT_MUTED,
                bg=ThemeConfig.CARD_BG).pack(anchor="w")
        
        # 右侧信息
        info_frame = tk.Frame(self.header_frame, bg=ThemeConfig.CARD_BG)
        info_frame.pack(side=tk.RIGHT, padx=30, pady=15)
        
        self.time_label = tk.Label(info_frame,
                                   text="",
                                   font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                                   fg=ThemeConfig.TEXT_SECONDARY,
                                   bg=ThemeConfig.CARD_BG)
        self.time_label.pack(anchor="e")
        self.update_time()
        
        # 分割线
        separator = tk.Frame(self.root, height=1, bg=ThemeConfig.BORDER_COLOR)
        separator.pack(fill=tk.X)
        
        # 工具栏
        self.toolbar_frame = tk.Frame(self.root, bg=ThemeConfig.BG_COLOR, height=60)
        self.toolbar_frame.pack(fill=tk.X, padx=20, pady=10)
        self.create_toolbar()
        
        # 主内容区
        self.content_frame = tk.Frame(self.root, bg=ThemeConfig.BG_COLOR)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # 左侧功能面板
        self.sidebar_frame = tk.Frame(self.content_frame, bg=ThemeConfig.CARD_BG, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        self.sidebar_frame.pack_propagate(False)
        self.create_sidebar()
        
        # 右侧主内容
        self.main_frame = tk.Frame(self.content_frame, bg=ThemeConfig.CARD_BG)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 初始化表格
        self.init_tree_view()
        
        # 状态栏
        self.status_frame = tk.Frame(self.root, bg=ThemeConfig.TABLE_HEADER_BG, height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(self.status_frame,
                                     text="✅ 系统就绪",
                                     font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                                     fg=ThemeConfig.TEXT_SECONDARY,
                                     bg=ThemeConfig.TABLE_HEADER_BG)
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.record_count_label = tk.Label(self.status_frame,
                                           text="",
                                           font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                                           fg=ThemeConfig.TEXT_SECONDARY,
                                           bg=ThemeConfig.TABLE_HEADER_BG)
        self.record_count_label.pack(side=tk.RIGHT, padx=15, pady=5)
    
    def update_time(self):
        """更新时间显示"""
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        self.time_label.config(text=f"🕐 {now}")
        self.root.after(1000, self.update_time)
    
    def create_toolbar(self):
        """创建工具栏"""
        # 快捷按钮
        buttons = [
            ("👤 新增用户", self.show_add_user),
            ("🚚 新增快递员", self.show_add_courier),
            ("📦 新增快递单", self.show_add_order),
            ("🔍 查询快递", self.show_query_order),
            ("📍 查询轨迹", self.show_query_track),
            ("📊 统计分析", self.show_branch_stats),
        ]
        
        for text, command in buttons:
            btn = ModernButton(self.toolbar_frame, text=text, command=command, style="secondary")
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_sidebar(self):
        """创建侧边栏"""
        # 标题
        tk.Label(self.sidebar_frame,
                text="功能导航",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_LARGE, "bold"),
                fg=ThemeConfig.TEXT_PRIMARY,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15), padx=15, anchor="w")
        
        # 分割线
        tk.Frame(self.sidebar_frame, height=1, bg=ThemeConfig.BORDER_COLOR).pack(fill=tk.X, padx=15)
        
        # 功能分类
        categories = [
            ("👥 用户管理", [
                ("新增用户", self.show_add_user),
                ("查询用户", self.show_query_user),
                ("修改用户", self.show_edit_user),
                ("删除用户", self.show_delete_user),
            ]),
            ("🚚 快递员管理", [
                ("新增快递员", self.show_add_courier),
                ("查询快递员", self.show_query_courier),
                ("修改快递员", self.show_edit_courier),
                ("删除快递员", self.show_delete_courier),
            ]),
            ("📦 快递管理", [
                ("新增快递单", self.show_add_order),
                ("查询快递单", self.show_query_order),
                ("修改快递单", self.show_edit_order),
                ("删除快递单", self.show_delete_order),
                ("查询轨迹", self.show_query_track),
            ]),
            ("📊 统计分析", [
                ("网点寄件量", self.show_branch_stats),
            ]),
        ]
        
        for cat_name, items in categories:
            # 分类标题
            tk.Label(self.sidebar_frame,
                    text=cat_name,
                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL, "bold"),
                    fg=ThemeConfig.PRIMARY_COLOR,
                    bg=ThemeConfig.CARD_BG).pack(pady=(15, 5), padx=15, anchor="w")
            
            # 功能项
            for item_name, command in items:
                btn = tk.Label(self.sidebar_frame,
                              text=f"  • {item_name}",
                              font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                              fg=ThemeConfig.TEXT_SECONDARY,
                              bg=ThemeConfig.CARD_BG,
                              cursor="hand2")
                btn.pack(anchor="w", padx=15, pady=2)
                btn.bind("<Button-1>", lambda e, cmd=command: cmd())
                btn.bind("<Enter>", lambda e, b=btn: b.configure(fg=ThemeConfig.PRIMARY_COLOR))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(fg=ThemeConfig.TEXT_SECONDARY))
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root, 
                         font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                         bg=ThemeConfig.CARD_BG)
        self.root.config(menu=menubar)
        
        # 用户管理菜单
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="👤 新增用户", command=self.show_add_user)
        user_menu.add_command(label="🔍 查询用户", command=self.show_query_user)
        user_menu.add_command(label="✏️ 修改用户", command=self.show_edit_user)
        user_menu.add_command(label="🗑️ 删除用户", command=self.show_delete_user)
        menubar.add_cascade(label="👥 用户管理", menu=user_menu)
        
        # 快递员管理菜单
        courier_menu = tk.Menu(menubar, tearoff=0)
        courier_menu.add_command(label="👤 新增快递员", command=self.show_add_courier)
        courier_menu.add_command(label="🔍 查询快递员", command=self.show_query_courier)
        courier_menu.add_command(label="✏️ 修改快递员", command=self.show_edit_courier)
        courier_menu.add_command(label="🗑️ 删除快递员", command=self.show_delete_courier)
        menubar.add_cascade(label="🚚 快递员管理", menu=courier_menu)
        
        # 快递管理菜单
        express_menu = tk.Menu(menubar, tearoff=0)
        express_menu.add_command(label="📦 新增快递单", command=self.show_add_order)
        express_menu.add_command(label="🔍 查询快递单", command=self.show_query_order)
        express_menu.add_command(label="✏️ 修改快递单", command=self.show_edit_order)
        express_menu.add_command(label="🗑️ 删除快递单", command=self.show_delete_order)
        express_menu.add_separator()
        express_menu.add_command(label="📍 查询快递轨迹", command=self.show_query_track)
        express_menu.add_separator()
        express_menu.add_command(label="📊 网点寄件量统计", command=self.show_branch_stats)
        menubar.add_cascade(label="📦 快递管理", menu=express_menu)
    
    def show_welcome(self):
        """显示欢迎信息"""
        # 清空现有内容
        for widget in self.main_frame.winfo_children():
            if widget != getattr(self, 'tree', None) and widget != getattr(self, 'scrollbar_y', None):
                pass  # 保留表格
        
        self.set_status("欢迎使用快递管理信息系统")
    
    def init_tree_view(self):
        """初始化结果显示表格"""
        # 表格容器
        tree_container = tk.Frame(self.main_frame, bg=ThemeConfig.CARD_BG)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 表格标题
        self.table_title = tk.Label(tree_container,
                                    text="📋 数据列表",
                                    font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_LARGE, "bold"),
                                    fg=ThemeConfig.TEXT_PRIMARY,
                                    bg=ThemeConfig.CARD_BG)
        self.table_title.pack(anchor="w", pady=(0, 10))
        
        # 表格框架
        table_frame = tk.Frame(tree_container, bg=ThemeConfig.BORDER_COLOR)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 内部框架（用于边框效果）
        inner_frame = tk.Frame(table_frame, bg=ThemeConfig.CARD_BG)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # 表格
        self.tree = ttk.Treeview(inner_frame, show="headings", columns=[])
        self.scrollbar_y = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar_x = ttk.Scrollbar(inner_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        # 布局
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def update_tree_view(self, data):
        """更新表格数据"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not data:
            self.set_status("⚠️ 无匹配数据")
            self.record_count_label.config(text="共 0 条记录")
            messagebox.showinfo("提示", "无匹配数据")
            return
        
        # 设置列名
        columns = list(data[0].keys())
        self.tree["columns"] = columns
        
        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            # 根据列名设置宽度
            width = max(len(col) * 15, 100)
            self.tree.column(col, width=width, anchor="center")
        
        # 插入数据（交替行颜色）
        for i, row in enumerate(data):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", tk.END, values=[row[col] for col in columns], tags=(tag,))
        
        # 设置交替行颜色
        self.tree.tag_configure("odd", background=ThemeConfig.TABLE_ROW_ODD)
        self.tree.tag_configure("even", background=ThemeConfig.TABLE_ROW_EVEN)
        
        # 更新状态
        self.set_status(f"✅ 查询完成，共 {len(data)} 条记录")
        self.record_count_label.config(text=f"共 {len(data)} 条记录")
    
    def set_status(self, message):
        """设置状态栏消息"""
        self.status_label.config(text=message)
    
    # ==================== 对话框基类方法 ====================
    def create_dialog(self, title, width=500, height=400):
        """创建统一风格的对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.configure(bg=ThemeConfig.CARD_BG)
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 计算居中位置
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        return dialog
    
    def create_form_field(self, parent, row, label_text, var, field_type="entry", 
                          values=None, state="normal"):
        """创建表单字段"""
        # 标签
        label = tk.Label(parent,
                        text=label_text,
                        font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_NORMAL),
                        fg=ThemeConfig.TEXT_PRIMARY,
                        bg=ThemeConfig.CARD_BG)
        label.grid(row=row, column=0, padx=(20, 10), pady=8, sticky=tk.W)
        
        # 输入控件
        if field_type == "combobox":
            widget = ttk.Combobox(parent, textvariable=var, values=values or [], 
                                 state=state, width=30)
        else:
            widget = ttk.Entry(parent, textvariable=var, width=32, state=state)
        
        widget.grid(row=row, column=1, padx=(0, 20), pady=8, sticky=tk.EW)
        
        return widget
    
    # ==================== 用户管理对话框 ====================
    def show_add_user(self):
        """新增用户对话框"""
        dialog = self.create_dialog("👤 新增用户", 550, 480)
        
        # 标题
        tk.Label(dialog,
                text="新增用户",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 5))
        
        tk.Label(dialog,
                text="请填写用户基本信息",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                fg=ThemeConfig.TEXT_MUTED,
                bg=ThemeConfig.CARD_BG).pack(pady=(0, 15))
        
        # 表单区域
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        fields = [
            ("用户ID", "uid", "entry"),
            ("姓名", "uname", "entry"),
            ("用户类型", "utype", "combobox"),
            ("手机号", "uphone", "entry"),
            ("省份", "uprovince", "entry"),
            ("城市", "ucity", "entry"),
            ("详细地址", "uaddress", "entry"),
            ("身份证号（可选）", "uidcard", "entry"),
        ]
        
        var_dict = {}
        for i, (label, key, field_type) in enumerate(fields):
            var = tk.StringVar()
            values = ['普通用户', '商家用户'] if key == 'utype' else None
            self.create_form_field(form_frame, i, label, var, field_type, values)
            var_dict[key] = var
        
        # 提示
        tk.Label(dialog,
                text="💡 快递员请在「快递员管理」菜单中添加",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                fg=ThemeConfig.TEXT_MUTED,
                bg=ThemeConfig.CARD_BG).pack(pady=10)
        
        # 按钮区域
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=20)
        
        def submit():
            user_data = {k: var.get().strip() for k, var in var_dict.items() if var.get().strip()}
            if insert_user(user_data):
                messagebox.showinfo("成功", "✅ 用户新增成功！")
                self.set_status("✅ 用户新增成功")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 新增失败，请检查字段格式！")
        
        ModernButton(btn_frame, text="确认提交", command=submit, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_query_user(self):
        """查询用户对话框"""
        dialog = self.create_dialog("🔍 查询用户", 450, 250)
        
        # 标题
        tk.Label(dialog,
                text="查询用户",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 5))
        
        tk.Label(dialog,
                text="请输入手机号进行查询",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                fg=ThemeConfig.TEXT_MUTED,
                bg=ThemeConfig.CARD_BG).pack(pady=(0, 20))
        
        # 表单
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.X, padx=40)
        
        phone_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "手机号", phone_var)
        
        # 按钮
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=30)
        
        def query():
            phone = phone_var.get().strip()
            if not phone:
                messagebox.showwarning("警告", "请输入手机号！")
                return
            results = query_user({"uphone": phone})
            self.update_tree_view(results)
            dialog.destroy()
        
        ModernButton(btn_frame, text="查询", command=query, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_edit_user(self):
        """修改用户对话框"""
        dialog = self.create_dialog("✏️ 修改用户", 550, 520)
        
        # 标题
        tk.Label(dialog,
                text="修改用户信息",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        # 表单
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        uid_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "用户ID", uid_var)
        
        fields = [
            ("姓名", "uname"), ("用户类型", "utype"), ("手机号", "uphone"),
            ("省份", "uprovince"), ("城市", "ucity"), ("详细地址", "uaddress"), 
            ("身份证号", "uidcard")
        ]
        
        var_dict = {}
        widgets = {}
        for i, (label, key) in enumerate(fields, start=2):
            var = tk.StringVar()
            field_type = "combobox" if key == 'utype' else "entry"
            values = ['普通用户', '商家用户'] if key == 'utype' else None
            widget = self.create_form_field(form_frame, i, label, var, field_type, values, state="disabled")
            var_dict[key] = var
            widgets[key] = widget
        
        def query_user_for_edit():
            uid = uid_var.get().strip()
            if not uid:
                messagebox.showwarning("警告", "请输入用户ID！")
                return
            user = query_user({"uid": uid})
            if not user:
                messagebox.showinfo("提示", "未找到用户")
                for var in var_dict.values():
                    var.set("")
                for widget in widgets.values():
                    widget.config(state="disabled")
                return
            user_data = user[0]
            for key, var in var_dict.items():
                var.set(user_data.get(key, ""))
                widgets[key].config(state="normal" if key != 'utype' else "readonly")
        
        def submit_edit():
            uid = uid_var.get().strip()
            if not uid:
                messagebox.showwarning("警告", "请输入用户ID！")
                return
            update_data = {k: v.get().strip() for k, v in var_dict.items() if v.get().strip()}
            if update_user(uid, update_data):
                messagebox.showinfo("成功", "✅ 用户信息更新成功！")
                self.user_phone_index.rebuild()
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 更新失败！")
        
        # 按钮
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=15)
        
        ModernButton(btn_frame, text="查询用户", command=query_user_for_edit, style="secondary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="提交修改", command=submit_edit, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_delete_user(self):
        """删除用户对话框"""
        dialog = self.create_dialog("🗑️ 删除用户", 400, 200)
        
        # 标题
        tk.Label(dialog,
                text="删除用户",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.DANGER_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        # 表单
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.X, padx=40)
        
        uid_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "用户ID", uid_var)
        
        def confirm_delete():
            uid = uid_var.get().strip()
            if not uid:
                messagebox.showwarning("警告", "请输入用户ID！")
                return
            if not messagebox.askyesno("确认", f"确定要删除用户 {uid} 吗？"):
                return
            if delete_user(uid):
                messagebox.showinfo("成功", "✅ 用户删除成功！")
                self.user_phone_index.rebuild()
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 删除失败！")
        
        # 按钮
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=20)
        
        ModernButton(btn_frame, text="确认删除", command=confirm_delete, style="danger").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    # ==================== 快递员管理对话框 ====================
    def show_add_courier(self):
        """新增快递员对话框"""
        dialog = self.create_dialog("🚚 新增快递员", 550, 380)
        
        tk.Label(dialog,
                text="新增快递员",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 5))
        
        tk.Label(dialog,
                text="请填写快递员基本信息",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                fg=ThemeConfig.TEXT_MUTED,
                bg=ThemeConfig.CARD_BG).pack(pady=(0, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        fields = [
            ("快递员ID", "courierId"),
            ("姓名", "courierName"),
            ("手机号", "courierPhone"),
            ("所属网点ID", "branchId"),
            ("身份证号（可选）", "courierIdCard"),
        ]
        
        var_dict = {}
        for i, (label, key) in enumerate(fields):
            var = tk.StringVar()
            self.create_form_field(form_frame, i, label, var)
            var_dict[key] = var
        
        tk.Label(dialog,
                text="💡 网点ID需在ExpressBranch表中存在",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_SMALL),
                fg=ThemeConfig.TEXT_MUTED,
                bg=ThemeConfig.CARD_BG).pack(pady=10)
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=15)
        
        def submit():
            courier_data = {k: var.get().strip() for k, var in var_dict.items() if var.get().strip()}
            if insert_courier(courier_data):
                messagebox.showinfo("成功", "✅ 快递员新增成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 新增失败，请检查字段！")
        
        ModernButton(btn_frame, text="确认提交", command=submit, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_query_courier(self):
        """查询快递员对话框"""
        dialog = self.create_dialog("🔍 查询快递员", 450, 320)
        
        tk.Label(dialog,
                text="查询快递员",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.X, padx=40)
        
        courier_id_var = tk.StringVar()
        phone_var = tk.StringVar()
        branch_var = tk.StringVar()
        
        self.create_form_field(form_frame, 0, "快递员ID", courier_id_var)
        self.create_form_field(form_frame, 1, "手机号", phone_var)
        self.create_form_field(form_frame, 2, "网点ID", branch_var)
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=30)
        
        def query():
            condition = {}
            if courier_id_var.get().strip():
                condition['courierId'] = courier_id_var.get().strip()
            if phone_var.get().strip():
                condition['courierPhone'] = phone_var.get().strip()
            if branch_var.get().strip():
                condition['branchId'] = branch_var.get().strip()
            results = query_courier(condition if condition else None)
            self.update_tree_view(results)
            dialog.destroy()
        
        ModernButton(btn_frame, text="查询", command=query, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_edit_courier(self):
        """修改快递员对话框"""
        dialog = self.create_dialog("✏️ 修改快递员", 550, 420)
        
        tk.Label(dialog,
                text="修改快递员信息",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        courier_id_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "快递员ID", courier_id_var)
        
        fields = [
            ("姓名", "courierName"),
            ("手机号", "courierPhone"),
            ("所属网点ID", "branchId"),
            ("身份证号", "courierIdCard"),
        ]
        
        var_dict = {}
        widgets = {}
        for i, (label, key) in enumerate(fields, start=2):
            var = tk.StringVar()
            widget = self.create_form_field(form_frame, i, label, var, state="disabled")
            var_dict[key] = var
            widgets[key] = widget
        
        def query_for_edit():
            cid = courier_id_var.get().strip()
            if not cid:
                messagebox.showwarning("警告", "请输入快递员ID！")
                return
            couriers = query_courier({"courierId": cid})
            if not couriers:
                messagebox.showinfo("提示", "未找到快递员")
                for var in var_dict.values():
                    var.set("")
                for widget in widgets.values():
                    widget.config(state="disabled")
                return
            data = couriers[0]
            for key, var in var_dict.items():
                var.set(data.get(key, ""))
                widgets[key].config(state="normal")
        
        def submit_edit():
            cid = courier_id_var.get().strip()
            if not cid:
                messagebox.showwarning("警告", "请输入快递员ID！")
                return
            update_data = {k: v.get().strip() for k, v in var_dict.items() if v.get().strip()}
            if update_courier(cid, update_data):
                messagebox.showinfo("成功", "✅ 快递员信息更新成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 更新失败！")
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=15)
        
        ModernButton(btn_frame, text="查询", command=query_for_edit, style="secondary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="提交修改", command=submit_edit, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_delete_courier(self):
        """删除快递员对话框"""
        dialog = self.create_dialog("🗑️ 删除快递员", 400, 200)
        
        tk.Label(dialog,
                text="删除快递员",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.DANGER_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.X, padx=40)
        
        courier_id_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "快递员ID", courier_id_var)
        
        def confirm_delete():
            cid = courier_id_var.get().strip()
            if not cid:
                messagebox.showwarning("警告", "请输入快递员ID！")
                return
            if not messagebox.askyesno("确认", f"确定要删除快递员 {cid} 吗？"):
                return
            if delete_courier(cid):
                messagebox.showinfo("成功", "✅ 快递员删除成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 删除失败！")
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=20)
        
        ModernButton(btn_frame, text="确认删除", command=confirm_delete, style="danger").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    # ==================== 快递单管理对话框 ====================
    def show_add_order(self):
        """新增快递单对话框"""
        dialog = self.create_dialog("📦 新增快递单", 550, 480)
        
        tk.Label(dialog,
                text="新增快递单",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        fields = [
            ("快递单号", "orderId"),
            ("寄件人ID", "senderId"),
            ("收件人ID", "receiverId"),
            ("物品名称", "goodsName"),
            ("物品重量(kg)", "goodsWeight"),
            ("寄件网点ID", "sendBranchId"),
            ("目标网点ID", "targetBranchId"),
            ("预计送达时间", "estimatedTime"),
        ]
        
        var_dict = {}
        for i, (label, key) in enumerate(fields):
            var = tk.StringVar()
            self.create_form_field(form_frame, i, label, var)
            var_dict[key] = var
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=20)
        
        def submit():
            order_data = {k: var.get().strip() for k, var in var_dict.items() if var.get().strip()}
            if insert_express_order(order_data):
                order_id = order_data.get('orderId')
                send_branch_id = order_data.get('sendBranchId')
                if order_id and send_branch_id:
                    from spatial_core import generate_express_track
                    generate_express_track(
                        order_id=order_id,
                        current_branch_id=send_branch_id,
                        operate_type="0",
                        prev_branch_id=None,
                        next_branch_id=None
                    )
                messagebox.showinfo("成功", "✅ 快递单新增成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 新增失败，请检查字段！")
        
        ModernButton(btn_frame, text="确认提交", command=submit, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_query_order(self):
        """查询快递单对话框"""
        dialog = self.create_dialog("🔍 查询快递单", 450, 280)
        
        tk.Label(dialog,
                text="查询快递单",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.X, padx=40)
        
        order_id_var = tk.StringVar()
        status_var = tk.StringVar(value="全部")
        
        self.create_form_field(form_frame, 0, "快递单号", order_id_var)
        self.create_form_field(form_frame, 1, "快递状态", status_var, "combobox",
                              ["全部", "0(待收件)", "1(已收件)", "2(中转中)", "3(派送中)", "4(已签收)", "5(异常)"])
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=30)
        
        def query():
            condition = {}
            if order_id_var.get().strip():
                condition['orderId'] = order_id_var.get().strip()
            if status_var.get() != "全部":
                condition['orderStatus'] = status_var.get().split('(')[0]
            results = query_express_order(condition, use_index=True)
            self.update_tree_view(results)
            dialog.destroy()
        
        ModernButton(btn_frame, text="查询", command=query, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_edit_order(self):
        """修改快递单对话框"""
        dialog = self.create_dialog("✏️ 修改快递单", 550, 520)
        
        tk.Label(dialog,
                text="修改快递单信息",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        order_id_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "快递单号", order_id_var)
        
        fields = [
            ("寄件人ID", "senderId", "entry"),
            ("收件人ID", "receiverId", "entry"),
            ("物品名称", "goodsName", "entry"),
            ("物品重量(kg)", "goodsWeight", "entry"),
            ("寄件网点ID", "sendBranchId", "entry"),
            ("目标网点ID", "targetBranchId", "entry"),
            ("预计送达时间", "estimatedTime", "entry"),
            ("订单状态", "orderStatus", "combobox"),
        ]
        
        var_dict = {}
        widgets = {}
        for i, (label, key, field_type) in enumerate(fields, start=2):
            var = tk.StringVar()
            values = ["0(待收件)", "1(已收件)", "2(中转中)", "3(派送中)", "4(已签收)", "5(异常)"] if key == "orderStatus" else None
            widget = self.create_form_field(form_frame, i, label, var, field_type, values, state="disabled")
            var_dict[key] = var
            widgets[key] = widget
        
        def query_for_edit():
            oid = order_id_var.get().strip()
            if not oid:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            orders = query_express_order({"orderId": oid})
            if not orders:
                messagebox.showinfo("提示", "未找到快递单")
                for var in var_dict.values():
                    var.set("")
                for widget in widgets.values():
                    widget.config(state="disabled")
                return
            data = orders[0]
            for key, var in var_dict.items():
                if key == "orderStatus":
                    status_text = next(
                        (v for v in ["0(待收件)", "1(已收件)", "2(中转中)", "3(派送中)", "4(已签收)", "5(异常)"] 
                         if v.startswith(data.get(key, ""))), "")
                    var.set(status_text)
                else:
                    var.set(data.get(key, ""))
                widgets[key].config(state="normal" if key != "orderStatus" else "readonly")
        
        def submit_edit():
            oid = order_id_var.get().strip()
            if not oid:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            update_data = {}
            for key, var in var_dict.items():
                val = var.get().strip()
                if not val:
                    continue
                if key == "orderStatus":
                    update_data[key] = val.split("(")[0]
                else:
                    update_data[key] = val
            if update_express_order(oid, update_data):
                messagebox.showinfo("成功", "✅ 快递单更新成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 更新失败！")
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=15)
        
        ModernButton(btn_frame, text="查询", command=query_for_edit, style="secondary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="提交修改", command=submit_edit, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_delete_order(self):
        """删除快递单对话框"""
        dialog = self.create_dialog("🗑️ 删除快递单", 400, 200)
        
        tk.Label(dialog,
                text="删除快递单",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.DANGER_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.X, padx=40)
        
        order_id_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "快递单号", order_id_var)
        
        def confirm_delete():
            oid = order_id_var.get().strip()
            if not oid:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            if not messagebox.askyesno("确认", f"确定要删除快递单 {oid} 吗？\n关联的轨迹记录可能残留！"):
                return
            if delete_express_order(oid):
                messagebox.showinfo("成功", "✅ 快递单删除成功！")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "❌ 删除失败！")
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=20)
        
        ModernButton(btn_frame, text="确认删除", command=confirm_delete, style="danger").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_query_track(self):
        """查询快递轨迹对话框"""
        dialog = self.create_dialog("📍 查询快递轨迹", 450, 250)
        
        tk.Label(dialog,
                text="查询快递轨迹",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.X, padx=40)
        
        order_id_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "快递单号", order_id_var)
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=30)
        
        def query_text():
            oid = order_id_var.get().strip()
            if not oid:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            track_data = express_spatial_track(oid)
            self.update_tree_view(track_data)
            dialog.destroy()
        
        def query_visual():
            oid = order_id_var.get().strip()
            if not oid:
                messagebox.showwarning("警告", "请输入快递单号！")
                return
            track_data = express_spatial_track(oid)
            if not track_data:
                messagebox.showinfo("提示", "无轨迹数据")
                return
            visualize_track_window(track_data)
            dialog.destroy()
        
        ModernButton(btn_frame, text="📋 文本查询", command=query_text, style="primary").pack(side=tk.LEFT, padx=10)
        if VISUALIZATION_AVAILABLE:
            ModernButton(btn_frame, text="🗺️ 可视化", command=query_visual, style="success").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    # ==================== 统计分析 ====================
    def show_courier_stats(self):
        """快递员派送统计"""
        dialog = self.create_dialog("📊 快递员派送统计", 400, 200)
        
        tk.Label(dialog,
                text="快递员派送统计",
                font=(ThemeConfig.FONT_FAMILY, ThemeConfig.FONT_SIZE_TITLE, "bold"),
                fg=ThemeConfig.PRIMARY_COLOR,
                bg=ThemeConfig.CARD_BG).pack(pady=(20, 15))
        
        form_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        form_frame.pack(fill=tk.X, padx=40)
        
        courier_id_var = tk.StringVar()
        self.create_form_field(form_frame, 0, "快递员ID", courier_id_var)
        
        btn_frame = tk.Frame(dialog, bg=ThemeConfig.CARD_BG)
        btn_frame.pack(pady=20)
        
        def query():
            cid = courier_id_var.get().strip()
            if not cid:
                messagebox.showwarning("警告", "请输入快递员ID！")
                return
            today = datetime.now().strftime("%Y-%m-%d")
            stats_data = join_courier_orders(cid, today)
            self.update_tree_view(stats_data)
            dialog.destroy()
        
        ModernButton(btn_frame, text="查询", command=query, style="primary").pack(side=tk.LEFT, padx=10)
        ModernButton(btn_frame, text="取消", command=dialog.destroy, style="secondary").pack(side=tk.LEFT, padx=10)
    
    def show_branch_stats(self):
        """网点寄件量统计"""
        self.set_status("📊 正在加载网点寄件量统计...")
        stats_data = query_view("BranchMonthlySend")
        self.update_tree_view(stats_data)
