#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of ppaurl
#
# Copyright (C) 2016-2017 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Vte', '2.91')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Vte
import sys
import comun
from comun import _
from doitinbackground import DoItInBackground
from progreso import Progreso
import utils

MARGIN = 5


def joiner(args):
    if len(args) == 1:
        return args[0]
    elif len(args) == 2:
        return ' and '.join(args)
    elif len(args) > 2:
        return ', '.join(args[:-2]) + ', ' + ' and '.join(args[-2:])
    else:
        return ''


class SmartTerminal(Vte.Terminal):
    def __init__(self, parent):
        Vte.Terminal.__init__(self)
        self.parent = parent
        '''
        self.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ['/bin/sh'],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )
        '''
    def execute(self, commands):
        diib = DoItInBackground(self, commands)
        progreso = Progreso('Adding new ppa', self.parent, len(commands))
        diib.connect('done_one', progreso.increase)
        diib.connect('ended', progreso.close)
        diib.connect('ended', self.on_ended)
        progreso.connect('i-want-stop', diib.stop)
        diib.start()

    def on_ended(self, diib, ok):
        if ok is True:
            kind = Gtk.MessageType.INFO
            if len(self.apps) > 1:
                message = _('Install packages')
            else:
                message = _('Install package')
        else:
            kind = Gtk.MessageType.ERROR
            message = _('Some packages could be installed')
        dialog = Gtk.MessageDialog(self.parent, 0, kind,
                                   Gtk.ButtonsType.OK,
                                   message)
        dialog.run()
        dialog.destroy()
        Gtk.main_quit()


class GAptInDialog(Gtk.Window):
    def __init__(self, args):
        Gtk.Window.__init__(self)
        if len(args) < 2:
            Gtk.main_quit()
        self.set_title(_('Install package'))
        self.connect('delete-event', Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_icon_from_file(comun.ICON)
        self.set_size_request(600, 50)
        grid = Gtk.Grid()
        grid.set_margin_bottom(MARGIN)
        grid.set_margin_left(MARGIN)
        grid.set_margin_right(MARGIN)
        grid.set_margin_top(MARGIN)

        grid.set_column_spacing(MARGIN)
        grid.set_row_spacing(MARGIN)
        self.add(grid)

        if args[1].find('apt://') > -1:
            self.apps = args[1].split('apt://')[1].split(',')
        elif args[1].find('apt:') > -1:
            self.apps = args[1].split('apt:')[1].split(',')
        else:
            Gtk.main_quit()
        if len(self.apps) > 0:
            label = Gtk.Label(_('Install this packages: %s?') % (
                joiner(self.apps)))
        label.set_alignment(0, 0.5)
        grid.attach(label, 0, 0, 2, 1)
        expander = Gtk.Expander()
        expander.connect('notify::expanded', self.on_expanded)
        grid.attach(expander, 0, 1, 2, 2)

        alignment = Gtk.Alignment()
        # alignment.set_padding(1, 0, 2, 2)
        alignment.props.xscale = 1
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.terminal = SmartTerminal(self)
        scrolledwindow.add(self.terminal)
        alignment.add(scrolledwindow)
        expander.add(alignment)

        button_ok = Gtk.Button(_('Ok'))
        grid.attach(button_ok, 0, 3, 1, 1)
        button_ok.connect('clicked', self.on_button_ok_clicked)
        button_cancel = Gtk.Button(_('Cancel'))
        button_cancel.connect('clicked', self.on_button_cancel_clicked)
        grid.attach(button_cancel, 1, 3, 1, 1)

        self.is_added = False
        self.show_all()

    def on_expanded(self, widget, data):
        if widget.get_property('expanded') is True:
            self.set_size_request(600, 200)
        else:
            self.set_size_request(600, 50)
            self.resize(600, 50)

    def on_button_cancel_clicked(self, button):
        Gtk.main_quit()

    def on_button_ok_clicked(self, button):
        if len(self.apps) > 0:
            commands = []
            for app in self.apps:
                if not utils.is_package_installed(app):
                    commands.append('apt install %s' % app)
        print(commands)
        self.terminal.execute(commands)


def main(args):
    print(args)
    if len(args) < 2:
        args.append('apt://my-weather-indicator')
    GAptInDialog(args)
    Gtk.main()


if __name__ == '__main__':
    main(sys.argv)
    exit(0)
