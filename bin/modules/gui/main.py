##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#					Fabien Pinckaers <fp@tiny.Be>
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

import time
import os
import gettext
import urlparse

import gobject
import gtk
from gtk import glade

import rpc

import service
import options
import common

from window import win_preference
import tools
import re
import xmlrpclib
import base64

def _refresh_dblist(db_widget, url, dbtoload=None):
	if not dbtoload:
		dbtoload = options.options['login.db']
	index = 0
	liststore = db_widget.get_model()
	liststore.clear()
	result = rpc.session.list_db(url)
	if result==-1:
		return -1
	for db_num, db_name in enumerate(rpc.session.list_db(url)):
		liststore.append([db_name])
		if db_name == dbtoload:
			index = db_num
	db_widget.set_active(index)
	return len(liststore)

def _refresh_langlist(lang_widget, url):
	liststore = lang_widget.get_model()
	liststore.clear()
	lang_list = rpc.session.db_exec_no_except(url, 'list_lang')
	lang_list.append( ('en_EN','English') )
	for key,val in lang_list:
		liststore.insert(0, (val,key))
	lang_widget.set_active(0)
	return lang_list

def _server_ask(server_widget):
	result = False
	win_gl = glade.XML(common.terp_path("terp.glade"),"win_server",gettext.textdomain())
	win = win_gl.get_widget('win_server')
	win.set_default_response(gtk.RESPONSE_OK)
	host_widget = win_gl.get_widget('ent_host')
	port_widget = win_gl.get_widget('ent_port')
	protocol_widget = win_gl.get_widget('protocol')

	protocol={'XML-RPC': 'http://',
			'XML-RPC secure': 'https://',
			'NET-RPC (faster)': 'socket://',}
	listprotocol = gtk.ListStore(str)
	protocol_widget.set_model(listprotocol)


	m = re.match('^(http[s]?://|socket://)([\w.-]+):(\d{1,5})$', server_widget.get_text())
	if m:
#		secure_widget.set_active(m.group(1) == 'https://')
		host_widget.set_text(m.group(2))
		port_widget.set_text(m.group(3))

	index = 0
	i = 0
	for p in protocol:
		listprotocol.append([p])
		if m and protocol[p] == m.group(1):
			index = i
		i += 1
	protocol_widget.set_active(index)

	res = win.run()
	if res == gtk.RESPONSE_OK:
#		protocol = secure_widget.get_active() and 'https://' or 'http://'
		protocol = protocol[protocol_widget.get_active_text()]
		url = '%s%s:%s' % (protocol, host_widget.get_text(), port_widget.get_text())
		server_widget.set_text(url)
		result = url
	win.destroy()
	return result

class db_login(object):
	def __init__(self):
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"win_login",gettext.textdomain())

	def refreshlist(self, widget, db_widget, label, url, butconnect=False):
		res = _refresh_dblist(db_widget, url)
		if res == -1:
			label.set_label('<b>'+_('Could not connect to server !')+'</b>')
			db_widget.hide()
			label.show()
			if butconnect:
				butconnect.set_sensitive(False)
		elif res==0:
			label.set_label('<b>'+_('No database found, you must create one !')+'</b>')
			db_widget.hide()
			label.show()
			if butconnect:
				butconnect.set_sensitive(False)
		else:
			label.hide()
			db_widget.show()
			if butconnect:
				butconnect.set_sensitive(True)
		return res

	def refreshlist_ask(self,widget, server_widget, db_widget, label, butconnect = False, url=False):
		url = _server_ask(server_widget) or url
		return self.refreshlist(widget, db_widget, label, url, butconnect)

	def run(self, dbname=None, parent=None):
		uid = 0
		win = self.win_gl.get_widget('win_login')
		if parent:
			win.set_transient_for(parent)
		login = self.win_gl.get_widget('ent_login')
		passwd = self.win_gl.get_widget('ent_passwd')
		server_widget = self.win_gl.get_widget('ent_server')
		but_connect = self.win_gl.get_widget('button_connect')
		db_widget = self.win_gl.get_widget('combo_db')
		change_button = self.win_gl.get_widget('but_server')
		label = self.win_gl.get_widget('combo_label')
		label.hide()

		host = options.options['login.server']
		port = options.options['login.port']
		protocol = options.options['login.protocol']
		
		url = '%s%s:%s' % (protocol, host, port)
		server_widget.set_text(url)
		login.set_text(options.options['login.login'])

		# construct the list of available db and select the last one used
		liststore = gtk.ListStore(str)
		db_widget.set_model(liststore)
		cell = gtk.CellRendererText()
		db_widget.pack_start(cell, True)
		db_widget.add_attribute(cell, 'text', 0)

		res = self.refreshlist(None, db_widget, label, url, but_connect)
		change_button.connect_after('clicked', self.refreshlist_ask, server_widget, db_widget, label, but_connect, url)

		if dbname:
			iter = liststore.get_iter_root()
			while iter:
				if liststore.get_value(iter, 0)==dbname:
					db_widget.set_active_iter(iter)
					break
				iter = liststore.iter_next(iter)

		res = win.run()
		m = re.match('^(http[s]?://|socket://)([\w.\-]+):(\d{1,5})$', server_widget.get_text() or '')
		if m:
			options.options['login.server'] = m.group(2)
			options.options['login.login'] = login.get_text()
			options.options['login.port'] = m.group(3)
			options.options['login.protocol'] = m.group(1)
			options.options['login.db'] = db_widget.get_active_text()
			result = (login.get_text(), passwd.get_text(), m.group(2), m.group(3), m.group(1), db_widget.get_active_text())
		else:
			win.destroy()
			raise 'QueryCanceled'
		if res == gtk.RESPONSE_CANCEL:
			win.destroy()
			raise 'QueryCanceled'
		win.destroy()
		return result

