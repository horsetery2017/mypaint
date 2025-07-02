#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轮廓填充笔刷编辑器
提供笔刷参数的图形化设置界面
"""

from lib.gibindings import Gtk
from lib.gibindings import Gdk
from lib.outline_fill_brush import OutlineFillBrushSettings


class OutlineFillBrushEditor(Gtk.Dialog):
    """轮廓填充笔刷编辑器"""
    
    def __init__(self, parent, brush):
        super().__init__("轮廓填充笔刷设置", parent)
        
        self.brush = brush
        self.settings = brush.settings
        
        self.setup_ui()
        self.connect_signals()
        self.load_current_settings()
        
    def setup_ui(self):
        """设置用户界面"""
        self.set_default_size(400, 500)
        
        # 创建主布局
        main_box = self.get_content_area()
        main_box.set_spacing(10)
        
        # 轮廓设置组
        outline_frame = Gtk.Frame(label="轮廓设置")
        outline_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        outline_box.set_margin_start(10)
        outline_box.set_margin_end(10)
        outline_box.set_margin_top(10)
        outline_box.set_margin_bottom(10)
        
        # 轮廓宽度
        width_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        width_label = Gtk.Label(label="轮廓宽度:")
        width_label.set_size_request(100, -1)
        self.width_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.5, 10.0, 0.5
        )
        self.width_scale.set_value(self.settings.outline_width)
        self.width_value_label = Gtk.Label(label=f"{self.settings.outline_width:.1f}")
        self.width_value_label.set_size_request(50, -1)
        
        width_box.pack_start(width_label, False, False, 0)
        width_box.pack_start(self.width_scale, True, True, 0)
        width_box.pack_start(self.width_value_label, False, False, 0)
        outline_box.pack_start(width_box, False, False, 0)
        
        # 轮廓颜色
        color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        color_label = Gtk.Label(label="轮廓颜色:")
        color_label.set_size_request(100, -1)
        self.color_button = Gtk.ColorButton()
        self.color_button.set_rgba(Gdk.RGBA(*self.settings.outline_color[:3]))
        color_box.pack_start(color_label, False, False, 0)
        color_box.pack_start(self.color_button, False, False, 0)
        outline_box.pack_start(color_box, False, False, 0)
        
        # 轮廓透明度
        opacity_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        opacity_label = Gtk.Label(label="轮廓透明度:")
        opacity_label.set_size_request(100, -1)
        self.outline_opacity_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.0, 1.0, 0.1
        )
        self.outline_opacity_scale.set_value(self.settings.outline_opacity)
        self.outline_opacity_label = Gtk.Label(label=f"{self.settings.outline_opacity:.1f}")
        self.outline_opacity_label.set_size_request(50, -1)
        
        opacity_box.pack_start(opacity_label, False, False, 0)
        opacity_box.pack_start(self.outline_opacity_scale, True, True, 0)
        opacity_box.pack_start(self.outline_opacity_label, False, False, 0)
        outline_box.pack_start(opacity_box, False, False, 0)
        
        # 压力响应
        pressure_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        pressure_label = Gtk.Label(label="压力响应:")
        pressure_label.set_size_request(100, -1)
        self.pressure_check = Gtk.CheckButton(label="轮廓宽度随压力变化")
        self.pressure_check.set_active(self.settings.outline_width_pressure)
        pressure_box.pack_start(pressure_label, False, False, 0)
        pressure_box.pack_start(self.pressure_check, False, False, 0)
        outline_box.pack_start(pressure_box, False, False, 0)
        
        outline_frame.add(outline_box)
        main_box.pack_start(outline_frame, False, False, 0)
        
        # 填充设置组
        fill_frame = Gtk.Frame(label="填充设置")
        fill_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        fill_box.set_margin_start(10)
        fill_box.set_margin_end(10)
        fill_box.set_margin_top(10)
        fill_box.set_margin_bottom(10)
        
        # 填充颜色
        fill_color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        fill_color_label = Gtk.Label(label="填充颜色:")
        fill_color_label.set_size_request(100, -1)
        self.fill_color_button = Gtk.ColorButton()
        self.fill_color_button.set_rgba(Gdk.RGBA(*self.settings.fill_color[:3]))
        fill_color_box.pack_start(fill_color_label, False, False, 0)
        fill_color_box.pack_start(self.fill_color_button, False, False, 0)
        fill_box.pack_start(fill_color_box, False, False, 0)
        
        # 填充透明度
        fill_opacity_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        fill_opacity_label = Gtk.Label(label="填充透明度:")
        fill_opacity_label.set_size_request(100, -1)
        self.fill_opacity_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.0, 1.0, 0.1
        )
        self.fill_opacity_scale.set_value(self.settings.fill_opacity)
        self.fill_opacity_label = Gtk.Label(label=f"{self.settings.fill_opacity:.1f}")
        self.fill_opacity_label.set_size_request(50, -1)
        
        fill_opacity_box.pack_start(fill_opacity_label, False, False, 0)
        fill_opacity_box.pack_start(self.fill_opacity_scale, True, True, 0)
        fill_opacity_box.pack_start(self.fill_opacity_label, False, False, 0)
        fill_box.pack_start(fill_opacity_box, False, False, 0)
        
        # 自动填充
        auto_fill_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        auto_fill_label = Gtk.Label(label="自动填充:")
        auto_fill_label.set_size_request(100, -1)
        self.auto_fill_check = Gtk.CheckButton(label="绘制完成后自动填充")
        self.auto_fill_check.set_active(self.settings.auto_fill)
        auto_fill_box.pack_start(auto_fill_label, False, False, 0)
        auto_fill_box.pack_start(self.auto_fill_check, False, False, 0)
        fill_box.pack_start(auto_fill_box, False, False, 0)
        
        fill_frame.add(fill_box)
        main_box.pack_start(fill_frame, False, False, 0)
        
        # 路径设置组
        path_frame = Gtk.Frame(label="路径设置")
        path_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        path_box.set_margin_start(10)
        path_box.set_margin_end(10)
        path_box.set_margin_top(10)
        path_box.set_margin_bottom(10)
        
        # 路径平滑
        smooth_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        smooth_label = Gtk.Label(label="路径平滑:")
        smooth_label.set_size_request(100, -1)
        self.smooth_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.0, 1.0, 0.1
        )
        self.smooth_scale.set_value(self.settings.smoothness)
        self.smooth_label = Gtk.Label(label=f"{self.settings.smoothness:.1f}")
        self.smooth_label.set_size_request(50, -1)
        
        smooth_box.pack_start(smooth_label, False, False, 0)
        smooth_box.pack_start(self.smooth_scale, True, True, 0)
        smooth_box.pack_start(self.smooth_label, False, False, 0)
        path_box.pack_start(smooth_box, False, False, 0)
        
        # 闭合路径
        close_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        close_label = Gtk.Label(label="闭合路径:")
        close_label.set_size_request(100, -1)
        self.close_check = Gtk.CheckButton(label="自动闭合路径")
        self.close_check.set_active(self.settings.close_path)
        close_box.pack_start(close_label, False, False, 0)
        close_box.pack_start(self.close_check, False, False, 0)
        path_box.pack_start(close_box, False, False, 0)
        
        path_frame.add(path_box)
        main_box.pack_start(path_frame, False, False, 0)
        
        # 按钮
        self.add_button("应用", Gtk.ResponseType.APPLY)
        self.add_button("取消", Gtk.ResponseType.CANCEL)
        
    def connect_signals(self):
        """连接信号"""
        self.width_scale.connect("value-changed", self.on_width_changed)
        self.color_button.connect("color-set", self.on_outline_color_changed)
        self.outline_opacity_scale.connect("value-changed", self.on_outline_opacity_changed)
        self.fill_color_button.connect("color-set", self.on_fill_color_changed)
        self.fill_opacity_scale.connect("value-changed", self.on_fill_opacity_changed)
        self.smooth_scale.connect("value-changed", self.on_smooth_changed)
        
        self.pressure_check.connect("toggled", self.on_pressure_toggled)
        self.auto_fill_check.connect("toggled", self.on_auto_fill_toggled)
        self.close_check.connect("toggled", self.on_close_toggled)
        
    def load_current_settings(self):
        """加载当前设置"""
        # 更新标签显示
        self.width_value_label.set_text(f"{self.settings.outline_width:.1f}")
        self.outline_opacity_label.set_text(f"{self.settings.outline_opacity:.1f}")
        self.fill_opacity_label.set_text(f"{self.settings.fill_opacity:.1f}")
        self.smooth_label.set_text(f"{self.settings.smoothness:.1f}")
        
    def on_width_changed(self, scale):
        """轮廓宽度改变"""
        value = scale.get_value()
        self.settings.outline_width = value
        self.width_value_label.set_text(f"{value:.1f}")
        
    def on_outline_color_changed(self, button):
        """轮廓颜色改变"""
        color = button.get_rgba()
        self.settings.outline_color = (color.red, color.green, color.blue, 1.0)
        
    def on_outline_opacity_changed(self, scale):
        """轮廓透明度改变"""
        value = scale.get_value()
        self.settings.outline_opacity = value
        self.outline_opacity_label.set_text(f"{value:.1f}")
        
    def on_fill_color_changed(self, button):
        """填充颜色改变"""
        color = button.get_rgba()
        self.settings.fill_color = (color.red, color.green, color.blue, 1.0)
        
    def on_fill_opacity_changed(self, scale):
        """填充透明度改变"""
        value = scale.get_value()
        self.settings.fill_opacity = value
        self.fill_opacity_label.set_text(f"{value:.1f}")
        
    def on_smooth_changed(self, scale):
        """平滑度改变"""
        value = scale.get_value()
        self.settings.smoothness = value
        self.smooth_label.set_text(f"{value:.1f}")
        
    def on_pressure_toggled(self, check):
        """压力响应切换"""
        self.settings.outline_width_pressure = check.get_active()
        
    def on_auto_fill_toggled(self, check):
        """自动填充切换"""
        self.settings.auto_fill = check.get_active()
        
    def on_close_toggled(self, check):
        """闭合路径切换"""
        self.settings.close_path = check.get_active()
        
    def get_settings(self):
        """获取当前设置"""
        return self.settings 