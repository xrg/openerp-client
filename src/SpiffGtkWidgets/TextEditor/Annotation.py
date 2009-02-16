# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Samuel Abels, http://debain.org
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
import gtk
import pango

class Annotation(object):
    def __init__(self, start_mark, end_mark = None):
        self.start_mark     = start_mark
        self.end_mark       = end_mark
        self.buffer         = gtk.TextBuffer()
        self.title          = ''
        self.title_len      = 0
        self.bg_color       = None
        self.border_color   = None
        self.text_color     = None
        self.display_buffer = None
        self.buffer.create_tag('title',
                               editable = False,
                               weight   = pango.WEIGHT_BOLD)
        self.buffer.connect('mark-set', self._on_buffer_mark_set)


    def _on_buffer_mark_set(self, buffer, iter, mark):
        if mark.get_name() not in ('selection_bound', 'insert'):
            return
        # Move the mark to the text start.
        if iter.get_offset() < self.title_len:
            iter = buffer.get_iter_at_offset(self.title_len)
            buffer.move_mark(mark, iter)


    def set_display_buffer(self, buffer):
        self.display_buffer = buffer


    def get_display_buffer(self):
        return self.display_buffer


    def set_bg_color(self, color):
        self.bg_color = color


    def get_bg_color(self):
        return self.bg_color


    def set_border_color(self, color):
        self.border_color = color


    def get_border_color(self):
        return self.border_color


    def set_text_color(self, color):
        self.text_color = color


    def get_text_color(self):
        return self.text_color


    def set_title(self, title, force_colon = False):
        # Clear the old title.
        start = self.buffer.get_start_iter()
        end   = self.buffer.get_iter_at_offset(self.title_len)
        self.buffer.delete(start, end)

        # Add the new title and make it non-editable.
        have_text  = self.buffer.get_char_count() > 0
        self.title = title
        if have_text or force_colon:
            title = '%s: ' % title
        self.title_len = len(title)
        start = self.buffer.get_start_iter()
        self.buffer.insert(start, title)
        start = self.buffer.get_start_iter()
        end   = self.buffer.get_iter_at_offset(len(title))
        self.buffer.apply_tag_by_name('title', start, end)


    def get_title(self):
        return self.title


    def set_text(self, text):
        # Clear the old editable text.
        start = self.buffer.get_start_iter()
        end   = self.buffer.get_end_iter()
        self.buffer.delete_interactive(start, end, True)

        # Append the new text.
        self.buffer.insert(end, text)
        self.set_title(self.title)


    def get_text(self):
        start = self.buffer.get_iter_at_offset(self.title_len)
        end   = self.buffer.get_end_iter()
        return self.buffer.get_text(start, end)


    @classmethod
    def _get_xml_text(self, nodes):
        return ''.join([n.data for n in nodes if n.nodeType == n.TEXT_NODE])


    @classmethod
    def _handle_xml_title(self, annotation, node):
        annotation.set_title(self._get_xml_text(node.childNodes))


    @classmethod
    def _handle_xml_text(self, annotation, node):
        annotation.set_text(self._get_xml_text(node.childNodes))


    @classmethod
    def fromxml(self, buffer, node):
        """
        Returns a new instance of an annotation that is assigned to the
        given buffer. node is a XML dom element.
        """
        name       = node.getAttribute('name')
        start      = int(node.getAttribute('start'))
        end        = int(node.getAttribute('end'))
        title_node = node.getElementsByTagName('title')[0]
        text_node  = node.getElementsByTagName('text')[0]
        start_iter = buffer.get_iter_at_offset(max(0, start))
        end_iter   = buffer.get_iter_at_offset(max(0, end))
        start_mark = buffer.create_mark(name,          start_iter)
        end_mark   = buffer.create_mark(name + '_end', end_iter)
        annotation = Annotation(start_mark, end_mark)
        annotation._handle_xml_title(annotation, title_node)
        annotation._handle_xml_text (annotation, text_node)
        return annotation


    def toxml(self):
        """
        Returns an XML representation of the annotation. The XML also
        contains the "mark" at which the node is added to the buffer.
        """
        buffer = self.display_buffer
        if buffer:
            start = buffer.get_iter_at_mark(self.start_mark).get_offset()
        else:
            start = -1
        attrs = (self.start_mark.get_name(), start, start)
        xml   = '<annotation name="%s" start="%d" end="%d">' % attrs
        xml  += '<title>%s</title>'                          % self.title
        xml  += '<text>%s</text>'                            % self.get_text()
        xml  += '</annotation>'
        return xml
