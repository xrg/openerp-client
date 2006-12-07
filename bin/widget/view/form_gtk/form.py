##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import tools
import interface

import widget.view.interface
from observator import oregistry, Observable

import gtk
from gtk import glade

import common
import service
import rpc


class Button(Observable):
	def __init__(self, attrs={}):
		super(Button, self).__init__()
		self.attrs = attrs
		args = {
			'label': attrs.get('string', 'unknown')
		}
#		if 'icon' in attrs:
#			args['stock'] = eval('gtk.'+attrs['icon'])
		self.widget = gtk.Button(**args)
		if attrs.get('icon', False):
			icon = gtk.Image()
			icon.set_from_stock(attrs['icon'], gtk.ICON_SIZE_BUTTON)
			self.widget.set_image(icon)
#		self.widget.set_use_stock(True)
#		self.widget.set_label(args['label'])

		self.widget.show()
		self.widget.connect('clicked', self.button_clicked)

	def button_clicked(self, widget):
		model = self.form.screen.current_model
		self.form.set_value()
		if model.validate():
			id = self.form.screen.save_current()
			if not self.attrs.get('confirm',False) or \
					common.sur(self.attrs['confirm']):
				button_type = self.attrs.get('type', 'workflow')
				if button_type == 'workflow':
					rpc.session.rpc_exec_auth('/object', 'exec_workflow',
											  self.form.screen.name,
											  self.attrs['name'], id)
				elif button_type == 'object':
					rpc.session.rpc_exec_auth('/object', 'execute',
											  self.form.screen.name,
											  self.attrs['name'],
											  [id], model.context_get())
				elif button_type == 'action':
					obj = service.LocalService('action.main')
					action_id = int(self.attrs['name'])
					obj.execute(action_id, {'model':self.form.screen.name, 'id': id,
									   'ids': [id]})
				else:
					raise 'Unallowed button type'
				self.form.screen.reload()
		else:
			self.warn('misc-message', _('Invalid Form, correct red fields !'))
			self.form.screen.display()

	def state_set(self, state):
		if self.attrs.get('states', False):
			my_states = self.attrs.get('states', '').split(',')
			if state not in my_states:
				self.widget.hide()
			else:
				self.widget.show()
		else:
			self.widget.show()

class _container(object):
	def __init__(self):
		self.cont = []
		self.col = []
		self.sg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.tooltips = gtk.Tooltips()
		self.trans_box = []

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
	def wid_add(self, widget, name=None, expand=False, ypadding=2, rowspan=1, colspan=1, translate=False, fname=None, help=False):
		(table, x, y) = self.cont[-1]
		if colspan>self.col[-1]:
			colspan=self.col[-1]
		a = name and 1 or 0
		if colspan+x+a>self.col[-1]:
			self.newline()
			(table, x, y) = self.cont[-1]
		if expand:
			yopt = gtk.EXPAND | gtk.FILL
		else:
			yopt = False
		if name:
			label = gtk.Label(name)
			if help:
				eb = gtk.EventBox()
				eb.add(label)
				self.tooltips.set_tip(eb, help)
				self.tooltips.enable()
				eb.show()
			else:
				eb = label
			if '_' in name:
				label.set_text_with_mnemonic(name)
				label.set_mnemonic_widget(widget)
			label.set_alignment(1.0, 0.5)
			table.attach(eb, x, x+1, y, y+rowspan, yoptions=yopt, xoptions=gtk.FILL, ypadding=ypadding, xpadding=5)
			x=x+1
		hbox = widget
		hbox.show_all()
		if translate:
			hbox = gtk.HBox(spacing=3)
			hbox.pack_start(widget)
			img = gtk.Image()
			img.set_from_stock('terp-translate', gtk.ICON_SIZE_MENU)
			ebox = gtk.EventBox()
			ebox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
			self.trans_box.append((ebox, name, fname, widget))
			
			ebox.add(img)
			hbox.pack_start(ebox, fill=False, expand=False)
			hbox.show_all()
		table.attach(hbox, x, x+colspan, y, y+rowspan, yoptions=yopt, ypadding=ypadding, xpadding=5)
		self.cont[-1] = (table, x+colspan, y)
		wid_list = table.get_children()
		wid_list.reverse()
		table.set_focus_chain(wid_list)

