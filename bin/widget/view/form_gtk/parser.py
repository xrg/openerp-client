# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import tools
import interface

import widget.view.interface
from observator import oregistry, Observable

import gtk

import common
import service
import rpc

import copy

import options


class Button(Observable):
    def __init__(self, attrs={}):
        super(Button, self).__init__()
        self.attrs = attrs
        args = {
            'label': attrs.get('string', 'unknown')
        }
        self.widget = gtk.Button(**args)
        self.widget.set_flags(gtk.CAN_DEFAULT)

        readonly = bool(int(attrs.get('readonly', '0')))
        self.set_sensitive(not readonly)

        if attrs.get('icon', False):
            try:
                stock = attrs['icon']
                icon = gtk.Image()
                icon.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
                self.widget.set_image(icon)
            except Exception,e:
                import logging
                log = logging.getLogger('common')
                log.warning(_('Wrong icon for the button !'))

#           self.widget.set_use_stock(True)
#       self.widget.set_label(args['label'])
        tooltip = attrs.get('help')
        if tooltip:
            self.widget.set_tooltip_markup(tooltip)
        self.widget.show()
        self.widget.connect('clicked', self.button_clicked)

        default_width = self.widget.size_request()[0]
        default_height = self.widget.size_request()[1]
        max_width = self.widget.get_screen().get_width()/5
        if default_width > max_width:
            self.widget.set_size_request(max_width, default_height)

    def grab_focus(self):
        self.widget.grab_focus()

    def hide(self):
        return self.widget.hide()

    def show(self):
        return self.widget.show()

    def set_sensitive(self, value):
        return self.widget.set_sensitive(value)

    def button_clicked(self, widget):
        model = self.form.screen.current_model
        self.form.set_value()
        button_type = self.attrs.get('special', '')

        if button_type=='cancel':
            self.form.screen.window.destroy()
            if 'name' in self.attrs.keys():
                type_button = self.attrs.get('type','object')

                if type_button == 'action':
                    obj = service.LocalService('action.main')
                    action_id = int(self.attrs['name'])

                    context_action = self.form.screen.context.copy()

                    if 'context' in self.attrs:
                        context_action.update(self.form.screen.current_model.expr_eval(self.attrs['context'], check_load=False))

                    obj.execute(action_id, {'model':self.form.screen.name, 'id': False, 'ids': [], 'report_type': 'pdf'}, context=context_action)

                elif type_button == 'object':
                    result = rpc.session.rpc_exec_auth(
                                '/object', 'execute',
                                self.form.screen.name,
                                self.attrs['name'],[], model.context_get())
                    datas = {}
                    obj = service.LocalService('action.main')
                    obj._exec_action(result,datas,context=self.form.screen.context)
                else:
                    raise Exception, 'Unallowed button type'

        elif model.validate():
            id = self.form.screen.save_current()
            model.get_button_action(self.form.screen, id, self.attrs)
            self.warn('misc-message', '')
        else:
            fields  = common.get_invalid_field(self.form.screen.current_model, self.form.screen.context)
            msg = ''
            for req, inv in fields:
                if inv:
                    msg += req + ' (<b>invisible</b>) '
                else:
                    msg += req
                msg += '\n'
            common.warning(_('Correct following red fields !\n\n%s')  % ( msg ),_('Input Error !'), parent=self.form.screen.current_view.window, to_xml=False)
            self.warn('misc-message', _('Invalid form, correct red fields !'), "red")
            self.form.screen.display()
            self.form.screen.current_view.set_cursor()



