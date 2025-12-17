#!/usr/bin/env python3
"""
快递轨迹可视化测试脚本
演示如何使用visualization模块
"""
import sys
import os

# 添加项目根目录到路径（便于导入模块）
sys.path.insert(0, os.path.dirname(__file__))

from spatial_core import express_spatial_track
from visualization import visualize_track_window
import tkinter as tk


def test_visualization():
    """测试可视化功能"""
    print("=" * 50)
    print("快递轨迹可视化测试")
    print("=" * 50)
    
    # 1. 查询轨迹数据
    test_order_id = "EXP001"
    print(f"\n正在查询快递单号: {test_order_id}")
    track_data = express_spatial_track(test_order_id)
    
    if not track_data:
        print("❌ 未找到轨迹数据")
        return
    
    print(f"✅ 查询到 {len(track_data)} 条轨迹记录\n")
    
    # 2. 打印轨迹详情
    print("轨迹详情：")
    for idx, track in enumerate(track_data, 1):
        print(f"{idx}. {track['操作时间']} | {track['操作类型']} | {track['当前网点坐标']} | {track['当前网点名称']}")
    
    # 3. 弹出可视化窗口
    print("\n正在启动可视化窗口...")
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    visualize_track_window(track_data)
    root.mainloop()


if __name__ == "__main__":
    test_visualization()
