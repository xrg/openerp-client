# Copyright (C) 2009 Samuel Abels <http://debain.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import gobject, gtk, os.path, gtk.glade

xml = os.path.join(os.path.dirname(__file__), 'preferences.glade')

class Preferences(gtk.EventBox):
    def __init__(self, element):
        gtk.EventBox.__init__(self)
        self.xml      = gtk.glade.XML(xml, 'table_main')
        self.table    = self.xml.get_widget('table_main')
        self.treeview = self.xml.get_widget('treeview_options')
        self.add(self.table)
        self.xml.signal_autoconnect(self)