class db_create(object):
	def set_sensitive(self, sensitive):
		if sensitive:
			label = self.dialog.get_widget('db_label_info')
			label.set_text(_('Do not use special characters !'))
			self.dialog.get_widget('button_db_ok').set_sensitive(True)
		else:
			label = self.dialog.get_widget('db_label_info')
			label.set_text(_('Can not connect to server, please change it !'))
			self.dialog.get_widget('button_db_ok').set_sensitive(False)
		return sensitive

	def server_change(self, widget=None):
		url = _server_ask(self.server_widget)
		try:
			if self.lang_widget:
				_refresh_langlist(self.lang_widget, url)
			self.set_sensitive(True)
		except:
			self.set_sensitive(False)
			return False
		return url

	def __init__(self, sig_login):
		self.dialog = glade.XML(common.terp_path("terp.glade"), "win_createdb", gettext.textdomain())
		self.sig_login = sig_login

	def run(self, parent=None):
		win = self.dialog.get_widget('win_createdb')
		if parent:
			win.set_transient_for(parent)
		lang_dict = {}
		pass_widget = self.dialog.get_widget('ent_password_new')
		self.server_widget = self.dialog.get_widget('ent_server_new')
		change_button = self.dialog.get_widget('but_server_new')
		self.lang_widget = self.dialog.get_widget('db_create_combo')
		self.db_widget = self.dialog.get_widget('ent_db')
		demo_widget = self.dialog.get_widget('check_demo')
		demo_widget.set_active(True)

		change_button.connect_after('clicked', self.server_change)
		protocol = options.options['login.protocol']
		url = '%s%s:%s' % (protocol, options.options['login.server'], options.options['login.port'])

		self.server_widget.set_text(url)
		liststore = gtk.ListStore(str, str)
		self.lang_widget.set_model(liststore)
		try:
			_refresh_langlist(self.lang_widget, url)
		except:
			self.set_sensitive(False)

		while True:
			res = win.run()
			db_name = self.db_widget.get_text()
			if (res==gtk.RESPONSE_OK) and ((not db_name) or (not re.match('^[a-zA-Z][a-zA-Z0-9_]+$', db_name))):
				common.warning(_('The database name must contain only normal characters or "_".\nYou must avoid all accents, space or special characters.'), _('Bad database name !'), parent=parent)

			else:
				break
		demo_data = demo_widget.get_active()

		langidx = self.lang_widget.get_active_iter()
		langreal = langidx and self.lang_widget.get_model().get_value(langidx,1)
		passwd = pass_widget.get_text()
		url = self.server_widget.get_text()
		m = re.match('^(http[s]?://|socket://)([\w.\-]+):(\d{1,5})$', url or '')
		if m:
			options.options['login.server'] = m.group(2)
			options.options['login.port'] = m.group(3)
			options.options['login.protocol'] = m.group(1)
		win.destroy()

		if res == gtk.RESPONSE_OK:
			try:
				id = rpc.session.db_exec(url, 'create', passwd, db_name, demo_data, langreal)
				dialog = glade.XML(common.terp_path("terp.glade"), "win_progress", gettext.textdomain())
				win = dialog.get_widget('win_progress')
				if parent:
					win.set_transient_for(parent)
				pb_widget = dialog.get_widget('progressbar')
				self.timer = gobject.timeout_add(1000, self.progress_timeout, pb_widget, url, passwd, id, win, db_name, parent)
				win.show()
			except Exception, e:
				if ('faultString' in e and e.faultString=='AccessDenied:None') or str(e)=='AccessDenied':
					common.warning(_('Bad database administrator password !'), _("Could not create database."))
				else:
					common.warning(_("Could not create database."),_('Error during database creation !'))
	
	def progress_timeout(self, pbar, url, passwd, id, win, dbname, parent=None):
		try:
			progress,users = rpc.session.db_exec_no_except(url, 'get_progress', passwd, id)
		except:
			win.destroy()
			common.warning(_("The server crashed during installation.\nWe suggest you to drop this database."),_("Error during database creation !"))
			return False

		if 0.0 <= progress < 1.0:
			pbar.set_fraction(progress)
		elif progress == 1.0:
			win.destroy()

			pwdlst = '\n'.join(map(lambda x: '    - %s: %s / %s' % (x['name'],x['login'],x['password']), users))
			dialog = glade.XML(common.terp_path("terp.glade"), "dia_dbcreate_ok", gettext.textdomain())
			win = dialog.get_widget('dia_dbcreate_ok')
			if parent:
				win.set_transient_for(parent)
			buffer = dialog.get_widget('dia_tv').get_buffer()

			buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
			iter_start = buffer.get_start_iter()
			buffer.insert(iter_start, _('The following users have been installed on your database:\n\n'+ pwdlst + '\n\n'+_('You can now connect to the database as an administrator.')))
			res = win.run()
			win.destroy()

			if res == gtk.RESPONSE_OK:
				m = re.match('^(http[s]?://|socket://)([\w.]+):(\d{1,5})$', url)
				res = ['admin', 'admin']
				if m:
					res.append( m.group(2) )
					res.append( m.group(3) )
					res.append( m.group(1) )
					res.append( dbname )

				self.sig_login(dbname=dbname)
			return False
		else:
			pbar.pulse()
		return True

	def process(self):
		return False


