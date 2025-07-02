#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轮廓填充笔刷管理器
集成到MyPaint的笔刷系统中
"""

from lib.gibindings import Gtk
from lib.gibindings import Gdk
from lib.outline_fill_brush import OutlineFillBrush, OutlineFillRenderer
from gui.outline_fill_brush_editor import OutlineFillBrushEditor


class OutlineFillBrushManager:
    """轮廓填充笔刷管理器"""
    
    def __init__(self, app):
        self.app = app
        self.brush = OutlineFillBrush()
        self.renderer = None
        self.is_active = False
        self.brush_button = None
        
        # 延迟创建按钮，等待应用程序完全初始化
        self._create_button_delayed()
        
    def _create_button_delayed(self):
        """延迟创建按钮"""
        try:
            # 等待应用程序完全初始化
            if hasattr(self.app, 'draw_window') and self.app.draw_window:
                self.create_brush_button()
            else:
                # 如果还没有准备好，稍后再试
                import threading
                import time
                def delayed_create():
                    time.sleep(1)  # 等待1秒
                    self._create_button_delayed()
                threading.Thread(target=delayed_create, daemon=True).start()
        except Exception as e:
            print(f"延迟创建按钮失败: {e}")
        
    def create_brush_button(self):
        """创建笔刷按钮"""
        try:
            # 创建工具栏按钮 - 使用ToolItem作为基类
            self.brush_button = Gtk.ToolItem()
            
            # 创建内部按钮
            inner_button = Gtk.Button()
            inner_button.set_tooltip_text("轮廓填充笔刷")
            
            # 创建图标 - 尝试多个图标名称
            icon = Gtk.Image()
            icon_names = [
                "mypaint-brush-symbolic",
                "brush-symbolic", 
                "edit-symbolic",
                "document-edit-symbolic",
                "gtk-edit"
            ]
            
            icon_set = False
            for icon_name in icon_names:
                try:
                    icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
                    print(f"成功设置图标: {icon_name}")
                    icon_set = True
                    break
                except Exception as e:
                    print(f"图标 {icon_name} 设置失败: {e}")
                    continue
            
            if not icon_set:
                # 如果所有图标都失败，使用文本标签
                print("所有图标都失败，使用文本标签")
                inner_button.set_label("轮廓")
            
            inner_button.set_image(icon)
            
            # 连接信号
            inner_button.connect("clicked", self.on_brush_button_clicked)
            
            # 将按钮添加到ToolItem
            self.brush_button.add(inner_button)
            
            print("轮廓填充笔刷按钮创建成功")
        except Exception as e:
            print(f"创建笔刷按钮失败: {e}")
            self.brush_button = None
        
    def on_brush_button_clicked(self, button):
        """笔刷按钮点击事件"""
        if self.is_active:
            self.deactivate_brush()
        else:
            self.activate_brush()
            
    def activate_brush(self):
        """激活笔刷"""
        if not self.brush_button:
            print("笔刷按钮未创建，无法激活")
            return
            
        self.is_active = True
        try:
            self.brush_button.get_style_context().add_class("suggested-action")
        except:
            pass
        
        # 获取当前文档的表面
        doc = self.app.doc
        if doc and hasattr(doc, 'surface'):
            self.renderer = OutlineFillRenderer(doc.surface)
            
        # 设置事件处理
        self.setup_event_handling()
        
        print("轮廓填充笔刷已激活")
        
    def deactivate_brush(self):
        """停用笔刷"""
        if not self.brush_button:
            return
            
        self.is_active = False
        try:
            self.brush_button.get_style_context().remove_class("suggested-action")
        except:
            pass
        self.remove_event_handling()
        print("轮廓填充笔刷已停用")
        
    def setup_event_handling(self):
        """设置事件处理"""
        # 获取主绘图窗口
        main_window = self.app.draw_window
        if main_window:
            # 连接鼠标事件
            drawing_area = main_window.tdw
            if drawing_area:
                drawing_area.connect("button-press-event", self.on_button_press)
                drawing_area.connect("motion-notify-event", self.on_motion_notify)
                drawing_area.connect("button-release-event", self.on_button_release)
                
    def remove_event_handling(self):
        """移除事件处理"""
        main_window = self.app.draw_window
        if main_window:
            drawing_area = main_window.tdw
            if drawing_area:
                try:
                    drawing_area.disconnect_by_func(self.on_button_press)
                    drawing_area.disconnect_by_func(self.on_motion_notify)
                    drawing_area.disconnect_by_func(self.on_button_release)
                except:
                    pass
                    
    def on_button_press(self, widget, event):
        """鼠标按下事件"""
        if not self.is_active:
            return False
            
        if event.button == 1:  # 左键
            # 获取画布坐标
            x, y = self.get_canvas_coordinates(event)
            pressure = self.get_pressure(event)
            
            # 开始笔画
            self.brush.start_stroke(x, y, pressure)
            return True
            
        return False
        
    def on_motion_notify(self, widget, event):
        """鼠标移动事件"""
        if not self.is_active or not self.brush.is_drawing:
            return False
            
        # 获取画布坐标
        x, y = self.get_canvas_coordinates(event)
        pressure = self.get_pressure(event)
        
        # 添加路径点
        self.brush.add_point(x, y, pressure)
        
        # 实时预览（可选）
        self.preview_current_path()
        
        return True
        
    def on_button_release(self, widget, event):
        """鼠标释放事件"""
        if not self.is_active or not self.brush.is_drawing:
            return False
            
        if event.button == 1:  # 左键
            # 获取画布坐标
            x, y = self.get_canvas_coordinates(event)
            pressure = self.get_pressure(event)
            
            # 添加最后一个点
            self.brush.add_point(x, y, pressure)
            
            # 结束笔画
            self.brush.end_stroke()
            
            # 渲染到画布
            self.render_to_canvas()
            
            return True
            
        return False
        
    def get_canvas_coordinates(self, event):
        """获取画布坐标"""
        # 获取绘图窗口
        main_window = self.app.draw_window
        if main_window and main_window.tdw:
            # 转换坐标
            x, y = main_window.tdw.get_canvas_coordinates(event.x, event.y)
            return x, y
        return event.x, event.y
        
    def get_pressure(self, event):
        """获取压力值"""
        if hasattr(event, 'pressure') and event.pressure > 0:
            return event.pressure
        return 1.0
        
    def preview_current_path(self):
        """预览当前路径"""
        # 这里可以实现实时预览功能
        pass
        
    def render_to_canvas(self):
        """渲染到画布"""
        if not self.renderer:
            return
            
        # 渲染笔刷
        self.renderer.render_brush(self.brush)
        
        # 刷新画布
        main_window = self.app.draw_window
        if main_window and main_window.tdw:
            main_window.tdw.queue_draw()
            
    def show_editor(self):
        """显示笔刷编辑器"""
        if not self.is_active:
            self.activate_brush()
            
        # 创建编辑器对话框
        parent = self.app.draw_window
        editor = OutlineFillBrushEditor(parent, self.brush)
        
        # 运行对话框
        response = editor.run()
        
        if response == Gtk.ResponseType.APPLY:
            # 应用设置
            settings = editor.get_settings()
            self.brush.settings = settings
            print("笔刷设置已更新")
            
        editor.destroy()
        
    def get_brush_button(self):
        """获取笔刷按钮"""
        if not self.brush_button:
            # 如果按钮还没有创建，尝试创建
            self.create_brush_button()
        
        return self.brush_button
        
    def clear_canvas(self):
        """清除画布上的笔刷内容"""
        self.brush.clear_paths()
        
        # 刷新画布
        main_window = self.app.draw_window
        if main_window and main_window.tdw:
            main_window.tdw.queue_draw() 