class StateAwareWidget(object):
    def __init__(self, widget, label=None, states=None):
        self.widget = widget
        self.label = label
        self.states = states or []
        self.frame_child = {}

    def __getattr__(self, a):
        return self.widget.__getattribute__(a)

    def state_set(self, state):
        if (not len(self.states)) or (state in self.states):
            self.widget.show()
        else:
            self.widget.hide()

    def attrs_set(self, model):
        sa = getattr(self.widget, 'attrs') or {}

        attrs_changes = eval(sa.get('attrs',"{}"),{'uid':rpc.session.uid})
        for k,v in attrs_changes.items():
            result = True
            result = result and tools.calc_condition(self, model, v)
            if k == 'invisible':
                if model and  model.state_attrs.get(sa['name']): 
                    model.state_attrs.get(sa['name'])['invisible'] = result
                func = ['show', 'hide'][bool(result)]
                getattr(self.widget, func)()
                if self.label:
                    getattr(self.label, func)()
            elif k == 'readonly':
                if isinstance(self.widget, gtk.Frame):
                    for name, wid in self.frame_child.iteritems():
                        self.set_sensitive(wid, result)
                else:
                    self.set_sensitive(self.widget, result)
    ## This method is hacked here because field labels that are readonly
    ## should not change their looks to readonly GTK widgets as it makes
    ## the label text very difficult to read in some themes.
    def set_sensitive(self, widget, value):
        if hasattr(widget, "get_children") and not \
            isinstance(widget, gtk.ComboBoxEntry):
            for wid in widget.get_children():
               self.set_sensitive(wid, value)
        if not isinstance(widget, gtk.Label):
            if hasattr(widget,'_readonly_set'):
                widget._readonly_set(value)
            else:
                widget.set_sensitive(not value)
        return True

class _container(object):
    def __init__(self):
        self.cont = []
        self.col = []
        self.sg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        self.trans_box = []
        self.trans_box_label = []

    def new(self, col=4):
        table = gtk.Table(1, col)
        table.set_homogeneous(False)
        table.set_col_spacings(3)
        table.set_row_spacings(0)
        table.set_border_width(1)
        self.cont.append( (table, 0, 0) )
        self.col.append( col )

    def get(self):
        return self.cont[-1][0]

    def pop(self):
        (table, x, y) = self.cont.pop()
        self.col.pop()
        return table

    def newline(self):
        (table, x, y) = self.cont[-1]
        if x>0:
            self.cont[-1] = (table, 0, y+1)
        table.resize(y+1,self.col[-1])

    def create_label(self, name, markup=False, align=1.0, wrap=False,
                     angle=None, width=None, fname=None, help=None, detail_tooltip=False):
        
        label = gtk.Label(name)
        eb = gtk.EventBox()
        eb.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        if markup:
            label.set_use_markup(True)
        self.trans_box_label.append((eb, name, fname))
        eb.add(label)
        
        def size_allocate(label, allocation):
            label.set_size_request( allocation.width - 2, -1 )
        if fname is None and name and len(name) > 50:
            label.connect( "size-allocate", size_allocate )
        uid = rpc.session.uid
        tooltip = ''
        if help:
            tooltip = '<span foreground="darkred"><b>%s</b></span>\n%s' % \
                        (tools.to_xml(name), tools.to_xml(help))
            label.set_markup('<sup><span foreground="darkgreen">?</span></sup>' + tools.to_xml(name))
        if detail_tooltip:
            tooltip += (help and '\n' or '') + detail_tooltip
        if tooltip:
            eb.set_tooltip_markup(tooltip)
        label.set_alignment(align, 0.5)
        if width:
            label.set_size_request(width, -1)
        label.set_line_wrap(bool(int(wrap)))
        if angle:
            label.set_angle(int(angle))
        return eb

    def wid_add(self, widget, label=None, xoptions=False, expand=False, ypadding=2, rowspan=1,
            colspan=1, translate=False, fname=None, fill=False, invisible=False):
        (table, x, y) = self.cont[-1]
        if colspan>self.col[-1]:
            colspan=self.col[-1]
        #Commented the following line in order to use colspan=4 and colspan=4 in same row
#        if colspan+x+a>self.col[-1]:
        if colspan+x>self.col[-1]:
            self.newline()
            (table, x, y) = self.cont[-1]
        yopt = False
        if expand:
            yopt = yopt | gtk.EXPAND
        if fill:
            yopt = yopt | gtk.FILL
        if not xoptions:
            xoptions = gtk.FILL|gtk.EXPAND

        if colspan == 1 and label:
            colspan = 2
        if label:
            table.attach(label, x, x+1, y, y+rowspan, yoptions=yopt,
                    xoptions=gtk.FILL, ypadding=ypadding, xpadding=2)

            real_label = label
            if isinstance(label, gtk.EventBox):
                real_label = label.child
            txt = real_label.get_text()
            if '_' in txt:
                real_label.set_text_with_mnemonic(txt)
                real_label.set_mnemonic_widget(widget)

        hbox = widget
        hbox.show_all()
        if translate:
            hbox = gtk.HBox(spacing=3)
            hbox.pack_start(widget)
            img = gtk.Image()
            img.set_from_stock('terp-translate', gtk.ICON_SIZE_MENU)
            ebox = gtk.EventBox()
            ebox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            self.trans_box.append((ebox, translate, fname, widget))

            ebox.add(img)
            hbox.pack_start(ebox, fill=False, expand=False)
            hbox.show_all()
        table.attach(hbox, x+int(bool(label)), x+colspan, y, y+rowspan,xoptions=xoptions, yoptions=yopt,
            ypadding=ypadding, xpadding=2)
        self.cont[-1] = (table, x+colspan, y)
        wid_list = table.get_children()
        wid_list.reverse()
        table.set_focus_chain(wid_list)
        if invisible:
            hbox.hide()

