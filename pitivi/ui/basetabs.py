# PiTiVi , Non-linear video editor
#
#       ui/basetabs.py
#
# Copyright (c) 2005, Edward Hervey <bilboed@bilboed.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import gtk
from pitivi.ui.common import SPACING
from pitivi.settings import GlobalSettings

class BaseTabs(gtk.Notebook):

    def __init__(self, app, hide_hpaned=False):
        """
        Initialize the notebook widget
        """
        gtk.Notebook.__init__(self)
        self.set_border_width(SPACING)
        self.set_tab_pos(gtk.POS_TOP)
        self.connect("create-window", self._createWindowCb)

        self._hide_hpaned = hide_hpaned
        self.app = app
        self.settings = app.settings  # To save/restore states of detached tabs

        notebook_widget_settings = self.get_settings()
        notebook_widget_settings.props.gtk_dnd_drag_threshold = 1

    def append_page(self, child, label):
        child_name = label.get_text()
        #child_name = child.__name__ # Won't work, because it's private...
        # Create default settings for each detachable widget
        GlobalSettings.addConfigSection("tabs - " + child_name)
        GlobalSettings.addConfigOption(child_name + "Docked",
            section="tabs - " + child_name,
            key="docked",
            default=True)
        GlobalSettings.addConfigOption(child_name + "Width",
            section="tabs - " + child_name,
            key="width",
            default=320)
        GlobalSettings.addConfigOption(child_name + "Height",
            section="tabs - " + child_name,
            key="height",
            default=240)
        GlobalSettings.addConfigOption(child_name + "X",
            section="tabs - " + child_name,
            key="x-pos",
            default=0)
        GlobalSettings.addConfigOption(child_name + "Y",
            section="tabs - " + child_name,
            key="y-pos",
            default=0)

        gtk.Notebook.append_page(self, child, label)
        self._set_child_properties(child, label)
        child.show()
        label.show()
        # TODO: if the child_name + "Docked" setting is False, emit create-window

    def _set_child_properties(self, child, label):
        self.child_set_property(child, "detachable", True)
        self.child_set_property(child, "tab-expand", False)
        self.child_set_property(child, "tab-fill", True)
        label.props.xalign = 0.0

    def _detachedComponentWindowDestroyCb(self, window, child,
            original_position, label):
        notebook = window.child
        position = notebook.child_get_property(child, "position")
        notebook.remove_page(position)
        label = gtk.Label(label)
        self.insert_page(child, label, original_position)
        self._set_child_properties(child, label)
        self.child_set_property(child, "detachable", True)

        if self._hide_hpaned:
            self._showSecondHpanedInMainWindow()

    def _detachedComponentWindowConfiguredCb(self, window, event, child_label):
        """
        When the user configures the detached window
        (changes its size, position, etc.), save the settings.
        """
        # Use a different variable name depending on the widget
        config_key = child_label
        setattr(self.settings, config_key + "Width", event.width)
        setattr(self.settings, config_key + "Height", event.height)
        setattr(self.settings, config_key + "X", event.x)
        setattr(self.settings, config_key + "Y", event.y)

    def _createWindowCb(self, from_notebook, child, x, y):
        original_position = self.child_get_property(child, "position")
        label = self.child_get_property(child, "tab-label")
        window = gtk.Window()
        window.set_title(label)
        # TODO: restore the saved size and other settings
        window.set_default_size(600, 400)
        window.connect("configure-event", self._detachedComponentWindowConfiguredCb, label)
        window.connect("destroy", self._detachedComponentWindowDestroyCb,
                child, original_position, label)
        notebook = gtk.Notebook()
        notebook.props.show_tabs = False
        window.add(notebook)

        window.show_all()
        # set_uposition is deprecated but what should I use instead?
        window.set_uposition(x, y)

        if self._hide_hpaned:
            self._hideSecondHpanedInMainWindow()

        return notebook

    def _hideSecondHpanedInMainWindow(self):
        self.app.gui.mainhpaned.remove(self.app.gui.secondhpaned)
        self.app.gui.secondhpaned.remove(self.app.gui.projecttabs)
        self.app.gui.secondhpaned.remove(self.app.gui.propertiestabs)
        self.app.gui.mainhpaned.pack1(self.app.gui.projecttabs, resize= True,
                                      shrink=False)

    def _showSecondHpanedInMainWindow(self):
        self.app.gui.mainhpaned.remove(self.app.gui.projecttabs)
        self.app.gui.secondhpaned.pack1(self.app.gui.projecttabs,
                                        resize= True, shrink=False)
        self.app.gui.secondhpaned.pack2(self.app.gui.propertiestabs,
                                        resize= True, shrink=False)
        self.app.gui.mainhpaned.pack1(self.app.gui.secondhpaned,
                                      resize= True, shrink=False)
