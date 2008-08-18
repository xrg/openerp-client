# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
    lang_list.append( ('en_US','English') )
    for key,val in lang_list:
        liststore.insert(0, (val,key))
    lang_widget.set_active(0)
    return lang_list

def _server_ask(server_widget, parent=None):
    result = False
    win_gl = glade.XML(common.terp_path("terp.glade"),"win_server",gettext.textdomain())
    win = win_gl.get_widget('win_server')
    if not parent:
        parent = service.LocalService('gui.main').window
    win.set_transient_for(parent)
    win.set_icon(common.TINYERP_ICON)
    win.show_all()
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
        protocol = protocol[protocol_widget.get_active_text()]
        url = '%s%s:%s' % (protocol, host_widget.get_text(), port_widget.get_text())
        server_widget.set_text(url)
        result = url
    parent.present()
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

    def refreshlist_ask(self,widget, server_widget, db_widget, label, butconnect = False, url=False, parent=None):
        url = _server_ask(server_widget, parent) or url
        return self.refreshlist(widget, db_widget, label, url, butconnect)

    def run(self, dbname=None, parent=None):
        uid = 0
        win = self.win_gl.get_widget('win_login')
        if not parent:
            parent = service.LocalService('gui.main').window
        win.set_transient_for(parent)
        win.set_icon(common.TINYERP_ICON)
        win.show_all()
        img = self.win_gl.get_widget('image_tinyerp')
        img.set_from_file(common.terp_path_pixmaps('tinyerp.png'))
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
        change_button.connect_after('clicked', self.refreshlist_ask, server_widget, db_widget, label, but_connect, url, win)

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
            parent.present()
            win.destroy()
            raise Exception('QueryCanceled')
        if res <> gtk.RESPONSE_OK:
            parent.present()
            win.destroy()
            raise Exception('QueryCanceled')
        parent.present()
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
            label.set_markup('<b>'+_('Can not connect to server, please change it !')+'</b>')
            self.dialog.get_widget('button_db_ok').set_sensitive(False)
        return sensitive

    def server_change(self, widget=None, parent=None):
        url = _server_ask(self.server_widget)
        try:
            if self.lang_widget and url:
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
        win.set_default_response(gtk.RESPONSE_OK)
        if not parent:
            parent = service.LocalService('gui.main').window
        win.set_transient_for(parent)
        win.show_all()
        lang_dict = {}
        pass_widget = self.dialog.get_widget('ent_password_new')
        self.server_widget = self.dialog.get_widget('ent_server_new')
        change_button = self.dialog.get_widget('but_server_new')
        self.lang_widget = self.dialog.get_widget('db_create_combo')
        self.db_widget = self.dialog.get_widget('ent_db_new')
        demo_widget = self.dialog.get_widget('check_demo')
        demo_widget.set_active(True)

        change_button.connect_after('clicked', self.server_change, win)
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
        parent.present()
        win.destroy()

        if res == gtk.RESPONSE_OK:
            try:
                id=rpc.session.db_exec(url, 'list')
                if db_name in id:
                    raise Exception('DbExist')
                id = rpc.session.db_exec(url, 'create', passwd, db_name, demo_data, langreal)
                win = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
                win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
                vbox = gtk.VBox(False, 0)
                hbox = gtk.HBox(False, 13)
                hbox.set_border_width(10)
                img = gtk.Image()
                img.set_from_stock('gtk-dialog-info', gtk.ICON_SIZE_DIALOG)
                hbox.pack_start(img, expand=True, fill=False)
                vbox2 = gtk.VBox(False, 0)
                label = gtk.Label()
                label.set_markup(_('<b>Operation in progress</b>'))
                label.set_alignment(0.0, 0.5)
                vbox2.pack_start(label, expand=True, fill=False)
                vbox2.pack_start(gtk.HSeparator(), expand=True, fill=True)
                vbox2.pack_start(gtk.Label(_("Please wait,\nthis operation may take a while...")), expand=True, fill=False)
                hbox.pack_start(vbox2, expand=True, fill=True)
                vbox.pack_start(hbox)
                pb = gtk.ProgressBar()
                pb.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
                vbox.pack_start(pb, expand=True, fill=False)
                win.add(vbox)
                if not parent:
                    parent = service.LocalService('gui.main').window
                win.set_transient_for(parent)
                win.show_all()
                self.timer = gobject.timeout_add(1000, self.progress_timeout, pb, url, passwd, id, win, db_name, parent)
            except Exception, e:
                if e.args == ('DbExist',):
                    common.warning(_("Could not create database."),_('Database already exists !'))
                elif ('faultString' in e and e.faultString=='AccessDenied:None') or str(e)=='AccessDenied':
                    common.warning(_('Bad database administrator password !'), _("Could not create database."))
                else:
                    print e
                    print str(e)
                    print e.faultString
                    print e.faultCode
                    common.warning(_("Could not create database."),_('Error during database creation !'))

    def progress_timeout(self, pbar, url, passwd, id, win, dbname, parent=None):
        try:
            progress,users = rpc.session.db_exec_no_except(url, 'get_progress', passwd, id)
        except:
            win.destroy()
            common.warning(_("The server crashed during installation.\nWe suggest you to drop this database."),_("Error during database creation !"))
            return False

        pbar.pulse()
        if progress == 1.0:
            win.destroy()

            pwdlst = '\n'.join(map(lambda x: '    - %s: %s / %s' % (x['name'],x['login'],x['password']), users))
            dialog = glade.XML(common.terp_path("terp.glade"), "dia_dbcreate_ok", gettext.textdomain())
            win = dialog.get_widget('dia_dbcreate_ok')
            if not parent:
                parent = service.LocalService('gui.main').window
            win.set_transient_for(parent)
            win.show_all()
            buffer = dialog.get_widget('dia_tv').get_buffer()

            buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
            iter_start = buffer.get_start_iter()
            buffer.insert(iter_start, _('The following users have been installed on your database:')+'\n\n'+ pwdlst + '\n\n'+_('You can now connect to the database as an administrator.'))
            res = win.run()
            parent.present()
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
        self.window.set_icon(common.TINYERP_ICON)

        self.notebook = gtk.Notebook()
        self.notebook.popup_enable()
        self.notebook.set_scrollable(True)
        self.sig_id = self.notebook.connect_after('switch-page', self._sig_page_changt)
        vbox = self.glade.get_widget('vbox_main')
        vbox.pack_start(self.notebook, expand=True, fill=True)

        self.shortcut_menu = self.glade.get_widget('shortcut')

        #
        # Code to add themes to the options->theme menu
        #
        submenu = gtk.Menu()
        menu = self.glade.get_widget('menu_theme')
        old = None
        themes_path = common.terp_path('themes')
        if themes_path:
            for dname in os.listdir(themes_path):
                if dname.startswith('.'):
                    continue
                fname = common.terp_path(os.path.join('themes', dname, 'gtkrc'))
                if fname and os.path.isfile(fname):
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
            'on_but_menu_clicked': self.sig_win_menu,
            'on_win_new_activate': self.sig_win_menu,
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


        # we now create the icon for the attachment button when there are attachments
        self.__img_no_attachments = gtk.Image()
        pxbf = self.window.render_icon(self.buttons['but_attach'].get_stock_id(), self.toolbar.get_icon_size())
        self.__img_no_attachments.set_from_pixbuf(pxbf)
        self.__img_no_attachments.show()

        pxbf = pxbf.copy()
        w, h = pxbf.get_width(), pxbf.get_height()
        overlay = self.window.render_icon(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU)
        ow, oh = overlay.get_width(), overlay.get_height()
        overlay.composite(pxbf,
                        0, h - oh,
                        ow, oh,
                        0, h - oh,
                        1.0, 1.0,
                        gtk.gdk.INTERP_NEAREST,
                        255)

        self.__img_attachments = gtk.Image()
        self.__img_attachments.set_from_pixbuf(pxbf)
        self.__img_attachments.show()

        self.sb_set()

        settings = gtk.settings_get_default()
        settings.set_long_property('gtk-button-images', 1, 'TinyERP:gui.main')

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


    def shortcut_edit(self, widget, model='ir.ui.menu'):
        obj = service.LocalService('gui.window')
        domain = [('user_id', '=', rpc.session.uid), ('resource', '=', model)]
        obj.create(False, 'ir.ui.view_sc', res_id=None, domain=domain, view_type='form', mode='tree,form')

    def shortcut_set(self, sc=None):
        def _action_shortcut(widget, action):
            if action:
                ctx = rpc.session.context.copy()
                obj = service.LocalService('action.main')
                obj.exec_keyword('tree_but_open', {'model': 'ir.ui.menu', 'id': action[0],
                    'ids': [action[0]], 'report_type': 'pdf', 'window': self.window}, context=ctx)

        if sc is None:
            uid = rpc.session.uid
            sc = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.ui.view_sc', 'get_sc', uid, 'ir.ui.menu', rpc.session.context) or []

        menu = gtk.Menu()
        for s in sc:
            menuitem = gtk.MenuItem(s['name'])
            menuitem.connect('activate', _action_shortcut, s['res_id'])
            menu.add(menuitem)

        menu.add(gtk.SeparatorMenuItem())
        menuitem = gtk.MenuItem(_('Edit'))
        menuitem.connect('activate', self.shortcut_edit)
        menu.add(menuitem)

        menu.show_all()
        self.shortcut_menu.set_submenu(menu)
        self.shortcut_menu.set_sensitive(True)

    def shortcut_unset(self):
        menu = gtk.Menu()
        menu.show_all()
        self.shortcut_menu.set_submenu(menu)
        self.shortcut_menu.set_sensitive(False)

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
        win =win_preference.win_preference(parent=self.window)
        win.run()
        return True

    def sig_win_close(self, *args):
        self._sig_child_call(args[0], 'but_close')

    def sig_request_new(self, args=None):
        obj = service.LocalService('gui.window')
        try:
            return obj.create(None, 'res.request', False,
                    [('act_from', '=', rpc.session.uid)], 'form',
                    mode='form,tree', window=self.window,
                    context={'active_test': False})
        except:
            return False

    def sig_request_open(self, args=None):
        ids,ids2 = self.request_set()
        obj = service.LocalService('gui.window')
        try:
            return obj.create(False, 'res.request', ids,
                    [('act_to', '=', rpc.session.uid), ('active', '=', True)],
                    'form', mode='tree,form', window=self.window,
                    context={'active_test': False})
        except:
            return False

    def sig_request_wait(self, args=None):
        ids,ids2 = self.request_set()
        obj = service.LocalService('gui.window')
        try:
            return obj.create(False, 'res.request', ids,
                    [('act_from', '=', rpc.session.uid),
                        ('state', '=', 'waiting'), ('active', '=', True)],
                    'form', mode='tree,form', window=self.window,
                    context={'active_test': False})
        except:
            return False

    def request_set(self):
        try:
            uid = rpc.session.uid
            ids,ids2 = rpc.session.rpc_exec_auth_try('/object', 'execute',
                    'res.request', 'request_get')
            if len(ids):
                message = _('%s request(s)') % len(ids)
            else:
                message = _('No request')
            if len(ids2):
                message += _(' - %s request(s) sended') % len(ids2)
            id = self.sb_requests.get_context_id('message')
            self.sb_requests.push(id, message)
            return (ids,ids2)
        except:
            return ([],[])

    def sig_login(self, widget=None, dbname=False):
        RES_OK = 1
        RES_BAD_PASSWORD = -2
        RES_CNX_ERROR = -1

        try:
            log_response = RES_BAD_PASSWORD
            res = None
            while log_response == RES_BAD_PASSWORD:
                try:
                    l = db_login()
                    res = l.run(dbname=dbname, parent=self.window)
                except Exception, e:
                    if e.args == ('QueryCanceled',):
                        return False
                    raise
                service.LocalService('gui.main').window.present()
                self.sig_logout(widget)
                log_response = rpc.session.login(*res)
                if log_response == RES_OK:
                    options.options.save()
                    id = self.sig_win_menu(quiet=False)
                    if id:
                        self.sig_home_new(quiet=True, except_id=id)
                    if res[4] == 'https://':
                        self.secure_img.show()
                    else:
                        self.secure_img.hide()
                    self.request_set()
                elif log_response == RES_CNX_ERROR:
                    common.message(_('Connection error !\nUnable to connect to the server !'))
                elif log_response == RES_BAD_PASSWORD:
                    common.message(_('Connection error !\nBad username or password !'))
        except rpc.rpc_exception:
            rpc.session.logout()
            raise
        self.glade.get_widget('but_menu').set_sensitive(True)
        self.glade.get_widget('user').set_sensitive(True)
        self.glade.get_widget('form').set_sensitive(True)
        self.glade.get_widget('plugins').set_sensitive(True)
        return True

    def sig_logout(self, widget):
        res = True
        while res:
            wid = self._wid_get()
            if wid:
                if 'but_close' in wid.handlers:
                    res = wid.handlers['but_close']()
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
        self.shortcut_unset()
        self.glade.get_widget('but_menu').set_sensitive(False)
        self.glade.get_widget('user').set_sensitive(False)
        self.glade.get_widget('form').set_sensitive(False)
        self.glade.get_widget('plugins').set_sensitive(False)
        rpc.session.logout()
        return True

    def sig_help_index(self, widget):
        tools.launch_browser(options.options['help.index'])

    def sig_help_context(self, widget):
        model = self._wid_get().model
        l = rpc.session.context.get('lang','en_US')
        tools.launch_browser(options.options['help.context']+'?model=%s&lang=%s' % (model,l))

    def sig_tips(self, *args):
        common.tipoftheday(self.window)

    def sig_licence(self, widget):
        dialog = glade.XML(common.terp_path("terp.glade"), "win_licence", gettext.textdomain())
        dialog.signal_connect("on_but_ok_pressed", lambda obj: dialog.get_widget('win_licence').destroy())

        win = dialog.get_widget('win_licence')
        win.set_transient_for(self.window)
        win.show_all()

    def sig_about(self, widget):
        about = glade.XML(common.terp_path("terp.glade"), "win_about", gettext.textdomain())
        buffer = about.get_widget('textview2').get_buffer()
        about_txt = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        buffer.set_text(about_txt % tinyerp_version)
        about.signal_connect("on_but_ok_pressed", lambda obj: about.get_widget('win_about').destroy())

        win = about.get_widget('win_about')
        win.set_transient_for(self.window)
        win.show_all()

    def sig_shortcuts(self, widget):
        shortcuts_win = glade.XML(common.terp_path('terp.glade'), 'shortcuts_dia', gettext.textdomain())
        shortcuts_win.signal_connect("on_but_ok_pressed", lambda obj: shortcuts_win.get_widget('shortcuts_dia').destroy())

        win = shortcuts_win.get_widget('shortcuts_dia')
        win.set_transient_for(self.window)
        win.show_all()

    def sig_win_menu(self, widget=None, quiet=True):
        for p in range(len(self.pages)):
            if self.pages[p].model=='ir.ui.menu':
                self.notebook.set_current_page(p)
                return True
        res = self.sig_win_new(widget, type='menu_id', quiet=quiet)
        if not res:
            return self.sig_win_new(widget, type='action_id', quiet=quiet)
        return res

    def sig_win_new(self, widget=None, type='menu_id', quiet=True, except_id=False):
        try:
            act_id = rpc.session.rpc_exec_auth('/object', 'execute', 'res.users',
                    'read', [rpc.session.uid], [type,'name'], rpc.session.context)
        except:
            return False
        id = self.sb_username.get_context_id('message')
        self.sb_username.push(id, act_id[0]['name'] or '')
        id = self.sb_servername.get_context_id('message')
        data = urlparse.urlsplit(rpc.session._url)
        self.sb_servername.push(id, data[0]+':'+(data[1] and '//'+data[1] \
                or data[2])+' ['+options.options['login.db']+']')
        if not act_id[0][type]:
            if quiet:
                return False
            common.warning(_("You can not log into the system !\nAsk the administrator to verify\nyou have an action defined for your user."),'Access Denied !')
            rpc.session.logout()
            return False
        act_id = act_id[0][type][0]
        if except_id and act_id == except_id:
            return act_id
        obj = service.LocalService('action.main')
        win = obj.execute(act_id, {'window':self.window})
        try:
            user = rpc.session.rpc_exec_auth_wo('/object', 'execute', 'res.users',
                    'read', [rpc.session.uid], [type,'name'], rpc.session.context)
            if user[0][type]:
                act_id = user[0][type][0]
        except:
            pass
        return act_id

    def sig_home_new(self, widget=None, quiet=True, except_id=False):
        return self.sig_win_new(widget, type='action_id', quiet=quiet,
                except_id=except_id)

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

    def __attachment_callback(self, view, objid):
        current_view = self._wid_get()
        current_id = current_view and current_view.id_get()
        if current_view == view and objid == current_id:
            cpt = None
            if objid and view.screen.current_view.view_type == 'form':
                cpt = rpc.session.rpc_exec_auth('/object', 'execute', 
                                                'ir.attachment', 'search_count', 
                                                [('res_model', '=', view.model), ('res_id', '=', objid)])
            if cpt:
                self.buttons['but_attach'].set_icon_widget(self.__img_attachments)
                self.buttons['but_attach'].set_label(_('Attachments (%d)') % cpt)


    def _update_attachment_button(self, view = None):
        """
        Update the attachment icon for display the number of attachments
        """
        if not view:
            view = self._wid_get()
        
        id = view and view.id_get()
        gobject.timeout_add(1500, self.__attachment_callback, view, id)
        self.buttons['but_attach'].set_icon_widget(self.__img_no_attachments)
        self.buttons['but_attach'].set_label(_('Attachments'))


    def sb_set(self, view=None):
        if not view:
            view = self._wid_get()
        self._update_attachment_button(view)
        for x in self.buttons:
            if self.buttons[x]:
                self.buttons[x].set_sensitive(view and (x in view.handlers))

    def _win_del(self):
        pn = self.notebook.get_current_page()
        if pn != -1:
            self.notebook.disconnect(self.sig_id)
            page = self.pages.pop(pn)
            self.notebook.remove_page(pn)
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
                res = wid.handlers[button_name]()
                # for those buttons, we refresh the attachment button.
                # for the "switch view" button, the action has already
                # been called by the Screen object of the view (wid)
                if button_name in ('but_new', 'but_remove', 'but_search', \
                                    'but_previous', 'but_next', 'but_open', \
                                    'but_close', 'but_reload', 'but_attach', 'but_goto_id'):
                    self._update_attachment_button(wid)
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
        filename = common.file_selection(_('Open...'), parent=self.window, preview=False)
        if not filename:
            return

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
        dialog = glade.XML(common.terp_path("terp.glade"), "dia_passwd_change",
                gettext.textdomain())
        win = dialog.get_widget('dia_passwd_change')
        win.set_icon(common.TINYERP_ICON)
        win.set_transient_for(self.window)
        win.show_all()
        server_widget = dialog.get_widget('ent_server')
        old_pass_widget = dialog.get_widget('old_passwd')
        new_pass_widget = dialog.get_widget('new_passwd')
        new_pass2_widget = dialog.get_widget('new_passwd2')
        change_button = dialog.get_widget('but_server_change')
        change_button.connect_after('clicked', lambda a,b: _server_ask(b, win), server_widget)

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
                common.warning(_("Confirmation password do not match " \
                        "new password, operation cancelled!"),
                        _("Validation Error."), parent=win)
            else:
                try:
                    rpc.session.db_exec(url, 'change_admin_password',
                            old_passwd, new_passwd)
                except Exception,e:
                    if ('faultString' in e and e.faultString=='AccessDenied:None') \
                            or str(e)=='AccessDenied':
                        common.warning(_("Could not change password database."),
                                _('Bas password provided !'), parent=win)
                    else:
                        common.warning(_("Error, password not changed."),
                                parent=win)
        self.window.present()
        win.destroy()

    def sig_db_dump(self, widget):
        url, db_name, passwd = self._choose_db_select(_('Backup a database'))
        if not db_name:
            return
        filename = common.file_selection(_('Save As...'),
                action=gtk.FILE_CHOOSER_ACTION_SAVE, parent=self.window, preview=False)

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

        def refreshlist_ask(widget, server_widget, db_widget, label, parent=None):
            url = _server_ask(server_widget, parent)
            if not url:
                return None
            refreshlist(widget, db_widget, label, url)
            return  url

        dialog = glade.XML(common.terp_path("terp.glade"), "win_db_select",
                gettext.textdomain())
        win = dialog.get_widget('win_db_select')
        win.set_icon(common.TINYERP_ICON)
        win.set_default_response(gtk.RESPONSE_OK)
        win.set_transient_for(self.window)
        win.show_all()

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
        change_button.connect_after('clicked', refreshlist_ask, server_widget, db_widget, label, win)

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
        self.window.present()
        win.destroy()
        return (url,db,passwd)

    def _choose_db_ent(self):
        dialog = glade.XML(common.terp_path("terp.glade"), "win_db_ent",
                gettext.textdomain())
        win = dialog.get_widget('win_db_ent')
        win.set_icon(common.TINYERP_ICON)
        win.set_transient_for(self.window)
        win.show_all()

        db_widget = dialog.get_widget('ent_db')
        widget_pass = dialog.get_widget('ent_password')
        widget_url = dialog.get_widget('ent_server')

        protocol = options.options['login.protocol']
        url = '%s%s:%s' % (protocol, options.options['login.server'],
                options.options['login.port'])
        widget_url.set_text(url)

        change_button = dialog.get_widget('but_server_change')
        change_button.connect_after('clicked', lambda a,b: _server_ask(b, win),
                widget_url)

        res = win.run()

        db = False
        passwd = False
        url = False
        if res == gtk.RESPONSE_OK:
            db = db_widget.get_text()
            url = widget_url.get_text()
            passwd = widget_pass.get_text()
        self.window.present()
        win.destroy()
        return url, db, passwd


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

