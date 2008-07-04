# -*- coding: UTF-8 -*-
import gtk, re, pango
from SpiffGtkWidgets.AnnotatedTextView import AnnotatedTextView

bullet_point_re = re.compile(r'^(?:\d+\.|[\*\-])$')

class SmartTextView(AnnotatedTextView):
    def __init__(self, *args, **kwargs):
        AnnotatedTextView.__init__(self, *args, **kwargs)
        buffer            = self.get_buffer()
        self.bullet_point = u'•'
        self.first_li_tag = buffer.create_tag('first-list-item',
                                              left_margin = 30)
        self.li_tag       = buffer.create_tag('list-item',
                                              left_margin        = 30,
                                              pixels_above_lines = 12)
        self.bullet_tag   = buffer.create_tag('list-item-bullet',
                                              weight = pango.WEIGHT_ULTRABOLD)
        buffer.connect_after('insert-text', self._on_buffer_insert_text)


    def _at_bullet_point(self, buffer, iter):
        end = iter.copy()
        end.forward_find_char(lambda x, d: x == ' ')
        if end.is_end() or end.get_line() != iter.get_line():
            return False
        text = buffer.get_text(iter, end)
        if bullet_point_re.match(text):
            return True
        return False


    def _on_buffer_insert_text(self, buffer, iter, text, length):
        iter = iter.copy()
        iter.backward_chars(length)
        iter.set_line(iter.get_line())
        while not iter.is_end():
            if not self._at_bullet_point(buffer, iter):
                iter.forward_line()
                continue

            # Replace the item by a bullet point.
            end = iter.copy()
            end.forward_find_char(lambda x, d: x == ' ')
            buffer.delete(iter, end)
            buffer.insert(iter, self.bullet_point)
            iter.set_line(iter.get_line())

            # Markup the bullet point.
            end = iter.copy()
            end.forward_find_char(lambda x, d: x == ' ')
            buffer.apply_tag(self.bullet_tag, iter, end)

            # Markup the list item.
            end.forward_to_line_end()
            if iter.get_line() == 0:
                buffer.apply_tag(self.first_li_tag, iter, end)
            else:
                buffer.apply_tag(self.li_tag, iter, end)
            iter.forward_line()