class parser_form(widget.view.interface.parser_interface):
	def parse(self, model, root_node, fields, notebook=None):
		dict_widget = {}
		button_list = []
		attrs = tools.node_attributes(root_node)
		on_write = attrs.get('on_write', '')
		container = _container()
		container.new(col=int(attrs.get('col', 4)))
		self.container = container

		if not self.title:
			attrs = tools.node_attributes(root_node)
			self.title = attrs.get('string', 'Unknown')

		for node in root_node.childNodes:
			if not node.nodeType==node.ELEMENT_NODE:
				continue
			attrs = tools.node_attributes(node)
			if node.localName=='image':
				icon = gtk.Image()
				icon.set_from_stock(attrs['name'], gtk.ICON_SIZE_DIALOG)
				container.wid_add(icon,colspan=int(attrs.get('colspan',1)),expand=int(attrs.get('expand',0)), ypadding=10, help=attrs.get('help', False))
			elif node.localName=='separator':
				vbox = gtk.VBox()
				if 'string' in attrs:
					l = gtk.Label(attrs.get('string', 'No String Attr.'))
					l.set_alignment(0.0, 0.5)
					vbox.pack_start(l)
				vbox.pack_start(gtk.HSeparator())
				container.wid_add(vbox,colspan=int(attrs.get('colspan',1)),expand=int(attrs.get('expand',0)), ypadding=10, help=attrs.get('help', False))
			elif node.localName=='label':
				text = attrs.get('string', '')
				if not text:
					for node in node.childNodes:
						if node.nodeType == node.TEXT_NODE:
							text += node.data
						else:
							text += node.toxml()
				label = gtk.Label(text)
				label.set_use_markup(True)
				if 'align' in attrs:
					try:
						label.set_alignment(float(attrs['align'] or 0.0), 0.5)
					except:
						pass
				if 'angle' not in attrs:
					label.set_line_wrap(True)
				label.set_angle(int(attrs.get('angle', 0)))
				container.wid_add(label, colspan=int(attrs.get('colspan', 1)), expand=False, help=attrs.get('help', False))

			elif node.localName=='newline':
				container.newline()

			elif node.localName=='button':
				button = Button(attrs)
				button_list.append(button)
				container.wid_add(button.widget, colspan=int(attrs.get('colspan', 1)), help=attrs.get('help', False))

			elif node.localName=='notebook':
				nb = gtk.Notebook()
				if attrs and 'tabpos' in attrs:
					pos = {'up':gtk.POS_TOP,
						'down':gtk.POS_BOTTOM,
						'left':gtk.POS_LEFT,
						'right':gtk.POS_RIGHT
					}[attrs['tabpos']]
				else:
					pos = gtk.POS_LEFT
				nb.set_tab_pos(pos)
				nb.set_border_width(3)
				container.wid_add(nb, colspan=attrs.get('colspan', 3), expand=True )
				_, widgets, buttons, on_write = self.parse(model, node, fields, nb)
				button_list += buttons
				dict_widget.update(widgets)

			elif node.localName=='page':
				l = gtk.Label(attrs.get('string','No String Attr.'))
				widget, widgets, buttons, on_write = self.parse(model, node, fields, notebook)
				button_list += buttons
				dict_widget.update(widgets)
				notebook.append_page(widget, l)

			elif node.localName=='field':
				name = attrs['name']
				del attrs['name']
				type = attrs.get('widget', fields[name]['type'])
				fields[name].update(attrs)
				fields[name]['model']=model
				if not type in widgets_type:
					continue

				fields[name]['name'] = name
				widget_act = widgets_type[type][0](self.window, self.parent, model, fields[name])
				label = None
				if not int(attrs.get('nolabel', 0)):
					label = fields[name]['string']+' :'
				dict_widget[name] = widget_act
				size = int(attrs.get('colspan', widgets_type[ type ][1]))
				expand = widgets_type[ type ][2]
				hlp = fields[name].get('help', attrs.get('help', False))
				container.wid_add(widget_act.widget, label, expand, translate=fields[name].get('translate',False), colspan=size, fname=name, help=hlp)

			elif node.localName=='group':
				frame = gtk.Frame(attrs.get('string', None))
				frame.set_border_width(0)


				container.wid_add(frame, colspan=int(attrs.get('colspan', 1)), expand=int(attrs.get('expand',0)), rowspan=int(attrs.get('rowspan', 1)))
				container.new(int(attrs.get('col',4)))

				widget, widgets, buttons, on_write = self.parse(model, node, fields)
				dict_widget.update(widgets)
				button_list += buttons
				frame.add(widget)
				if not attrs.get('string', None):
					frame.set_shadow_type(gtk.SHADOW_NONE)
					container.get().set_border_width(0)
				container.pop()

		for (ebox,src,name,widget) in container.trans_box:
			ebox.connect('button_press_event',self.translate, model, name, src, widget)
		return container.pop(), dict_widget, button_list, on_write

	def translate(self, widget, event, model, name, src, widget_entry):
		#value = [self.id, model, name,src, widget_entry]
		id = model.id_get()
		if not id:
			common.message('You need to save ressource before adding translations')
			return False
		uid = rpc.session.uid

		win = gtk.Dialog('Add Translation')

		lang_ids = rpc.session.rpc_exec_auth('/object', 'execute', 'res.lang', 'search', [('translatable','=','1')])
		langs = rpc.session.rpc_exec_auth('/object', 'execute', 'res.lang', 'read', lang_ids, ['code'])

		#Add english ; default value not in res.lang
		langs.append({'code':'en'})
		code = rpc.session.context.get('lang', 'en')

		#change 'en' to false for context
		def adapt_context(val):
			if val == 'en':
				return False
			else:
				return val

		#widget accessor fucntions
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
				return gtk.Entry()
			elif type(widget.child) == type(gtk.TextView()):
				tv = gtk.TextView()
				tv.set_wrap_mode(gtk.WRAP_WORD)
				sw = gtk.ScrolledWindow()
				sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
				sw.set_shadow_type(gtk.SHADOW_NONE)
				sw.set_size_request(-1, 80)
				sw.add(tv)
				tv.set_accepts_tab(False)
				return sw
			else:
				return None
		entries_list = []
		win.vbox.set_spacing(5)
		vbox = gtk.VBox()
		
		for lang in langs:
			context = copy.copy(rpc.session.context)
			context['lang'] = adapt_context(lang['code'])
			val = rpc.session.rpc_exec_auth('/object', 'execute', value[1], 'read', [value[0]], [value[2]], context)
			val = val[0]
			
			label = gtk.Label(lang['code'] or 'en')
			entry = widget_duplicate(value[4])

			hbox = gtk.HBox(homogeneous=True, spacing=0)
			if code == lang['code']:
				value_set(entry,value_get(value[4]))
			else:
				value_set(entry,val[value[2]])
			
			entries_list.append((val['id'], lang['code'], entry))
			hbox.pack_start(label, expand=False, fill=False)
			hbox.pack_start(entry, expand=True, fill=True)
			vbox.pack_start(hbox, expand=True, fill=True)
		
		sv = gtk.ScrolledWindow()
		sv.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC )
		sv.add_with_viewport(vbox)
		win.vbox.pack_start(sv)
		win.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		win.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
		win.resize(320,240)
		win.show_all()
		
		ok = False
		data = []
		while not ok:
			response = win.run()
			ok = True
			#res = None
			if response == gtk.RESPONSE_OK:
				to_save = map(lambda x : (x[0], x[1], value_get(x[2])), entries_list)
				while to_save != []:
					new_val = {}
					new_val['id'],new_val['lang'], new_val['value'] = to_save.pop()
					#update form field
					if new_val['lang'] == code:
						value_set(value[4],new_val['value'])
				
					context = copy.copy(rpc.session.context)
					context['lang'] = adapt_context(new_val['lang'])
					rpc.session.rpc_exec_auth('/object', 'execute', value[1], 'write', [value[0]], {str(value[2]):  new_val['value']}, context)
			if response == gtk.RESPONSE_CANCEL:
				win.destroy()
				return
		win.destroy()
		return True


		pass


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


widgets_type = {
	'date': (calendar.calendar, 1, False),
	'time': (calendar.stime, 1, False),
	'datetime': (calendar.datetime, 1, False),
	'float': (spinbutton.spinbutton, 1, False),
	'integer': (spinint.spinint, 1, False),
	'selection': (selection.selection, 1, False),
	'char': (char.char, 1, False),
	'boolean': (checkbox.checkbox, 1, False),
	'button': (button.button, 1, False),
	'reference': (reference.reference, 1, False),
	'binary': (binary.wid_binary, 1, False),
	'picture': (picture.wid_picture, 1, False),
	'text': (textbox.textbox, 1, True),
	'text_tag': (textbox_tag.textbox_tag, 1, True),
	'one2many': (one2many_list.one2many_list, 1, True),
	'one2many_form': (one2many_list.one2many_list, 1, True),
	'one2many_list': (one2many_list.one2many_list, 1, True),
	'many2many': (many2many.many2many, 1, True),
	'many2one': (many2one.many2one, 1, False),
	'email' : (url.email, 1, False),
	'url' : (url.url, 1, False),
	'image' : (image.image_wid, 1, False),
}

# vim:noexpandtab:
