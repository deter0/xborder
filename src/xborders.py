#!/bin/python3

import os
import subprocess
import threading
import webbrowser

import cairo
import gi
import requests

import xborderConfig

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Wnck", "3.0")
gi.require_version("GObject", "2.0")
from gi.repository import Gtk, Gdk, Wnck, GObject

GlobalConfig: xborderConfig.xborderConfig = xborderConfig.xborderConfig()

def get_version() -> float|str:
    try:
        our_location = os.path.dirname(os.path.abspath(__file__))

        version_file = open(our_location + "/../version.txt", "r")
        our_version_string = version_file.read()
        version_file.close()

        return float(our_version_string)
    except:
        return "[ERROR GETTING VERSION]"

def get_latest_version() -> float|str:
    try:
        url = "https://raw.githubusercontent.com/deter0/xborder/main/version.txt"  # Maybe hardcoding it is a bad idea
        request = requests.get(url, allow_redirects=True)
        latest_version_string = request.content.decode("utf-8")

        return float(latest_version_string)
    except:
        return "[ERROR GETTING LATEST VERSION]"

def get_screen_size(display) -> tuple[int]:  # TODO: Multiple monitor size support
    mon_geoms = [display.get_monitor(i).get_geometry() for i in range(display.get_n_monitors())]

    x0 = min(r.x for r in mon_geoms)
    y0 = min(r.y for r in mon_geoms)
    x1 = max(r.x + r.width for r in mon_geoms)
    y1 = max(r.y + r.height for r in mon_geoms)

    return x1 - x0, y1 - y0

def notify_about_version(our_version: float, latest_version: float) -> None:
        notification_string = f"xborders has an update!  [{our_version} 🡢 {latest_version}]"
        completed_process = subprocess.run(
            ["notify-send", "--app-name=xborder", "--expire-time=5000",
            notification_string, "--action=How to Update?",
            "--action=Ignore Update"],
            capture_output=True
        )
        if completed_process.returncode == 0:
            result_string = completed_process.stdout.decode("utf-8")
            if result_string == '':
                return
            result = int(result_string)
            if result == 1:
                our_location = os.path.dirname(os.path.abspath(__file__))
                file = open(our_location + "/.update_ignore.txt", "w")
                file.write(str(latest_version))
                file.close()
            elif result == 0:
                webbrowser.open_new_tab("https://github.com/deter0/xborder#updating")
        else:
            print("something went wrong in notify-send.")

def notify_version():
    if GlobalConfig.disableUpdatePrompt:
        return
    try:
        our_location = os.path.dirname(os.path.abspath(__file__))
        
        our_version = get_version()
        latest_version = get_latest_version()
        if (type(latest_version) == str):
            return

        if os.path.isfile(our_location + "/../.update_ignore.txt"):
            ignore_version_file = open(our_location + "/.update_ignore.txt", "r")
            ignored_version_string = ignore_version_file.read()
            ignored_version = float(ignored_version_string)
            if ignored_version == latest_version:
                return

        if our_version < latest_version:
            threading._start_new_thread(notify_about_version, (our_version, latest_version))
    except:
        try:
            subprocess.Popen(["notify-send", "--app-name=xborders", "ERROR: xborders couldn't get latest version!"])
        except:
            pass

