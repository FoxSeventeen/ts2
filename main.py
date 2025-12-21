import tkinter as tk
from tkinter import messagebox
import os
import sys
from GUI import ExpressGUI
from index_core import HashIndex  # 导入索引类
from db_core import DATA_DIR, INDEX_DIR, VIEWS_META_PATH  # 导入路径常量


def init_directories():
    """初始化必要的目录，确保路径规范"""
    try:
        # 创建数据目录（DATA_DIR）
        os.makedirs(DATA_DIR, exist_ok=True)
        # 创建索引目录（INDEX_DIR）
        os.makedirs(INDEX_DIR, exist_ok=True)
        print(f"✅ 数据目录：{os.path.abspath(DATA_DIR)}")
        print(f"✅ 索引目录：{os.path.abspath(INDEX_DIR)}")
        
        # 检查并创建/修复Courier.csv（快递员表）
        courier_path = os.path.join(DATA_DIR, "Courier.csv")
        correct_header = "courierId,courierName,courierPhone,branchId,courierIdCard\n"
        
        if not os.path.exists(courier_path):
            with open(courier_path, 'w', encoding='utf-8', newline='') as f:
                # 写入快递员表表头（不包含入职日期）
                f.write(correct_header)
            print(f"✅ 已创建快递员表：{courier_path}")
        else:
            # 检查并修复表头（移除hireDate字段）
            try:
                with open(courier_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if lines and 'hireDate' in lines[0]:
                    # 需要修复表头，移除hireDate列
                    print(f"ℹ️ 检测到旧版Courier表，正在修复...")
                    new_lines = [correct_header]
                    for line in lines[1:]:
                        parts = line.strip().split(',')
                        if len(parts) >= 5:
                            # 只保留前5个字段（移除hireDate）
                            new_lines.append(','.join(parts[:5]) + '\n')
                    with open(courier_path, 'w', encoding='utf-8', newline='') as f:
                        f.writelines(new_lines)
                    print(f"✅ 快递员表已修复：{courier_path}")
                else:
                    print(f"ℹ️ 快递员表已存在：{courier_path}")
            except Exception as e:
                print(f"⚠️ 检查快递员表时出错：{e}")
        
        return True
    except Exception as e:
        messagebox.showerror("目录初始化失败", f"无法创建必要目录：{str(e)}")
        print(f"❌ 目录初始化失败：{e}")
        return False


def init_views_meta():
    """初始化视图元数据文件（views.meta）"""
    try:
        if not os.path.exists(VIEWS_META_PATH):
            with open(VIEWS_META_PATH, 'w', encoding='utf-8') as f:
                # 写入视图元数据表头
                f.write("viewName|defineSQL|createTime|creatorId\n")
            print(f"✅ 已创建视图元数据文件：{VIEWS_META_PATH}")
        else:
            print(f"ℹ️ 视图元数据文件已存在：{VIEWS_META_PATH}")
        return True
    except Exception as e:
        messagebox.showerror("视图文件初始化失败", f"无法创建views.meta：{str(e)}")
        print(f"❌ 视图文件初始化失败：{e}")
        return False


def init_indexes():
    """初始化索引：为已有数据的表自动构建索引"""
    try:
        # 需要初始化索引的表和字段（可根据实际需求扩展）
        tables = [
            ("User", "uphone"),  # 用户表-手机号索引
            ("ExpressOrder", "orderId")  # 快递单表-单号索引
        ]

        for table_name, index_col in tables:
            csv_path = os.path.join(DATA_DIR, f"{table_name}.csv")
            # 检查CSV文件是否存在且非空
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                print(f"ℹ️ 检测到{table_name}.csv，开始构建{index_col}索引...")
                index = HashIndex(table_name, index_col)
                index.build()  # 基于已有数据构建索引
            else:
                print(f"ℹ️ {table_name}.csv为空或不存在，暂不构建索引")
        return True
    except Exception as e:
        messagebox.showwarning("索引初始化警告", f"部分索引构建失败：{str(e)}\n不影响新增数据，但历史数据可能查询不到")
        print(f"⚠️ 索引初始化警告：{e}")
        return False  # 索引失败不阻断程序启动，仅警告


def main():
    """主程序入口：初始化环境并启动GUI"""
    # 设置中文字体支持（避免Tkinter中文乱码）
    root = tk.Tk()
    root.option_add("*Font", ["SimHei", 10])  # 适配中文显示

    # 打印程序启动信息
    print("=" * 50)
    print(f"程序启动于：{os.path.abspath('.')}")
    print(f"Python路径：{sys.executable}")
    print("=" * 50)

    # 分步初始化
    if not init_directories():
        root.destroy()
        return

    if not init_views_meta():
        root.destroy()
        return

    # 索引初始化失败不阻断程序，仅警告
    init_indexes()

    # 启动GUI
    try:
        app = ExpressGUI(root)
        root.title("快递管理系统")
        root.geometry("1000x600")  # 设置初始窗口大小
        root.mainloop()
    except Exception as e:
        messagebox.showerror("程序启动失败", f"GUI初始化错误：{str(e)}")
        print(f"❌ GUI启动失败：{e}")


if __name__ == "__main__":
    main()