class parser_form(widget.view.interface.parser_interface):
    def __init__(self, window, parent=None, attrs=None, screen=None):
           super(parser_form, self).__init__(window, parent=parent, attrs=attrs,
                    screen=screen)
           self.widget_id = 0
           self.default_focus_field = False
           self.default_focus_button = False
           self.accepted_attr_list = ['type','domain','context','relation', 'widget','attrs',
                                      'digits','function','store','fnct_search','fnct_inv','fnct_inv_arg',
                                      'func_obj','func_method','related_columns','third_table','states',
                                      'translate','change_default','size','selection']

    def create_detail_tooltip(self, name='', field_attr={}):
        tooltip = '<span foreground="#009900"><b>%s:</b> %s - <b>%s:</b> %s' % \
                (_('Field'), tools.to_xml(name), _('Object'), tools.to_xml(field_attr.get('model','')))
        attributes = field_attr.keys()
        attributes.sort()
        for attr in attributes:
            if attr in self.accepted_attr_list:
                tooltip += '\n<b>%s:</b> %s' %(tools.to_xml(str(attr).capitalize()),tools.to_xml(str(field_attr[attr])))
        return tooltip + '</span>'

    def parse(self, model, root_node, fields, notebook=None, paned=None):
        dict_widget = {}
        saw_list = []   # state aware widget list
        attrs = tools.node_attributes(root_node)
        on_write = attrs.get('on_write', '')
        container = _container()
        container.new(col=int(attrs.get('col', 4)))
        self.container = container

        if not self.title:
            attrs = tools.node_attributes(root_node)
            self.title = attrs.get('string', 'Unknown')

        for node in root_node:
            attrs = tools.node_attributes(node)
            if node.tag=='image':
                icon = gtk.Image()
                icon.set_from_stock(attrs['name'], gtk.ICON_SIZE_DIALOG)
                container.wid_add(icon,colspan=int(attrs.get('colspan',1)),expand=int(attrs.get('expand',0)), ypadding=10, fill=int(attrs.get('fill', 0)))
            elif node.tag=='separator':
                orientation = attrs.get('orientation', 'horizontal')
                if orientation == 'vertical':
                    vbox = gtk.HBox(homogeneous=False, spacing=0)
                else:
                    vbox = gtk.VBox()
                if 'string' in attrs:
                    text = attrs.get('string', 'No String Attr.')
                    l = gtk.Label('<b>'+(text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'))+'</b>')
                    l.set_use_markup(True)
                    l.set_alignment(0.0, 0.5)
                    eb = gtk.EventBox()
                    eb.set_events(gtk.gdk.BUTTON_PRESS_MASK)
                    eb.add(l)
                    container.trans_box_label.append((eb, text, None))
                    vbox.pack_start(eb)
                if orientation == 'vertical':
                    vsep = gtk.VSeparator()
                    rowspan = int(attrs.get('rowspan', '1'))
                    vsep.set_size_request(1, 20*rowspan)
                    vbox.pack_start(vsep, False, False, 5)
                    xoptions = gtk.SHRINK
                else:
                    xoptions = False
                    vbox.pack_start(gtk.HSeparator())
                container.wid_add(vbox,colspan=int(attrs.get('colspan',1)), xoptions=xoptions,expand=int(attrs.get('expand',0)), ypadding=10, fill=int(attrs.get('fill', 0)))
            elif node.tag=='label':
                text = attrs.get('string', '')
                if not text:
                    for node in node:
                        text += node.text
                align = float(attrs.get('align', 0))

                eb = container.create_label(text, markup=True, align=align,
                                            width=int(attrs.get('width', -1)),
                                            angle=attrs.get('angle'),
                                            wrap=attrs.get('wrap', True),
                                            help=attrs.get('help'))


                container.trans_box_label.append((eb, text, None))

                container.wid_add(
                    eb,
                    colspan=int(attrs.get('colspan', 1)),
                    expand=False,
                    fill=int(attrs.get('fill', 0))
                )

            elif node.tag=='newline':
                container.newline()

            elif node.tag=='button':
                if attrs.get('invisible', False):
                    visval = eval(attrs['invisible'], {'context':self.screen.context})
                    if visval:
                        continue
                    
                if 'default_focus' in attrs and not self.default_focus_button:
                    attrs['focus_button'] = attrs['default_focus']
                    self.default_focus_button = True
              
                button = Button(attrs)
                
                states = [e for e in attrs.get('states','').split(',') if e]
                saw_list.append(StateAwareWidget(button, states=states))
                container.wid_add(button.widget, colspan=int(attrs.get('colspan', 1)))

            elif node.tag=='notebook':
                if attrs.get('invisible', False):
                    visval = eval(attrs['invisible'], {'context':self.screen.context})
                    if visval:
                        continue
                nb = gtk.Notebook()
                if attrs and 'tabpos' in attrs:
                    pos = {'up':gtk.POS_TOP,
                        'down':gtk.POS_BOTTOM,
                        'left':gtk.POS_LEFT,
                        'right':gtk.POS_RIGHT
                    }[attrs['tabpos']]
                else:
                    if options.options['client.form_tab'] == 'top':
                        pos = gtk.POS_TOP
                    elif options.options['client.form_tab'] == 'left':
                        pos = gtk.POS_LEFT
                    elif options.options['client.form_tab'] == 'right':
                        pos = gtk.POS_RIGHT
                    elif options.options['client.form_tab'] == 'bottom':
                        pos = gtk.POS_BOTTOM
                nb.set_tab_pos(pos)
                nb.set_border_width(3)
                container.wid_add(nb, colspan=attrs.get('colspan', 3), expand=True, fill=True )
                _, widgets, saws, on_write = self.parse(model, node, fields, nb)
                saw_list += saws
                dict_widget.update(widgets)

            elif node.tag=='page':
                if attrs.get('invisible', False):
                    visval = eval(attrs['invisible'], {'context':self.screen.context})
                    if visval:
                        continue
                if attrs and 'angle' in attrs:
                    angle = int(attrs['angle'])
                else:
                    angle = int(options.options['client.form_tab_orientation'])
                l = gtk.Label(attrs.get('string','No String Attr.'))
                l.attrs=attrs.copy()
                l.set_angle(angle)
                widget, widgets, saws, on_write = self.parse(model, node, fields, notebook)
                saw_list += saws
                dict_widget.update(widgets)
                notebook.append_page(widget, l)

            elif node.tag =='field':
                name = str(attrs['name'])
                del attrs['name']
                name = unicode(name)
                type = attrs.get('widget', fields[name]['type'])
                if 'selection' in attrs:
                    attrs['selection'] = fields[name]['selection']
                fields[name].update(attrs)
                fields[name]['model'] = model
                if not type in widgets_type:
                    continue

                fields[name]['name'] = name
                if 'saves' in attrs:
                    fields[name]['saves'] = attrs['saves']

                if 'filename' in attrs:
                    fields[name]['filename'] = attrs['filename']

                if 'default_focus' in attrs and not self.default_focus_field:
                    fields[name]['focus_field'] = attrs['default_focus']
                    self.default_focus_field = True

                widget_act = widgets_type[type][0](self.window, self.parent, model, fields[name])
                self.widget_id += 1
                widget_act.position = self.widget_id

                label = None
                if not int(attrs.get('nolabel', 0)):
                    # TODO space before ':' depends of lang (ex: english no space)
                    if gtk.widget_get_default_direction() == gtk.TEXT_DIR_RTL:
                        label = ': '+fields[name]['string']
                    else:
                        label = fields[name]['string']+' :'
                dict_widget[name] = widget_act
                size = int(attrs.get('colspan', widgets_type[ type ][1]))
                expand = widgets_type[ type ][2]
                fill = widgets_type[ type ][3]
                hlp = fields[name].get('help', attrs.get('help', False))
                if attrs.get('height', False) or attrs.get('width', False):
                    widget_act.widget.set_size_request(
                            int(attrs.get('width', -1)), int(attrs.get('height', -1)))
                if attrs.get('invisible', False):
                    visval = eval(attrs['invisible'], {'context':self.screen.context})
                    if visval:
                        continue

                translate = fields[name]['string'] if fields[name].get('translate') else None
                detail_tooltip = False
                if options.options['debug_mode_tooltips']:
                    detail_tooltip = self.create_detail_tooltip(name, fields[name])

                widget_label = container.create_label(label, help=hlp, fname=name, detail_tooltip=detail_tooltip) if label else None
                if attrs.get('attrs'):
                    saw_list.append(StateAwareWidget(widget_act, widget_label))

                container.wid_add(widget=widget_act.widget, label=widget_label, expand=expand, translate=translate, colspan=size, fname=name, fill=fill)

            elif node.tag =='group':
                frame = gtk.Frame(attrs.get('string', None))
                frame.attrs=attrs
                frame.set_border_width(0)
                states = [e for e in attrs.get('states','').split(',') if e]
                if attrs.get('invisible', False):
                    visval = eval(attrs['invisible'], {'context':self.screen.context})
                    if visval:
                        continue
                state_aware = StateAwareWidget(frame, states=states)
                saw_list.append(state_aware)

                if attrs.get("width",False) or attrs.get("height"):
                    frame.set_size_request(int(attrs.get('width', -1)) ,int(attrs.get('height', -1)))
                    hbox = gtk.HBox(homogeneous=False, spacing=0)
                    hbox.pack_start(frame, expand=False, fill=False, padding=0)
                    group_wid = hbox
                else:
                    group_wid = frame
                container.wid_add(group_wid, colspan=int(attrs.get('colspan', 1)), expand=int(attrs.get('expand',0)), rowspan=int(attrs.get('rowspan', 1)), ypadding=0, fill=int(attrs.get('fill', 1)))
                container.new(int(attrs.get('col',4)))
                widget, widgets, saws, on_write = self.parse(model, node, fields)
                state_aware.frame_child.update(widgets)
                dict_widget.update(widgets)
                saw_list += saws
                frame.add(widget)
                if not attrs.get('string', None):
                    frame.set_shadow_type(gtk.SHADOW_NONE)
                    container.get().set_border_width(0)
                container.pop()
            elif node.tag =='hpaned':
                hp = gtk.HPaned()
                container.wid_add(hp, colspan=int(attrs.get('colspan', 4)), expand=True, fill=True)
                _, widgets, saws, on_write = self.parse(model, node, fields, paned=hp)
                saw_list += saws
                dict_widget.update(widgets)
                #if 'position' in attrs:
                #   hp.set_position(int(attrs['position']))
            elif node.tag =='vpaned':
                hp = gtk.VPaned()
                container.wid_add(hp, colspan=int(attrs.get('colspan', 4)), expand=True, fill=True)
                _, widgets, saws, on_write = self.parse(model, node, fields, paned=hp)
                saw_list += saws
                dict_widget.update(widgets)
                if 'position' in attrs:
                    hp.set_position(int(attrs['position']))
            elif node.tag =='child1':
                widget, widgets, saws, on_write = self.parse(model, node, fields, paned=paned)
                saw_list += saws
                dict_widget.update(widgets)
                paned.pack1(widget, resize=True, shrink=True)
            elif node.tag =='child2':
                widget, widgets, saws, on_write = self.parse(model, node, fields, paned=paned)
                saw_list += saws
                dict_widget.update(widgets)
                paned.pack2(widget, resize=True, shrink=True)
            elif node.tag =='action':
                from action import action
                name = str(attrs['name'])
                widget_act = action(self.window, self.parent, model, attrs)
                dict_widget[name] = widget_act
                container.wid_add(widget_act.widget, colspan=int(attrs.get('colspan', 3)), expand=True, fill=True)
        for (ebox,src,name,widget) in container.trans_box:
            ebox.connect('button_press_event',self.translate, model, name, src, widget, self.screen, self.window)
        for (ebox,src,name) in container.trans_box_label:
            ebox.connect('button_press_event', self.translate_label, model, name, src, self.window)
        return container.pop(), dict_widget, saw_list, on_write

    def translate(self, widget, event, model, name, src, widget_entry, screen, window):
        """Translation window for object data strings"""
        #widget accessor functions
        def value_get(widget):
            if type(widget) == type(gtk.Entry()):
                return widget.get_text()
            elif type(widget.child) == type(gtk.TextView()):
                buffer = widget.child.get_buffer()
                iter_start = buffer.get_start_iter()
                iter_end = buffer.get_end_iter()
                return buffer.get_text(iter_start,iter_end,False)
            else:
                return None

        def value_set(widget, value):
            if type(widget) == type(gtk.Entry()):
                widget.set_text(value)
            elif type(widget.child) == type(gtk.TextView()):
                if value==False:
                    value=''
                buffer = widget.child.get_buffer()
                buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
                iter_start = buffer.get_start_iter()
                buffer.insert(iter_start, value)

        def widget_duplicate(widget):
            if type(widget) == type(gtk.Entry()):
                entry = gtk.Entry()
                entry.set_property('activates_default', True)
                entry.set_max_length(widget.get_max_length())
                entry.set_width_chars(widget.get_width_chars())
                return entry, gtk.FILL
            elif type(widget.child) == type(gtk.TextView()):
                tv = gtk.TextView()
                tv.set_wrap_mode(gtk.WRAP_WORD)
                sw = gtk.ScrolledWindow()
                sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
                sw.set_shadow_type(gtk.SHADOW_NONE)
                sw.set_size_request(-1, 80)
                sw.add(tv)
                tv.set_accepts_tab(False)
                return sw, gtk.FILL | gtk.EXPAND
            else:
                return None, False

        if not value_get(widget_entry):
            common.message(
                    _('Enter some text to the related field before adding translations!'),
                    parent=self.window)
            return False

        id = screen.current_model.id
        if not id:
            common.message(
                    _('You need to save resource before adding translations!'),
                    parent=self.window)
            return False
        id = screen.current_model.save(reload=False)
        uid = rpc.session.uid
        # Find the translatable languages
        lang_ids = rpc.session.rpc_exec_auth('/object', 'execute', 'res.lang',
                'search', [('translatable','=','1')])
        if not lang_ids:
            common.message(_('No other language available!'),
                    parent=window)
            return False
        langs = rpc.session.rpc_exec_auth('/object', 'execute', 'res.lang',
                'read', lang_ids, ['code', 'name'])
        # get the code of the current language
        current_lang = rpc.session.context.get('lang', 'en_US')

        # There used to be a adapt_context() function here, to make sure we sent
        # False instead of 'en_US'. But why do that at all ?

        # Window
        win = gtk.Dialog(_('Add Translation'), window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        win.vbox.set_spacing(5)
        win.set_property('default-width', 600)
        win.set_property('default-height', 400)
        win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        win.set_icon(common.OPENERP_ICON)
        # Accelerators
        accel_group = gtk.AccelGroup()
        win.add_accel_group(accel_group)
        # Buttons
        but_cancel = win.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        but_cancel.add_accelerator('clicked', accel_group, gtk.keysyms.Escape,
                gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        but_ok = win.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        but_ok.add_accelerator('clicked', accel_group, gtk.keysyms.Return,
                gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        # Vertical box
        vbox = gtk.VBox(spacing=5)
        # Grid with all the translations
        entries_list = []
        table = gtk.Table(len(langs), 2)
        table.set_homogeneous(False)
        table.set_col_spacings(3)
        table.set_row_spacings(0)
        table.set_border_width(1)
        i = 0
        for lang in langs:
            # Make sure the context won't mutate
            context = copy.copy(rpc.session.context)
            context['lang'] = lang['code']
            # Read the string in this language 
            val = rpc.session.rpc_exec_auth('/object', 'execute', model,
                    'read', [id], [name], context)
            val = val[0]
            # Label
            #TODO space before ':' depends of lang (ex: english no space)
            if gtk.widget_get_default_direction() == gtk.TEXT_DIR_RTL:
                label = gtk.Label(': ' + lang['name'])
            else:
                label = gtk.Label(lang['name'] + ' :')
            label.set_alignment(1.0, 0.5)
            (entry, yoptions) = widget_duplicate(widget_entry)

             # Setting the writable property according to main widget
            if isinstance(entry,gtk.Entry):
                entry.set_sensitive(widget_entry.get_editable())
            elif isinstance(entry,gtk.ScrolledWindow):
                entry.child.set_sensitive(widget_entry.child.get_editable())

            # Label and text box side by side
            hbox = gtk.HBox(homogeneous=False)
            # Take the latest text in the user's language
            if lang['code'] == current_lang:
                value_set(entry,value_get(widget_entry))
            else:
                value_set(entry,val[name])
            
            entries_list.append((lang['code'], entry))
            table.attach(label, 0, 1, i, i+1, yoptions=False, xoptions=gtk.FILL,
                    ypadding=2, xpadding=5)
            table.attach(entry, 1, 2, i, i+1, yoptions=yoptions,
                    ypadding=2, xpadding=5)
            i += 1
        # Open the window
        vbox.pack_start(table)
        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        vp.add(vbox)
        sv = gtk.ScrolledWindow()
        sv.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC )
        sv.set_shadow_type(gtk.SHADOW_NONE)
        sv.add(vp)
        win.vbox.add(sv)
        win.show_all()
        
        # process the response
        ok = False
        data = []
        while not ok:
            response = win.run()
            ok = True
            if response == gtk.RESPONSE_OK:
                # Get the values of all the text boxes
                for code, entry in entries_list:
                    value=value_get(entry)
                    # update the previous form if the string in the user's language was just changed
                    if code == current_lang:
                        value_set(widget_entry, value)
                    # write the new translation
                    context = copy.copy(rpc.session.context)
                    context['lang'] = code
                    rpc.session.rpc_exec_auth('/object', 'execute', model,
                            'write', [id], {str(name):  value},
                            context)
            if response == gtk.RESPONSE_CANCEL:
                window.present()
                win.destroy()
                return
        screen.current_model.reload()
        window.present()
        win.destroy()
        return True

    def translate_label(self, widget, event, model, name, src, window):
        def callback_label(self, widget, event, model, name, src, window=None):
            lang_ids = rpc.session.rpc_exec_auth('/object', 'execute',
                    'res.lang', 'search', [('translatable', '=', '1')])
            if not lang_ids:
                common.message(_('No other language available!'),
                        parent=window)
                return False
            langs = rpc.session.rpc_exec_auth('/object', 'execute', 'res.lang',
                    'read', lang_ids, ['code', 'name'])

            win = gtk.Dialog(_('Add Translation'), window,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
            win.vbox.set_spacing(5)
            win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            win.set_icon(common.OPENERP_ICON)
            vbox = gtk.VBox(spacing=5)

            entries_list = []
            for lang in langs:
                code=lang['code']
                val = rpc.session.rpc_exec_auth('/object', 'execute', model,
                        'read_string', False, [code], [name])
                if val and code in val:
                    val = val[code]
                else:
                    val={'code': code, 'name': src}
                label = gtk.Label(lang['name'])
                entry = gtk.Entry()
                entry.set_text(val[name])
                entries_list.append((code, entry))
                hbox = gtk.HBox(homogeneous=True)
                hbox.pack_start(label, expand=False, fill=False)
                hbox.pack_start(entry, expand=True, fill=True)
                vbox.pack_start(hbox, expand=False, fill=True)
            vp = gtk.Viewport()
            vp.set_shadow_type(gtk.SHADOW_NONE)
            vp.add(vbox)
            sv = gtk.ScrolledWindow()
            sv.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC )
            sv.set_shadow_type(gtk.SHADOW_NONE)
            sv.add(vp)
            win.vbox.add(sv)
            win.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            win.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
            win.resize(400,200)
            win.show_all()
            res = win.run()
            if res == gtk.RESPONSE_OK:
                to_save = map(lambda x: (x[0], x[1].get_text()), entries_list)
                while to_save:
                    code, val = to_save.pop()
                    rpc.session.rpc_exec_auth('/object', 'execute', model,
                            'write_string', False, [code], {name: val})
            window.present()
            win.destroy()
            return res

        def callback_view(self, widget, event, model, src, window=None):
            lang_ids = rpc.session.rpc_exec_auth('/object', 'execute',
                    'res.lang', 'search', [('translatable', '=', '1')])
            if not lang_ids:
                common.message(_('No other language available!'),
                        parent=window)
                return False
            langs = rpc.session.rpc_exec_auth('/object', 'execute', 'res.lang',
                    'read', lang_ids, ['code', 'name'])

            win = gtk.Dialog(_('Add Translation'), window,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
            win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            win.set_icon(common.OPENERP_ICON)
            win.vbox.set_spacing(5)
            vbox = gtk.VBox(spacing=5)

            entries_list = []
            for lang in langs:
                code=lang['code']
                view_item_ids = rpc.session.rpc_exec_auth('/object', 'execute',
                        'ir.translation', 'search', [
                            ('name', '=', model),
                            ('type', '=', 'view'),
                            ('lang', '=', code),
                            ])
                view_items = rpc.session.rpc_exec_auth('/object', 'execute',
                        'ir.translation', 'read', view_item_ids,
                        ['src', 'value'])
                label = gtk.Label(lang['name'])
                vbox.pack_start(label, expand=False, fill=True)
                for val in view_items:
                    label = gtk.Label(val['src'])
                    entry = gtk.Entry()
                    entry.set_text(val['value'])
                    entries_list.append((val['id'], entry))
                    hbox = gtk.HBox(homogeneous=True)
                    hbox.pack_start(label, expand=False, fill=False)
                    hbox.pack_start(entry, expand=True, fill=True)
                    vbox.pack_start(hbox, expand=False, fill=True)
            vp = gtk.Viewport()
            vp.set_shadow_type(gtk.SHADOW_NONE)
            vp.add(vbox)
            sv = gtk.ScrolledWindow()
            sv.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC )
            sv.set_shadow_type(gtk.SHADOW_NONE)
            sv.add(vp)
            win.vbox.add(sv)
            win.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            win.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
            win.resize(400,200)
            win.show_all()
            res = win.run()
            if res == gtk.RESPONSE_OK:
                to_save = map(lambda x: (x[0], x[1].get_text()), entries_list)
                while to_save:
                    id, val = to_save.pop()
                    rpc.session.rpc_exec_auth('/object', 'execute',
                            'ir.translation', 'write', [id], {'value': val})
            window.present()
            win.destroy()
            return res
        if event.button != 3:
            return
        menu = gtk.Menu()
        if name:
            item = gtk.ImageMenuItem(_('Translate label'))
            item.connect("activate", callback_label, widget, event, model, name, src, window)
            item.set_sensitive(1)
            item.show()
            menu.append(item)
        item = gtk.ImageMenuItem(_('Translate view'))
        item.connect("activate", callback_view, widget, event, model, src, window)
        item.set_sensitive(1)
        item.show()
        menu.append(item)
        menu.popup(None,None,None,event.button,event.time)
        return True

import float_time
import calendar
import spinbutton
import spinint
import char
import checkbox
import button
import reference
import binary
import textbox
import textbox_tag
#import one2many
import many2many
import many2one
import selection
import one2many_list
import picture
import url
import image

import progressbar

widgets_type = {
    'date': (calendar.calendar, 1, False, False),
    'time': (calendar.stime, 1, False, False),
    'datetime': (calendar.datetime, 1, False, False),
    'float': (spinbutton.spinbutton, 1, False, False),
    'integer': (spinint.spinint, 1, False, False),
    'selection': (selection.selection, 1, False, False),
    'char': (char.char, 1, False, False),
    'float_time': (float_time.float_time, 1, False, False),
    'boolean': (checkbox.checkbox, 1, False, False),
    'button': (button.button, 1, False, False),
    'reference': (reference.reference, 1, False, False),
    'binary': (binary.wid_binary, 1, False, False),
    'picture': (picture.wid_picture, 1, False, False),
    'text': (textbox.textbox, 1, True, True),
    'text_wiki': (textbox.textbox, 1, True, True),
    'text_tag': (textbox_tag.textbox_tag, 1, True, True),
    'one2many': (one2many_list.one2many_list, 1, True, True),
    'one2many_form': (one2many_list.one2many_list, 1, True, True),
    'one2many_list': (one2many_list.one2many_list, 1, True, True),
    'many2many': (many2many.many2many, 1, True, True),
    'many2one': (many2one.many2one, 1, False, False),
    'email' : (url.email, 1, False, False),
    'url' : (url.url, 1, False, False),
    'callto' : (url.callto, 1, False, False),
    'sip' : (url.sip, 1, False, False),
    'image' : (image.image_wid, 1, False, False),
    'uri' : (url.uri, 1, False, False),
    'progressbar' : (progressbar.progressbar, 1, False, False),
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