class terp_main(service.Service):
	def __init__(self, name='gui.main', audience='gui.*'):
		service.Service.__init__(self, name, audience)
		self.exportMethod(self.win_add)

		self.glade = glade.XML(common.terp_path("terp.glade"),"win_main",gettext.textdomain())
		self.status_bar_main = self.glade.get_widget('hbox_status_main')
		self.toolbar = self.glade.get_widget('main_toolbar')
		self.sb_requests = self.glade.get_widget('sb_requests')
		self.sb_username = self.glade.get_widget('sb_user_name')
		self.sb_servername = self.glade.get_widget('sb_user_server')
		id = self.sb_servername.get_context_id('message')
		self.sb_servername.push(id, _('Press Ctrl+O to login'))
		self.secure_img = self.glade.get_widget('secure_img')
		self.secure_img.hide()

		window = self.glade.get_widget('win_main')
		window.connect("destroy", self.sig_quit)
		window.connect("delete_event", self.sig_delete)
		self.window = window
		self.window.set_icon(gtk.gdk.pixbuf_new_from_file(common.terp_path_pixmaps('tinyerp_icon.png')))

		self.notebook = gtk.Notebook()
		self.notebook.popup_enable()
		self.notebook.set_scrollable(True)
		#self.notebook.set_show_border(False)
		self.sig_id = self.notebook.connect_after('switch-page', self._sig_page_changt)
		vbox = self.glade.get_widget('vbox_main')
		vbox.pack_start(self.notebook, expand=True, fill=True)

		#pict = gtk.Image()
		#pict.set_from_file('goals.png')
		#pict.show()
		#vbox.pack_start(pict, expand=True, fill=True)
		#vbox.remove(pict)

		#
		# Code to add themes to the options->theme menu
		#
		submenu = gtk.Menu()
		menu = self.glade.get_widget('menu_theme')
		old = None
		for dname in os.listdir(common.terp_path('themes')):
			if dname.startswith('.'):
				continue
			fname = common.terp_path(os.path.join('themes', dname, 'gtkrc'))
			if os.path.isfile(fname):
				open_item = gtk.RadioMenuItem(old, dname)
				old = open_item
				submenu.append(open_item)
				if dname == options.options['client.theme']:
					open_item.set_active(True)
				open_item.connect('toggled', self.theme_select, dname)

		submenu.append(gtk.SeparatorMenuItem())
		open_item = gtk.RadioMenuItem(old, _('Default Theme'))
		submenu.append(open_item)
		if 'none'==options.options['client.theme']:
			open_item.set_active(True)
		open_item.connect('toggled', self.theme_select, 'none')
		submenu.show_all()
		menu.set_submenu(submenu)

		#
		# Default Notebook
		#

		self.notebook.show()
		self.pages = []
		self.current_page = 0
		self.last_page = 0

		dict = {
			'on_login_activate': self.sig_login,
			'on_logout_activate': self.sig_logout,
			'on_win_next_activate': self.sig_win_next,
			'on_win_prev_activate': self.sig_win_prev,
			'on_plugin_execute_activate': self.sig_plugin_execute,
			'on_quit_activate': self.sig_close,
			'on_win_new_activate': self.sig_win_new,
			'on_win_home_activate': self.sig_home_new,
			'on_win_close_activate': self.sig_win_close,
			'on_support_activate': common.support,
			'on_preference_activate': self.sig_user_preferences,
			'on_read_requests_activate': self.sig_request_open,
			'on_send_request_activate': self.sig_request_new,
			'on_request_wait_activate': self.sig_request_wait,
			'on_opt_save_activate': lambda x: options.options.save(),
			'on_menubar_icons_activate': lambda x: self.sig_menubar('icons'),
			'on_menubar_text_activate': lambda x: self.sig_menubar('text'),
			'on_menubar_both_activate': lambda x: self.sig_menubar('both'),
			'on_mode_normal_activate': lambda x: self.sig_mode_change(False),
			'on_mode_pda_activate': lambda x: self.sig_mode_change(True),
			'on_opt_form_tab_top_activate': lambda x: self.sig_form_tab('top'),
			'on_opt_form_tab_left_activate': lambda x: self.sig_form_tab('left'),
			'on_opt_form_tab_right_activate': lambda x: self.sig_form_tab('right'),
			'on_opt_form_tab_bottom_activate': lambda x: self.sig_form_tab('bottom'),
			'on_opt_form_tab_orientation_horizontal_activate': lambda x: self.sig_form_tab_orientation(0),
			'on_opt_form_tab_orientation_vertical_activate': lambda x: self.sig_form_tab_orientation(90),
			'on_help_index_activate': self.sig_help_index,
			'on_help_contextual_activate': self.sig_help_context,
			'on_help_tips_activate': self.sig_tips,
			'on_help_licence_activate': self.sig_licence,
			'on_about_activate': self.sig_about,
			'on_shortcuts_activate' : self.sig_shortcuts,
			'on_db_new_activate': self.sig_db_new,
			'on_db_restore_activate': self.sig_db_restore,
			'on_db_backup_activate': self.sig_db_dump,
			'on_db_drop_activate': self.sig_db_drop,
			'on_admin_password_activate': self.sig_db_password,
		}
		for signal in dict:
			self.glade.signal_connect(signal, dict[signal])

		self.buttons = {}
		for button in ('but_new', 'but_save', 'but_remove', 'but_search', 'but_previous', 'but_next', 'but_action', 'but_open', 'but_print', 'but_close', 'but_reload', 'but_switch','but_attach'):
			self.glade.signal_connect('on_'+button+'_clicked', self._sig_child_call, button)
			self.buttons[button]=self.glade.get_widget(button)

		menus = {
			'form_del': 'but_remove',
			'form_new': 'but_new',
			'form_copy': 'but_copy',
			'form_reload': 'but_reload',
			'form_log': 'but_log',
			'form_open': 'but_open',
			'form_search': 'but_search',
			'form_previous': 'but_previous',
			'form_next': 'but_next',
			'form_save': 'but_save',
			'goto_id': 'but_goto_id',
			'form_print': 'but_print',
			'form_print_html': 'but_print_html',
			'form_save_as': 'but_save_as',
			'form_import': 'but_import',
			'form_filter': 'but_filter',
			'form_repeat': 'but_print_repeat'
		}
		for menu in menus:
			self.glade.signal_connect('on_'+menu+'_activate', self._sig_child_call, menus[menu])

		spool = service.LocalService('spool')
		spool.subscribe('gui.window', self.win_add)

		self.sb_set()

		def fnc_menuitem(menuitem, opt_name):
			options.options[opt_name] = menuitem.get_active()
		dict = {
			'on_opt_print_preview_activate': (fnc_menuitem, 'printer.preview', 'opt_print_preview'),
			'on_opt_form_toolbar_activate': (fnc_menuitem, 'form.toolbar', 'opt_form_toolbar'),
		}
		self.glade.get_widget('menubar_'+(options.options['client.toolbar'] or 'both')).set_active(True)
		self.sig_menubar(options.options['client.toolbar'] or 'both')
		self.glade.get_widget('opt_form_tab_'+(options.options['client.form_tab'] or 'left')).set_active(True)
		self.sig_form_tab(options.options['client.form_tab'] or 'left')
		self.glade.get_widget('opt_form_tab_orientation_'+(str(options.options['client.form_tab_orientation']) or '0')).set_active(True)
		self.sig_form_tab_orientation(options.options['client.form_tab_orientation'] or 0)
		if options.options['client.modepda']:
			self.glade.get_widget('mode_pda').set_active(True)
		else:
			self.glade.get_widget('mode_normal').set_active(True)
		self.sig_mode()
		for signal in dict:
			self.glade.signal_connect(signal, dict[signal][0], dict[signal][1])
			self.glade.get_widget(dict[signal][2]).set_active(int(bool(options.options[dict[signal][1]])))

		# Adding a timer the check to requests
		gobject.timeout_add(5 * 60 * 1000, self.request_set)

	def theme_select(self, widget, theme):
		options.options['client.theme'] = theme
		common.theme_set()
		self.window.show_all()
		return True

	def sig_mode_change(self, pda_mode=False):
		options.options['client.modepda'] = pda_mode
		return self.sig_mode()

	def sig_mode(self):
		pda_mode = options.options['client.modepda']
		#
		# Put here specific code for PDA (or not)
		#
		if pda_mode:
			self.status_bar_main.hide()
		else:
			self.status_bar_main.show()
		return pda_mode

	def sig_menubar(self, option):
		options.options['client.toolbar'] = option
		if option=='both':
			self.toolbar.set_style(gtk.TOOLBAR_BOTH)
		elif option=='text':
			self.toolbar.set_style(gtk.TOOLBAR_TEXT)
		elif option=='icons':
			self.toolbar.set_style(gtk.TOOLBAR_ICONS)
	
	def sig_form_tab(self, option):
		options.options['client.form_tab'] = option
	
	def sig_form_tab_orientation(self, option):
		options.options['client.form_tab_orientation'] = option

	def sig_win_next(self, args):
		pn = self.notebook.get_current_page()
		if pn == len(self.pages)-1:
			pn = -1
		self.notebook.set_current_page(pn+1)

	def sig_win_prev(self, args):
		pn = self.notebook.get_current_page()
		self.notebook.set_current_page(pn-1)

	def sig_user_preferences(self, *args):
		try:
			actions = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'meta', False, [('res.users',False)], True, rpc.session.context, True)

			win = win_preference.win_preference('res.users', rpc.session.uid, actions, parent=self.window)
			if win.run():
				rpc.session.context_reload()
			return True
		except:
			return False

	def sig_win_close(self, *args):
		self._sig_child_call(args[0], 'but_close')

	def sig_request_new(self, args=None):
		obj = service.LocalService('gui.window')
		try:
			return obj.create(None, 'res.request', False, [('act_from','=',rpc.session.uid)], 'form', mode='form,tree')
		except:
			return False

	def sig_request_open(self, args=None):
		ids,ids2 = self.request_set()
		obj = service.LocalService('gui.window')
		try:
			return obj.create(False, 'res.request', ids, [('act_to','=',rpc.session.uid)], 'form', mode='tree,form')
		except:
			return False

	def sig_request_wait(self, args=None):
		ids,ids2 = self.request_set()
		obj = service.LocalService('gui.window')
		try:
			return obj.create(False, 'res.request', ids, [('act_from','=',rpc.session.uid), ('state','=','waiting')], 'form', mode='tree,form')
		except:
			return False

	def request_set(self):
		try:
			uid = rpc.session.uid
			ids,ids2 = rpc.session.rpc_exec_auth_try('/object', 'execute', 'res.request', 'request_get')
			if len(ids):
				message = _('%s request(s)') % len(ids)
			else:
				message = _('No request')
			if len(ids2):
				message += _(' - %s pending request(s)') % len(ids2)
			id = self.sb_requests.get_context_id('message')
			self.sb_requests.push(id, message)
			return (ids,ids2)
		except:
			return ([],[])

	def sig_login(self, widget=None, dbname=False, res=None):
		try:
			if not res:
				try:
					l = db_login()
					res = l.run(dbname=dbname, parent=self.window)
				except 'QueryCanceled':
					return False
			self.sig_logout(widget)
			log_response = rpc.session.login(*res)
			if log_response==1:
				options.options.save()
				self.sig_home_new()
				if res[4] == 'https://':
					self.secure_img.show()
				else:
					self.secure_img.hide()
				self.request_set()
			elif log_response==-1:
				common.message(_('Connection error !\nUnable to connect to the server !'))
			elif log_response==-2:
				common.message(_('Connection error !\nBad username or password !'))
		except rpc.rpc_exception, e:
			(e1,e2) = e
			rpc.session.logout()
			common.error(_('Connection Error !'),e1,e2)
		return True

	def sig_logout(self, widget):
		res = True
		while res:
			wid = self._wid_get()
			if wid:
				if 'but_close' in wid.handlers:
					res = wid.handlers['but_close'][1]()
				if not res:
					return False
				res = self._win_del()
			else:
				res = False
		id = self.sb_requests.get_context_id('message')
		self.sb_requests.push(id, '')
		id = self.sb_username.get_context_id('message')
		self.sb_username.push(id, _('Not logged !'))
		id = self.sb_servername.get_context_id('message')
		self.sb_servername.push(id, _('Press Ctrl+O to login'))
		self.secure_img.hide()
		rpc.session.logout()
		return True
		
	def sig_help_index(self, widget):
		tools.launch_browser('http://tinyerp.com/documentation/user-manual/')

	def sig_help_context(self, widget):
		model = self._wid_get().model
		l = rpc.session.context.get('lang','en')
		tools.launch_browser('http://tinyerp.org/scripts/context_index.php?model=%s&lang=%s' % (model,l))

	def sig_tips(self, *args):
		common.tipoftheday(self.window)
		
	def sig_licence(self, widget):
		dialog = glade.XML(common.terp_path("terp.glade"), "win_licence", gettext.textdomain())
		dialog.get_widget('win_licence').set_transient_for(self.window)
		dialog.signal_connect("on_but_ok_pressed", lambda obj: dialog.get_widget('win_licence').destroy())

	def sig_about(self, widget):
		about = glade.XML(common.terp_path("terp.glade"), "win_about", gettext.textdomain())
		about.get_widget('win_about').set_transient_for(self.window)
		buffer = about.get_widget('textview2').get_buffer()
		about_txt = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
		buffer.set_text(about_txt % tinyerp_version)
		about.signal_connect("on_but_ok_pressed", lambda obj: about.get_widget('win_about').destroy())

	def sig_shortcuts(self, widget):
		shortcuts_win = glade.XML(common.terp_path('terp.glade'), 'shortcuts_dia', gettext.textdomain())
		shortcuts_win.get_widget('shortcuts_dia').set_transient_for(self.window)
		shortcuts_win.signal_connect("on_but_ok_pressed", lambda obj: shortcuts_win.get_widget('shortcuts_dia').destroy())

	def sig_win_new(self, widget=None, type='menu_id'):
		try:
			act_id = rpc.session.rpc_exec_auth('/object', 'execute', 'res.users', 'read', [rpc.session.uid], [type,'name'], rpc.session.context)
		except:
			return False
		id = self.sb_username.get_context_id('message')
		self.sb_username.push(id, act_id[0]['name'] or '')
		id = self.sb_servername.get_context_id('message')
		data = urlparse.urlsplit(rpc.session._url)
		self.sb_servername.push(id, data[0]+':'+(data[1] and '//'+data[1] or data[2])+' ['+options.options['login.db']+']')
		if not act_id[0][type]:
			common.warning('You can not log into the system !\nAsk the administrator to verify\nyou have an action defined for your user.','Access Denied !')
			rpc.session.logout()
			return False
		act_id = act_id[0][type][0]
		obj = service.LocalService('action.main')
		win = obj.execute(act_id, {'window':self.window})
	
	def sig_home_new(self, widget=None):
		return self.sig_win_new(widget, type='action_id')

	def sig_plugin_execute(self, widget):
		import plugins
		pn = self.notebook.get_current_page()
		datas = {'model': self.pages[pn].model, 'ids':self.pages[pn].ids_get(), 'id' : self.pages[pn].id_get()}
		plugins.execute(datas)

	def sig_quit(self, widget):
		options.options.save()
		gtk.main_quit()

	def sig_close(self, widget):
		if common.sur(_("Do you really want to quit ?"), parent=self.window):
			if not self.sig_logout(widget):
				return False
			options.options.save()
			gtk.main_quit()

	def sig_delete(self, widget, event, data=None):
		if common.sur(_("Do you really want to quit ?"), parent=self.window):
			if not self.sig_logout(widget):
				return True
			return False
		return True

	def win_add(self, win, datas):
		self.pages.append(win)
		self.notebook.append_page(win.widget, gtk.Label(win.name))
		self.notebook.set_current_page(-1)

	def message(self, message):
		id = self.status_bar.get_context_id('message')
		self.status_bar.push(id, message)

	def sb_set(self, view=None):
		if view==None:
			view = self._wid_get()
		for x in self.buttons:
			if self.buttons[x]:
				self.buttons[x].set_sensitive(view and (x in view.handlers))

	def _win_del(self):
		pn = self.notebook.get_current_page()
		if pn != -1:
			self.notebook.disconnect(self.sig_id)
			page = self.pages.pop(pn)
			self.notebook.remove_page(pn)
