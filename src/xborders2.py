#!/bin/python3

import os
import subprocess
import threading
import webbrowser

import cairo
import gi
import requests

import xborderConfig

import cairo

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Wnck", "3.0")
gi.require_version("GObject", "2.0")
from gi.repository import Gtk, Gdk, Wnck, GObject, GLib

class WindowHighlights(Gtk.Window):
  wnck_screen: Wnck.Screen = None
  is_composited: bool = False
  is_fullscreen: bool = False
  
  def __init__(self, screen_index: int):
    super().__init__(type=Gtk.WindowType.POPUP)
  
    self.wnck_screen = Wnck.Screen.get_default()
    self.set_app_paintable(True)
    
    rgba_visual = self.get_screen().get_rgba_visual()
    if (rgba_visual == None):
      raise RuntimeError("RGBA windows not supported with current windowing system.")
    self.set_visual(rgba_visual)
    
    self.set_role("xborder")
    # Backwards compat
    self.set_wmclass("xborders", "xborder")
    
    self.resize(
      self.wnck_screen.get_width(),
      self.wnck_screen.get_height()
    )
    init_win_pos = 0 if self.get_screen().is_composited() else 1e6
    self.move(init_win_pos, init_win_pos)
    
    self.fullscreen()
    self.set_decorated(False)
    self.set_skip_taskbar_hint(True)
    self.set_skip_pager_hint(True)
    self.set_keep_above(True)
    self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
    
    self.set_accept_focus(False)
    self.set_focus_on_map(False)
    
    drawing_area = Gtk.DrawingArea()
    drawing_area.set_events(Gdk.EventMask.EXPOSURE_MASK)
    self.add(drawing_area)
    
    # Blank input region
    self.input_shape_combine_region(cairo.Region())
    self.set_keep_above(True)
    
    self.set_title("xborders")
    self.show_all()
    
    self.connect("destroy", Gtk.main_quit)
    self.connect("composited-changed", self.on_composited_changed)
    self.connect("draw", self.on_draw)
    
    self.wnck_screen.connect("active-window-changed", self.on_active_window_change)
    self.on_active_window_change()
    
    self.queue_draw()
  
  def active_window_connect_signal_once(self, signal_name: str, callback: callable) -> int:
    if not self.active_window:
      return
    signal = GObject.signal_lookup(signal_name,
                                  self.active_window)
    signal_has_connected = GObject.signal_has_handler_pending(self.active_window,
                                                              signal, 
                                                              0, False)
    if not signal_has_connected:
      connection_id: int = self.active_window.connect(signal_name,
                                                      callback)
      return connection_id

  signal_garbage: list[(Wnck.Window, int)] = []
  def on_active_window_change(self, *_) -> None:
    for garbage in self.signal_garbage:
      GObject.signal_handler_disconnect(garbage[0], garbage[1])
    self.signal_garbage.clear()
    
    self.active_window = self.wnck_screen.get_active_window()
    
    if self.active_window:
      state_change_con_id = self.active_window_connect_signal_once('state-changed',
                                                                  self.on_active_window_state_changed)
      self.signal_garbage.append((self.active_window, state_change_con_id))
  
  def on_active_window_state_changed(self, *_):
    if self.active_window == None:
      self.is_fullscreen = False
      return
    
    active_window_state = self.active_window.get_state()
    if (active_window_state & Wnck.WindowState.FULLSCREEN) != 0:
      self.is_fullscreen = True
    else:
      self.is_fullscreen = False
    
    print(self.is_fullscreen)
  
  def on_composited_changed(self, *_) -> None:
    self.is_composited = self.get_screen().is_composited()
    
  def on_draw(self, _, ctx) -> None:
    workspace = self.wnck_screen.get_active_workspace()
    all_windows = self.wnck_screen.get_windows_stacked()
    ctx.save()
    
    print(len(all_windows))
    for window in all_windows:
      if window.is_visible_on_workspace(workspace):
        if window.get_window_type() == Wnck.WindowType.NORMAL:
          window_geometry = window.get_geometry()
          x = window_geometry.xp
          y = window_geometry.yp
          w = window_geometry.widthp
          h = window_geometry.heightp
          
          ctx.set_source_rgba(0, 0, 0, 0)
          ctx.set_operator(cairo.OPERATOR_SOURCE)
          
          radius = 24
          degrees = 0.017453292519943295  # pi/180
          ctx.arc(x + w - radius, y + radius, radius, -90 * degrees, 0 * degrees)
          ctx.arc(x + w - radius, y + h - radius, radius, 0 * degrees, 90 * degrees)
          ctx.arc(x + radius, y + h - radius, radius, 90 * degrees, 180 * degrees)
          ctx.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
          ctx.close_path()
          
          ctx.fill_preserve()
          ctx.set_source_rgba(1, 1, 1, 1)
          ctx.set_line_width(4)
          ctx.stroke()
    
    print("Drew")
    ctx.restore()
    # self.queue_draw()
    GLib.timeout_add(1000 / 24, self.queue_draw)

WindowHighlights(0)
Gtk.main()
