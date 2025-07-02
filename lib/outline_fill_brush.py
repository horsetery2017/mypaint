#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轮廓填充笔刷实现
提供轮廓绘制和自动填充功能
"""

import time
import math


class OutlineFillBrushSettings:
    """轮廓填充笔刷设置"""
    
    def __init__(self):
        # 轮廓设置
        self.outline_width = 2.0
        self.outline_color = (0.0, 0.0, 0.0, 1.0)  # RGBA
        self.outline_opacity = 1.0
        
        # 填充设置
        self.fill_color = (1.0, 0.0, 0.0, 0.5)  # RGBA
        self.fill_opacity = 0.5
        self.fill_mode = "solid"  # solid, gradient, pattern
        
        # 路径设置
        self.smoothness = 0.8
        self.close_path = True
        self.auto_fill = True
        
        # 高级设置
        self.outline_width_pressure = True
        self.fill_pressure_alpha = True


class OutlineFillBrush:
    """轮廓填充笔刷实现"""
    
    def __init__(self):
        self.current_path = []
        self.completed_paths = []
        self.settings = OutlineFillBrushSettings()
        self.is_drawing = False
        
    def start_stroke(self, x, y, pressure=1.0):
        """开始笔画"""
        self.is_drawing = True
        self.current_path = []
        self.add_point(x, y, pressure)
        
    def add_point(self, x, y, pressure=1.0):
        """添加路径点"""
        if not self.is_drawing:
            return
            
        point = {
            'x': x,
            'y': y,
            'pressure': pressure,
            'timestamp': time.time()
        }
        self.current_path.append(point)
        
    def end_stroke(self):
        """结束笔画"""
        if not self.is_drawing or len(self.current_path) < 2:
            self.is_drawing = False
            return
            
        # 平滑路径
        smoothed_path = self.smooth_path(self.current_path)
        
        # 闭合路径（如果需要）
        if self.settings.close_path and len(smoothed_path) > 2:
            smoothed_path.append(smoothed_path[0])
        
        self.completed_paths.append(smoothed_path)
        self.current_path = []
        self.is_drawing = False
        
    def smooth_path(self, path):
        """平滑路径"""
        if len(path) < 3:
            return path
            
        smoothed = []
        for i in range(len(path)):
            if i == 0 or i == len(path) - 1:
                smoothed.append(path[i])
            else:
                # 使用加权平均平滑
                prev = path[i-1]
                curr = path[i]
                next_point = path[i+1]
                
                smooth_x = (prev['x'] + curr['x'] * 2 + next_point['x']) / 4
                smooth_y = (prev['y'] + curr['y'] * 2 + next_point['y']) / 4
                
                smoothed.append({
                    'x': smooth_x,
                    'y': smooth_y,
                    'pressure': curr['pressure'],
                    'timestamp': curr['timestamp']
                })
        
        return smoothed
    
    def clear_paths(self):
        """清除所有路径"""
        self.current_path = []
        self.completed_paths = []
        
    def get_paths(self):
        """获取所有路径"""
        return self.completed_paths.copy()


class PathFiller:
    """路径填充算法"""
    
    def __init__(self, surface):
        self.surface = surface
        
    def fill_path(self, path, fill_color, fill_opacity):
        """填充路径内部"""
        if len(path) < 3:
            return
            
        # 获取路径边界框
        bbox = self.get_path_bbox(path)
        
        # 使用扫描线算法填充
        for y in range(int(bbox['min_y']), int(bbox['max_y']) + 1):
            intersections = self.get_line_intersections(path, y)
            
            # 排序交点
            intersections.sort()
            
            # 填充交点之间的区域
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    x1 = int(intersections[i])
                    x2 = int(intersections[i + 1])
                    
                    # 填充线段
                    for x in range(x1, x2 + 1):
                        if 0 <= x < self.surface.width and 0 <= y < self.surface.height:
                            self.fill_pixel(x, y, fill_color, fill_opacity)
    
    def get_path_bbox(self, path):
        """获取路径的边界框"""
        if not path:
            return {'min_x': 0, 'min_y': 0, 'max_x': 0, 'max_y': 0}
            
        min_x = min(p['x'] for p in path)
        max_x = max(p['x'] for p in path)
        min_y = min(p['y'] for p in path)
        max_y = max(p['y'] for p in path)
        
        return {
            'min_x': max(0, int(min_x)),
            'max_x': min(self.surface.width - 1, int(max_x)),
            'min_y': max(0, int(min_y)),
            'max_y': min(self.surface.height - 1, int(max_y))
        }
    
    def get_line_intersections(self, path, y):
        """获取水平线与路径的交点"""
        intersections = []
        
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i + 1]
            
            # 检查线段是否与水平线相交
            if (p1['y'] <= y and p2['y'] >= y) or (p1['y'] >= y and p2['y'] <= y):
                if abs(p2['y'] - p1['y']) > 0.001:  # 避免除零
                    # 计算交点x坐标
                    t = (y - p1['y']) / (p2['y'] - p1['y'])
                    x = p1['x'] + t * (p2['x'] - p1['x'])
                    intersections.append(x)
        
        return intersections
    
    def fill_pixel(self, x, y, fill_color, fill_opacity):
        """填充单个像素"""
        try:
            # 获取当前像素颜色
            current_color = self.surface.get_pixel(x, y)
            
            # 混合颜色
            blended_color = self.blend_colors(current_color, fill_color, fill_opacity)
            
            # 设置像素
            self.surface.set_pixel(x, y, blended_color)
        except:
            # 忽略边界错误
            pass
    
    def blend_colors(self, bg_color, fg_color, opacity):
        """混合颜色"""
        r1, g1, b1, a1 = bg_color
        r2, g2, b2, a2 = fg_color
        
        # 预乘alpha混合
        alpha = a2 * opacity
        inv_alpha = 1.0 - alpha
        
        r = r1 * inv_alpha + r2 * alpha
        g = g1 * inv_alpha + g2 * alpha
        b = b1 * inv_alpha + b2 * alpha
        a = a1 * inv_alpha + alpha
        
        return (r, g, b, a)


class OutlineFillRenderer:
    """轮廓填充笔刷渲染器"""
    
    def __init__(self, surface):
        self.surface = surface
        self.filler = PathFiller(surface)
        
    def render_outline(self, path, settings):
        """渲染轮廓"""
        if len(path) < 2:
            return
            
        # 设置轮廓颜色和透明度
        outline_color = settings.outline_color
        outline_opacity = settings.outline_opacity * outline_color[3]
        
        # 绘制路径线段
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i + 1]
            
            # 计算线段宽度（基于压力）
            if settings.outline_width_pressure:
                width = settings.outline_width * p1['pressure']
            else:
                width = settings.outline_width
            
            # 绘制线段
            self.draw_line(p1['x'], p1['y'], p2['x'], p2['y'], 
                          width, outline_color, outline_opacity)
    
    def draw_line(self, x1, y1, x2, y2, width, color, opacity):
        """绘制线段"""
        # 使用Bresenham算法绘制线段
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        # 避免除零错误
        if dx == 0 and dy == 0:
            # 单点，直接绘制
            self.draw_circle(x1, y1, width/2, color, opacity)
            return
        
        if dx > dy:
            # 水平线
            if x1 > x2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            
            for x in range(int(x1), int(x2) + 1):
                if x2 != x1:  # 避免除零
                    y = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
                else:
                    y = y1
                self.draw_circle(x, y, width/2, color, opacity)
        else:
            # 垂直线
            if y1 > y2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            
            for y in range(int(y1), int(y2) + 1):
                if y2 != y1:  # 避免除零
                    x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                else:
                    x = x1
                self.draw_circle(x, y, width/2, color, opacity)
    
    def draw_circle(self, x, y, radius, color, opacity):
        """绘制圆形（用于线段端点）"""
        radius = max(1, int(radius))
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    px, py = int(x + dx), int(y + dy)
                    if 0 <= px < self.surface.width and 0 <= py < self.surface.height:
                        try:
                            self.surface.set_pixel(px, py, color, opacity)
                        except:
                            pass
    
    def render_fill(self, path, settings):
        """渲染填充"""
        if not path or len(path) < 3:
            return
            
        # 填充路径内部
        fill_color = settings.fill_color
        fill_opacity = settings.fill_opacity * fill_color[3]
        
        self.filler.fill_path(path, fill_color, fill_opacity)
    
    def render_brush(self, brush):
        """渲染整个笔刷"""
        settings = brush.settings
        
        # 渲染所有完成的路径
        for path in brush.completed_paths:
            # 先渲染填充
            self.render_fill(path, settings)
            # 再渲染轮廓
            self.render_outline(path, settings) 