#			if self.last_page > self.current_page :
#				self.notebook.set_current_page(self.last_page-1)
#			else:
#				self.notebook.set_current_page(self.last_page)
			self.sig_id = self.notebook.connect_after('switch-page', self._sig_page_changt)
			self.sb_set()

			page.destroy()
			del page
		return self.notebook.get_current_page() != -1

	def _wid_get(self):
		pn = self.notebook.get_current_page()
		if pn == -1:
			return False
		return self.pages[pn]

	def _sig_child_call(self, widget, button_name, *args):
		wid = self._wid_get()
		if wid:
			res = True
			if button_name in wid.handlers:
				res = wid.handlers[button_name][1]()
			if button_name=='but_close' and res:
				self._win_del()

	def _sig_page_changt(self, widget=None, *args): 
		self.last_page = self.current_page
		self.current_page = self.notebook.get_current_page()
		self.sb_set()

	def sig_db_new(self, widget):
		if not self.sig_logout(widget):
			return False
		dia = db_create(self.sig_login)
		res = dia.run(self.window)
		if res:
			options.options.save()
		return res

	def sig_db_drop(self, widget):
		if not self.sig_logout(widget):
			return False
		# 1) choose db (selection)
		url, db_name, passwd = self._choose_db_select(_('Delete a database'))
		if not db_name:
			return

		try:
			rpc.session.db_exec(url, 'drop', passwd, db_name)
			common.message(_("Database dropped successfully !"), parent=self.window)
		except Exception, e:
			if ('faultString' in e and e.faultString=='AccessDenied:None') or str(e)=='AccessDenied':
				common.warning(_('Bad database administrator password !'),_("Could not drop database."), parent=self.window)
			else:
				common.warning(_("Couldn't drop database"), parent=self.window)

	def sig_db_restore(self, widget):
		# 1) choose file
			
		chooser = gtk.FileChooserDialog(title='Open...', action=gtk.FILE_CHOOSER_ACTION_OPEN,
										buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), parent=self.window)
		filename = False
		res = chooser.run()
		if res == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
		chooser.destroy()
		if not filename:
			return

		# 2) choose db (text entry) ou selection?
		#	-> if db doesn't exist: createdb
		#	-> if it exist: refuse
		url, db_name, passwd = self._choose_db_ent()
		if db_name:
			try:
				f = file(filename, 'rb')
				data_b64 = base64.encodestring(f.read())
				f.close()
				rpc.session.db_exec(url, 'restore', passwd, db_name, data_b64)
				common.message(_("Database restored successfully !"), parent=self.window)
			except Exception,e:
				if ('faultString' in e and e.faultString=='AccessDenied:None') or str(e)=='AccessDenied':
					common.warning(_('Bad database administrator password !'),_("Could not restore database."), parent=self.window)
				else:
					common.warning(_("Couldn't restore database"), parent=self.window)
		
	def sig_db_password(self, widget):
		dialog = glade.XML(common.terp_path("terp.glade"), "dia_passwd_change", gettext.textdomain())
		win = dialog.get_widget('dia_passwd_change')
		win.set_transient_for(self.window)
		server_widget = dialog.get_widget('ent_server')
		old_pass_widget = dialog.get_widget('old_passwd')
		new_pass_widget = dialog.get_widget('new_passwd')
		new_pass2_widget = dialog.get_widget('new_passwd2')
		change_button = dialog.get_widget('but_server_change')
		change_button.connect_after('clicked', lambda a,b: _server_ask(b), server_widget)

		host = options.options['login.server']
		port = options.options['login.port']
		protocol = options.options['login.protocol']
		url = '%s%s:%s' % (protocol, host, port)
		server_widget.set_text(url)

		res = win.run()
		if res == gtk.RESPONSE_OK:
			url = server_widget.get_text()
			old_passwd = old_pass_widget.get_text()
			new_passwd = new_pass_widget.get_text()
			new_passwd2 = new_pass2_widget.get_text()
			if new_passwd != new_passwd2:
				common.warning(_("Confirmation password do not match new password, operation cancelled!"), _("Validation Error."), parent=self.window)
			else:
				try:
					rpc.session.db_exec(url, 'change_admin_password', old_passwd, new_passwd)
				except Exception,e:
					if ('faultString' in e and e.faultString=='AccessDenied:None') or str(e)=='AccessDenied':
						common.warning(_("Could not change password database."),_('Bas password provided !'), parent=self.window)
					else:
						common.warning(_("Error, password not changed."), parent=self.window)
		win.destroy()

	def sig_db_dump(self, widget):
		# 1) choose db (selection)
		url, db_name, passwd = self._choose_db_select(_('Backup a database'))
		if not db_name:
			return

		# 2) choose file
		chooser = gtk.FileChooserDialog(title='Save As...', action=gtk.FILE_CHOOSER_ACTION_SAVE,
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), parent=self.window)
		res = chooser.run()

		filename = False
		if res == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
		chooser.destroy()

		if filename:
			try:
				dump_b64 = rpc.session.db_exec(url, 'dump', passwd, db_name)
				dump = base64.decodestring(dump_b64)
				f = file(filename, 'wb')
				f.write(dump)
				f.close()
				common.message(_("Database backuped successfully !"), parent=self.window)
			except:
				common.warning(_("Couldn't backup database."), parent=self.window)

	def _choose_db_select(self, title=_("Backup a database")):
		def refreshlist(widget, db_widget, label, url):
			res = _refresh_dblist(db_widget, url)
			if res == -1:
				label.set_label('<b>'+_('Could not connect to server !')+'</b>')
				db_widget.hide()
				label.show()
			elif res==0:
				label.set_label('<b>'+_('No database found, you must create one !')+'</b>')
				db_widget.hide()
				label.show()
			else:
				label.hide()
				db_widget.show()
			return res

		def refreshlist_ask(widget, server_widget, db_widget, label):
			url = _server_ask(server_widget)
			if not url:
				return None
			refreshlist(widget, db_widget, label, url)
			return  url

		dialog = glade.XML(common.terp_path("terp.glade"), "win_db_select", gettext.textdomain())
		win = dialog.get_widget('win_db_select')
		win.set_transient_for(self.window)

		pass_widget = dialog.get_widget('ent_passwd_select')
		server_widget = dialog.get_widget('ent_server_select')
		db_widget = dialog.get_widget('combo_db_select')
		label = dialog.get_widget('label_db_select')


		dialog.get_widget('db_select_label').set_markup('<b>'+title+'</b>')

		protocol = options.options['login.protocol']
		url = '%s%s:%s' % (protocol, options.options['login.server'], options.options['login.port'])
		server_widget.set_text(url)

		liststore = gtk.ListStore(str)
		db_widget.set_model(liststore)

		refreshlist(None, db_widget, label, url)
		change_button = dialog.get_widget('but_server_select')
		change_button.connect_after('clicked', refreshlist_ask, server_widget, db_widget, label)

		cell = gtk.CellRendererText()
		db_widget.pack_start(cell, True)
		db_widget.add_attribute(cell, 'text', 0)

		res = win.run()

		db = False
		url = False
		passwd = False
		if res == gtk.RESPONSE_OK:
			db = db_widget.get_active_text()
			url = server_widget.get_text()
			passwd = pass_widget.get_text()
		win.destroy()
		return (url,db,passwd)
	
	def _choose_db_ent(self):
		dialog = glade.XML(common.terp_path("terp.glade"), "win_db_ent", gettext.textdomain())
		win = dialog.get_widget('win_db_ent')
		win.set_transient_for(self.window)

		db_widget = dialog.get_widget('ent_db')
		widget_pass = dialog.get_widget('ent_password')
		widget_url = dialog.get_widget('ent_server')

		protocol = options.options['login.protocol']
		url = '%s://%s:%s' % (protocol, options.options['login.server'], options.options['login.port'])
		widget_url.set_text(url)

		change_button = dialog.get_widget('but_server_change')
		change_button.connect_after('clicked', lambda a,b: _server_ask(b), widget_url)

		res = win.run()

		db = False
		passwd = False
		url = False
		if res == gtk.RESPONSE_OK:
			db = db_widget.get_text()
			url = widget_url.get_text()
			passwd = widget_pass.get_text()
		win.destroy()
		return url, db, passwd

