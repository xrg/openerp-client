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
import gtk, pango, time, gobject, string
from Annotation     import Annotation
from UndoInsertText import UndoInsertText
from UndoDeleteText import UndoDeleteText
from UndoApplyTag   import UndoApplyTag
from UndoRemoveTag  import UndoRemoveTag
from UndoCollection import UndoCollection
import Features

class TextBuffer(gtk.TextBuffer):
    def __init__(self, *args, **kwargs):
        gtk.TextBuffer.__init__(self, *args)
        self.undo_stack      = []
        self.redo_stack      = []
        self.current_undo    = UndoCollection(self)
        self.lock_undo       = False
        self.max_undo        = 250
        self.max_redo        = 250
        self.undo_freq       = 300 # minimum milliseconds between actions
        self.undo_timeout_id = None
        self.user_action     = 0
        self.active_features = []
        self.annotations     = {}

        # Connect signals.
        self.connect('insert-text',       self._on_insert_text)
        self.connect('delete-range',      self._on_delete_range)
        self.connect('apply-tag',         self._on_apply_tag)
        self.connect('remove-tag',        self._on_remove_tag)
        self.connect('begin-user-action', self._on_begin_user_action)
        self.connect('end-user-action',   self._on_end_user_action)

        # Create text styles.
        self.create_tag('bold',      weight    = pango.WEIGHT_BOLD)
        self.create_tag('italic',    style     = pango.STYLE_ITALIC)
        self.create_tag('underline', underline = pango.UNDERLINE_SINGLE)

        # Enable other features.
        features = (
            #('list-indent', True, Features.ListIndent, ()),
        )
        for name, default, feature, feature_args in features:
            active = kwargs.get(name, default)
            if active:
                self.activate_feature(feature, *feature_args)
        self._update_timestamp()


    def activate_feature(self, feature, *args):
        self.active_features.append(feature(self, *args))


    def offset_range_has_tag(self, start, end, tag_name):
        tags_list = self.get_tags_at_offset(start, end)
        for tags in tags_list:
            names = [t.get_property('name') for t in tags]
            if tag_name not in names:
                return False
        return True


    def selection_has_tag(self, tag_name):
        # Check whether there is a selection.
        bounds = self.get_selection_bounds()
        if bounds:
            start = bounds[0].get_offset()
            end   = bounds[1].get_offset()
            return self.offset_range_has_tag(start, end, tag_name)

        # So nothing is selected. Get the position of the cursor.
        mark = self.get_mark('insert')
        iter = self.get_iter_at_mark(mark)

        # Get a range of one char around that mark.
        iter.backward_char()
        start = iter.get_offset()
        iter.forward_chars(2)
        end = iter.get_offset()

        # Return True if both chars have the given tag, False otherwise.
        return self.offset_range_has_tag(start, end, tag_name)


    def tag_selection(self, tag_name):
        bounds = self.get_selection_bounds()
        if not bounds:
            return
        self.apply_tag_by_name(tag_name, *bounds)


    def untag_selection(self, tag_name):
        bounds = self.get_selection_bounds()
        if not bounds:
            return
        tag_list = self.get_tags_at_offset(bounds[0].get_offset(),
                                           bounds[1].get_offset())
        for tags in tag_list:
            for tag in tags:
                name = tag.get_property('name')
                if name == tag_name:
                    self.remove_tag(tag, *bounds)


    def toggle_selection_tag(self, tag_name):
        if self.selection_has_tag(tag_name):
            self.untag_selection(tag_name)
        else:
            self.tag_selection(tag_name)


    def _cancel_undo_timeout(self):
        if self.undo_timeout_id is None:
            return
        gobject.source_remove(self.undo_timeout_id)
        self.undo_timeout_id = None
        self.end_user_action()


    def _update_timestamp(self):
        if self.undo_timeout_id is not None:
            gobject.source_remove(self.undo_timeout_id)
        else:
            self.begin_user_action()
        self.undo_timeout_id = gobject.timeout_add(self.undo_freq,
                                                   self._cancel_undo_timeout)


    def _on_insert_text(self, buffer, start, text, length):
        if self.lock_undo:
            return
        self._update_timestamp()
        item = UndoInsertText(self, start, text)
        self.current_undo.add(item)
        self.emit('undo-stack-changed')


    def _on_delete_range(self, buffer, start, end):
        if self.lock_undo:
            return
        self._update_timestamp()
        item = UndoDeleteText(self, start, end)
        self.current_undo.add(item)


    def _on_apply_tag(self, buffer, tag, start, end):
        if self.lock_undo:
            return
        if tag.get_property('name') == 'gtkspell-misspelled':
            return
        self._update_timestamp()
        item = UndoApplyTag(self, start, end, tag)
        self.current_undo.add(item)


    def _on_remove_tag(self, buffer, tag, start, end):
        if self.lock_undo:
            return
        if tag.get_property('name') == 'gtkspell-misspelled':
            return
        self._update_timestamp()
        item = UndoRemoveTag(self, start, end, tag)
        self.current_undo.add(item)


    def _on_begin_user_action(self, buffer):
        self.user_action += 1


    def _on_end_user_action(self, buffer):
        self.user_action -= 1
        if self.user_action != 0:
            return
        if self.current_undo is None:
            return
        if len(self.current_undo.children) == 0:
            return
        self._undo_add(self.current_undo)
        self.redo_stack = []
        self.current_undo = UndoCollection(self)


    def _undo_add(self, item):
        self.undo_stack.append(item)
        while len(self.undo_stack) >= self.max_undo:
            self.undo_stack.pop(0)
        self.emit('undo-stack-changed')


    def _redo_add(self, item):
        self.redo_stack.append(item)
        while len(self.redo_stack) >= self.max_redo:
            self.redo_stack.pop(0)
        self.emit('undo-stack-changed')


    def insert_at_offset(self, offset, text):
        iter = self.get_iter_at_offset(offset)
        self.insert(iter, text)


    def delete_range_at_offset(self, start, end):
        start = self.get_iter_at_offset(start)
        end   = self.get_iter_at_offset(end)
        self.delete(start, end)


    def apply_tag_at_offset(self, tag, start, end):
        start = self.get_iter_at_offset(start)
        end   = self.get_iter_at_offset(end)
        self.apply_tag(tag, start, end)


    def remove_tag_at_offset(self, tag, start, end):
        start = self.get_iter_at_offset(start)
        end   = self.get_iter_at_offset(end)
        self.remove_tag(tag, start, end)


    def get_tags_at_offset(self, start, end):
        taglist = []
        iter    = self.get_iter_at_offset(start)
        while True:
            taglist.append(iter.get_tags())
            iter.forward_char()
            if iter.get_offset() >= end:
                break
        return taglist


    def apply_tags_at_offset(self, taglist, start, end):
        end   = self.get_iter_at_offset(start + 1)
        start = self.get_iter_at_offset(start)
        for tags in taglist:
            for tag in tags:
                self.apply_tag(tag, start, end)
            start.forward_char()
            end.forward_char()


    def can_undo(self):
        if self.current_undo is not None \
          and len(self.current_undo.children) > 0:
            return True
        return len(self.undo_stack) > 0


    def undo(self):
        self._cancel_undo_timeout()
        if len(self.undo_stack) == 0:
            return
        self.lock_undo = True
        item = self.undo_stack.pop()
        item.undo()
        self._redo_add(item)
        self.lock_undo = False


    def flush_undo_stack(self):
        self._cancel_undo_timeout()
        if len(self.undo_stack) == 0:
            return
        self.undo_stack = []
        self.emit('undo-stack-changed')


    def can_redo(self):
        return len(self.redo_stack) > 0


    def redo(self):
        self._cancel_undo_timeout()
        if len(self.redo_stack) == 0:
            return
        self.lock_undo = True
        item = self.redo_stack.pop()
        item.redo()
        self._undo_add(item)
        self.lock_undo = False


    def flush_redo_stack(self):
        self._cancel_undo_timeout()
        if len(self.redo_stack) == 0:
            return
        self.redo_stack = []
        self.emit('undo-stack-changed')


    def add_annotation(self, annotation):
        self.annotations[annotation.start_mark] = annotation
        self.emit('annotation-added', annotation)


    def remove_annotation(self, annotation):
        self.delete_mark(annotation.start_mark) #FIXME: don't do this here
        del self.annotations[annotation.start_mark]
        self.emit('annotation-removed', annotation)


    def remove_annotations(self):
        for annotation in self.annotations.values():
            self.remove_annotation(annotation)


    def get_annotation_from_mark(self, mark):
        return self.annotations[mark]


    def get_annotations(self):
        return self.annotations.values()


    def get_annotations_xml(self):
        xml = '<xml>\n'
        for annotation in self.annotations.itervalues():
            xml += annotation.toxml()
        return xml + '</xml>\n'


    def add_annotations_from_xml(self, xml):
        from xml.dom.minidom import parseString
        root = parseString(xml)
        for node in root.getElementsByTagName('annotation'):
            self.add_annotation(Annotation.fromxml(self, node))


    def _collect_links(self, tag, data):
        link = tag.get_data('link')
        if not link:
            return
        name           = tag.get_property('name')
        self.link_xml += '<link name="%s">%s</link>\n' % (name, link)


    def _merge_data(self, **kwargs):
        """
        Takes n different strings (or binary data) and merges them into one
        string such that they can be split later.
        """
        index = ''
        data  = ''
        pos   = 0
        for key, value in kwargs.iteritems():
            value  = str(value)
            end    = pos + len(value)
            tuple  = [str(pos), str(end), key]
            index += '|'.join(tuple) + "\n"
            data  += value
            pos    = end
        return index + "\n" + data


    def _unmerge_data(self, string):
        """
        Takes a string that was created using _merge_data and splits it
        into the original data.
        """
        result = dict()
        string = str(string)
        if string == '':
            return result
        index_end = string.index("\n\n")
        index     = string[:index_end]
        data      = string[index_end + 2:]
        for line in index.split("\n"):
            start, end, name = line.split('|')
            result[name]     = data[int(start):int(end)]
        return result


    def dump(self):
        """
        Serializes the content of the buffer, including annotations and
        links.
        """
        # Serialize the content of the buffer. This does not include the
        # annotations or data that is attached to tags.
        self.register_serialize_tagset()
        format  = 'application/x-gtk-text-buffer-rich-text'
        bounds  = self.get_bounds()
        content = self.serialize(self, format, *bounds)

        # Secure the 'link' data that may be attached to a tag.
        self.link_xml = '<xml>\n'
        tag_table     = self.get_tag_table()
        tag_table.foreach(self._collect_links)
        self.link_xml += '</xml>\n'

        # Also attach the annotation xml.
        return self._merge_data(content     = content,
                                links       = self.link_xml,
                                annotations = self.get_annotations_xml())


    def restore(self, dump):
        from xml.dom.minidom import parseString
        data = self._unmerge_data(dump)
        self.delete(*self.get_bounds())

        # Parse links and remove collisions from the tag table.
        tag_table = self.get_tag_table()
        links     = {}
        root      = parseString(data['links'])
        for node in root.getElementsByTagName('link'):
            name = node.getAttribute('name')
            link = node.childNodes[0].data
            links[name] = link

        # Restore the content first.
        format = 'application/x-gtk-text-buffer-rich-text'
        self.register_deserialize_tagset()
        self.deserialize_set_can_create_tags(format, False)
        self.deserialize(self, format, self.get_start_iter(), data['content'])

        # Restore links.
        for name, link in links.iteritems():
            tag = tag_table.lookup(name)
            if tag:
                tag.set_data('link', link)

        # Restore annotations.
        self.remove_annotations()
        self.add_annotations_from_xml(data['annotations'])


gobject.signal_new('annotation-added',
                   TextBuffer,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.signal_new('annotation-removed',
                   TextBuffer,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.signal_new('undo-stack-changed',
                   TextBuffer,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   ())

gobject.type_register(TextBuffer)
