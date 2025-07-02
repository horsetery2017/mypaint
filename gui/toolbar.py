# This file is part of MyPaint.
# Copyright (C) 2011-2018 by the MyPaint Development Team.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""The application toolbar, and its specialised widgets"""


## Imports

import os
from gettext import gettext as _

from lib.gibindings import Gtk

from . import widgets


## Module constants


FRAMEWORK_XML = "toolbar.xml"
MERGEABLE_XML = [
    ("toolbar1_file", "toolbar-file.xml", _("File handling")),
    ("toolbar1_scrap", "toolbar-scrap.xml", _("Scraps switcher")),
    ("toolbar1_edit", "toolbar-edit.xml", _("Undo and Redo")),
    ("toolbar1_blendmodes", "toolbar-blendmodes.xml", _("Blend Modes")),
    ("toolbar1_linemodes", "toolbar-linemodes.xml", _("Line Modes")),
    ("toolbar1_view_modes", "toolbar-view-modes.xml", _("View (Main)")),
    (
        "toolbar1_view_manips",
        "toolbar-view-manips.xml",
        _("View (Alternative/Secondary)"),
    ),
    ("toolbar1_view_resets", "toolbar-view-resets.xml", _("View (Resetting)")),
]


## Class definitions


class ToolbarManager(object):
    """Manager for toolbars, currently just the main one.

    The main toolbar, /toolbar1, contains a menu button and quick
    access to the painting tools.
    """

    def __init__(self, draw_window):
        super(ToolbarManager, self).__init__()
        self.draw_window = draw_window
        self.app = draw_window.app
        self.toolbar1_ui_loaded = {}  # {name: merge_id, ...}
        self.init_actions()
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        toolbarpath = os.path.join(ui_dir, FRAMEWORK_XML)
        self.app.ui_manager.add_ui_from_file(toolbarpath)
        self.toolbar1 = self.app.ui_manager.get_widget("/toolbar1")
        self.toolbar1.set_style(Gtk.ToolbarStyle.ICONS)
        self.toolbar1.set_icon_size(widgets.get_toolbar_icon_size())
        self.toolbar1.set_border_width(0)
        self.toolbar1.set_show_arrow(True)
        self.toolbar1.connect("popup-context-menu", self.on_toolbar1_popup_context_menu)
        self.toolbar1_popup = self.app.ui_manager.get_widget("/toolbar1-settings-menu")
        for item in self.toolbar1:
            if isinstance(item, Gtk.SeparatorToolItem):
                item.set_draw(False)
        self.toolbar2 = self.app.ui_manager.get_widget("/toolbar2")
        self.toolbar2.set_style(Gtk.ToolbarStyle.ICONS)
        self.toolbar2.set_icon_size(widgets.get_toolbar_icon_size())
        self.toolbar2.set_border_width(0)
        self.toolbar2.set_show_arrow(False)
        for toolbar in (self.toolbar1, self.toolbar2):
            styles = toolbar.get_style_context()
            styles.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        # Merge in UI pieces based on the user's saved preferences
        for action in self.settings_actions:
            name = action.get_property("name")
            active = self.app.preferences["ui.toolbar_items"].get(name, False)
            action.set_active(active)
            action.toggled()

    def init_actions(self):
        ag = self.draw_window.action_group
        actions = []

        self.settings_actions = []
        for name, ui_xml, label in MERGEABLE_XML:
            action = Gtk.ToggleAction.new(name, label, None, None)
            action.connect("toggled", self.on_settings_toggle, ui_xml)
            self.settings_actions.append(action)
        actions += self.settings_actions

        for action in actions:
            ag.add_action(action)

    def on_toolbar1_popup_context_menu(self, toolbar, x, y, button):
        menu = self.toolbar1_popup

        def _posfunc(*a):
            return x, y, True

        time = Gtk.get_current_event_time()
        menu.popup(None, None, _posfunc, None, button, time)

    def on_settings_toggle(self, toggleaction, ui_xml_file):
        name = toggleaction.get_property("name")
        merge_id = self.toolbar1_ui_loaded.get(name, None)
        if toggleaction.get_active():
            self.app.preferences["ui.toolbar_items"][name] = True
            if merge_id is not None:
                return
            ui_dir = os.path.dirname(os.path.abspath(__file__))
            ui_xml_path = os.path.join(ui_dir, ui_xml_file)
            merge_id = self.app.ui_manager.add_ui_from_file(ui_xml_path)
            self.toolbar1_ui_loaded[name] = merge_id
        else:
            self.app.preferences["ui.toolbar_items"][name] = False
            if merge_id is None:
                return
            self.app.ui_manager.remove_ui(merge_id)
            self.toolbar1_ui_loaded.pop(name)

def add_outline_fill_brush_button(toolbar, app):
    """添加轮廓填充笔刷按钮到工具栏"""
    try:
        # 获取轮廓填充笔刷管理器
        outline_fill_manager = app.outline_fill_brush_manager
        
        if not outline_fill_manager:
            print("轮廓填充笔刷管理器未初始化")
            return None
        
        # 获取笔刷按钮
        brush_button = outline_fill_manager.get_brush_button()
        
        if not brush_button:
            print("笔刷按钮为空")
            return None
        
        # 添加到工具栏
        toolbar.insert(brush_button, -1)
        
        # 添加分隔符
        separator = Gtk.SeparatorToolItem()
        separator.set_draw(False)
        separator.set_expand(True)
        toolbar.insert(separator, -1)
        
        print("轮廓填充笔刷按钮已添加到工具栏")
        return brush_button
    except Exception as e:
        print(f"添加轮廓填充笔刷按钮时出错: {e}")
        import traceback
        traceback.print_exc()
        return None