class Highlight(Gtk.Window):
    def __init__(self, screen_width, screen_height):
        super().__init__(type=Gtk.WindowType.POPUP)
        notify_version()

        self.wnck_screen = Wnck.Screen.get_default()

        self.set_app_paintable(True)
        self.screen = self.get_screen()
        self.set_visual(self.screen.get_rgba_visual())

        # As described here: https://docs.gtk.org/gtk3/method.Window.set_wmclass.html
        # Picom blur exclusion would be:
        # "role   = 'xborder'",
        self.set_role("xborder")

        # We can still set this for old configurations, we don't want to update and have the user confused as to what
        # has happened
        self.set_wmclass("xborders", "xborder")

        self.resize(screen_width, screen_height)
        self.move(0, 0)

        self.fullscreen()
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)

        self.set_accept_focus(False)
        self.set_focus_on_map(False)

        self.drawingarea = Gtk.DrawingArea()
        self.drawingarea.set_events(Gdk.EventMask.EXPOSURE_MASK)
        self.add(self.drawingarea)
        self.input_shape_combine_region(cairo.Region())

        self.set_keep_above(True)
        self.set_title("xborders")
        self.show_all()
        self.border_path = [0, 0, 0, 0]

        # Event connection:
        self.connect("draw", self._draw)
        self.connect("destroy", Gtk.main_quit)
        self.connect('composited-changed', self._composited_changed_event)
        self.wnck_screen.connect("active-window-changed", self._active_window_changed_event)

        # Call initial events
        self._composited_changed_event(None)
        self._active_window_changed_event(None, None)
        self._geometry_changed_event(None)

    # This triggers every time the window composited state changes.
    # https://docs.gtk.org/gtk3/signal.Widget.composited-changed.html
    def _composited_changed_event(self, _arg):
        if self.screen.is_composited():
            self.move(0, 0)
        else:
            self.move(1e6, 1e6)
            subprocess.Popen(["notify-send", "--app-name=xborder",
                            "xborders requires a compositor. Resuming once a compositor is running."])

    # Avoid memory leaks
    old_window = None
    old_signals_to_disconnect = [None, None]

    def is_alone_in_workspace(self) -> bool:
        workspace = Wnck.Screen.get_active_workspace(self.wnck_screen)
        windows = Wnck.Screen.get_windows(self.wnck_screen)
        windows_on_workspace = list(filter(lambda w: w.is_visible_on_workspace(workspace), windows))
        return len(windows_on_workspace) == 1

    # This event will trigger every active window change, it will queue a border to be drawn and then do nothing.
    # See: Signals available for the Wnck.Screen class:
    # https://lazka.github.io/pgi-docs/Wnck-3.0/classes/Screen.html#signals Signals available for the Wnck.Window
    # class: https://lazka.github.io/pgi-docs/Wnck-3.0/classes/Window.html#signals
    def _active_window_changed_event(self, _screen, _previous_active_window) -> None:
        if self.old_window and len(self.old_signals_to_disconnect) > 0:
            for sig_id in self.old_signals_to_disconnect:
                GObject.signal_handler_disconnect(self.old_window, sig_id)

        self.old_signals_to_disconnect = []
        self.old_window = None

        active_window = self.wnck_screen.get_active_window()

        self.border_path = [0, 0, 0, 0]
        if active_window != None and not (GlobalConfig.smartHideBorder and self.is_alone_in_workspace()):
            # Find if the window has a 'geometry-changed' event connected.

            geom_signal_id = GObject.signal_lookup('geometry-changed', active_window)
            state_signal_id = GObject.signal_lookup('state-changed', active_window)
            geom_has_event_connected = GObject.signal_has_handler_pending(active_window, geom_signal_id, 0, False)
            state_has_event_connected = GObject.signal_has_handler_pending(active_window, state_signal_id, 0, False)

            # if it doesn't have one.
            if not geom_has_event_connected:
                # Connect it.
                # Has to be done this way in order to not connect an event
                # every time the active window changes, thus, drawing unnecesary frames.
                sig_id = active_window.connect('geometry-changed', self._geometry_changed_event)
                self.old_signals_to_disconnect.append(sig_id)

            if not state_has_event_connected:
                sig_id = active_window.connect('state-changed', self._state_changed_event)
                self.old_signals_to_disconnect.append(sig_id)

            self.old_window = active_window

            self._calc_border_geometry(active_window)
        self.queue_draw()

    def _state_changed_event(self, active_window, _changed_mask, new_state):
        if new_state & Wnck.WindowState.FULLSCREEN != 0:
            self._calc_border_geometry(active_window)
        self.queue_draw()

    # This is weird, "_window_changed" is not necessarily the active window,
    # it is the window which receives the signal of resizing and is not necessarily
    # the active window, this means the border will get drawn on other windows.
    def _geometry_changed_event(self, _window_changed):
        active_window = self.wnck_screen.get_active_window()
        if active_window is None or (active_window.get_state() & Wnck.WindowState.FULLSCREEN != 0):
            self.border_path = [0, 0, 0, 0]
        else:
            self._calc_border_geometry(active_window)
        self.queue_draw()

    def _calc_border_geometry(self, window):
        if (window.get_state() & Wnck.WindowState.FULLSCREEN != 0):
            self.border_path = [0, 0, 0, 0]
            return
        # window.get_geometry() works better than window.get_client-geometry() which is odd
        x, y, w, h = window.get_geometry()

        # Inside
        if GlobalConfig.borderMode == xborderConfig.BorderMode.INSIDE:
            x += GlobalConfig.borderThickness / 2
            y += GlobalConfig.borderThickness / 2
            w -= GlobalConfig.borderThickness
            h -= GlobalConfig.borderThickness

        # Outside
        elif GlobalConfig.borderMode == xborderConfig.BorderMode.OUTSIDE:
            x -= GlobalConfig.borderThickness / 2
            y -= GlobalConfig.borderThickness / 2
            w += GlobalConfig.borderThickness
            h += GlobalConfig.borderThickness

        # Offsets

        w += GlobalConfig.offsets[0] or 0
        h += GlobalConfig.offsets[1] or 0

        x -= GlobalConfig.offsets[2] or 0
        w += GlobalConfig.offsets[2] or 0

        y -= GlobalConfig.offsets[3] or 0
        h += GlobalConfig.offsets[3] or 0

        # Center
        self.border_path = [x, y, w, h]

    def _draw(self, _wid, ctx):
        ctx.save()
        if self.border_path != [0, 0, 0, 0]:
            x, y, w, h = self.border_path
            if GlobalConfig.borderThickness > 0:
                radius = GlobalConfig.borderRadius
                if radius > 0:
                    degrees = 0.017453292519943295  # pi/180
                    ctx.arc(x + w - radius, y + radius, radius, -90 * degrees, 0 * degrees)
                    ctx.arc(x + w - radius, y + h - radius, radius, 0 * degrees, 90 * degrees)
                    ctx.arc(x + radius, y + h - radius, radius, 90 * degrees, 180 * degrees)
                    ctx.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
                    ctx.close_path()
                else:
                    ctx.rectangle(x, y, w, h)

                ctx.set_source_rgba(GlobalConfig.borderColor.r, GlobalConfig.borderColor.g, GlobalConfig.borderColor.b, GlobalConfig.borderColor.a)
                ctx.set_line_width(GlobalConfig.borderThickness)
                ctx.stroke()
        ctx.restore()

def main():
    try:
        GlobalConfig.ParseCmlArgs()
    except:
        subprocess.Popen(["notify-send", "--app-name=xborder",
                            "xborders Config Error", "Config was changed in v4, check help command or documentation."])
        return
    if GlobalConfig.printVersion:
        version = get_version()
        latest_version = get_latest_version()
        print(f"xborders v{version}, (latest v{latest_version})")
        return
    
    root = Gdk.get_default_root_window()
    root.get_screen()
    screen_width, screen_height = get_screen_size(Gdk.Display.get_default())
    Highlight(screen_width, screen_height)
    Gtk.main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
else:
    print(
        "xborders: This program is not meant to be imported to other Python modules. Please run xborders as a "
        "standalone script!")
