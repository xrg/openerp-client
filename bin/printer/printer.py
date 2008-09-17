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

# ------------------------------------------------------------------- #
# Module printer
# ------------------------------------------------------------------- #
#
# Supported formats: pdf
#
# Print or open a previewer
#

import os, base64, options, sys
import gc
import common
import time
import gtk

class Printer(object):

    def __init__(self):
        self.openers = {
            'pdf': self._findPDFOpener,
            'html': self._findHTMLOpener,
            'doc': self._findHTMLOpener,
            'xls': self._findHTMLOpener,
            'sxw': self._findSXWOpener,
        }

    def _findInPath(self, progs):
        lstprogs = progs[:]
        found = {}
        path = [dir for dir in os.environ['PATH'].split(':')
                if os.path.isdir(dir)]
        for dir in path:
            content = os.listdir(dir)
            for prog in progs[:]:
                if prog in content:
                    return os.path.join(dir, prog)#prog
                    
                    progs.remove(prog)
                    found[prog] = os.path.join(dir, prog)
        for prog in lstprogs:
            if prog in found:
                return found[prog]
        return ''

    def _findHTMLOpener(self):
        import webbrowser
        def opener(fn):
            webbrowser.open('file://'+fn)
        return opener

    def __opener(self, fnct):
        pid = os.fork()
        if not pid:
            pid = os.fork()
            if not pid:
                fnct()
            time.sleep(0.1)
            sys.exit(0)
        os.waitpid(pid, 0)

    def _findPDFOpener(self):
        if os.uname()[0] == 'Darwin' :
            def opener(fn):
                self.__opener( lambda: os.system('/usr/bin/open -a Preview ' + fn) )
            return opener
        if os.name == 'nt':
            if options.options['printer.preview']:
                if options.options['printer.softpath'] == 'none':
                    return lambda fn: os.startfile(fn)
                else:
                    return lambda fn: os.system(options.options['printer.softpath'] + ' ' + fn)
            else:
                return lambda fn: print_w32_filename(fn)
        else:
            if options.options['printer.preview']:
                if options.options['printer.softpath'] == 'none':
                    prog = self._findInPath(['evince', 'xpdf', 'gpdf', 'kpdf', 'epdfview', 'acroread', 'open'])
                    def opener(fn):
                        self.__opener( lambda: os.execv(prog, (os.path.basename(prog), fn) ))
                    return opener
                else:
                    def opener(fn):
                        self.__opener( lambda: os.execv(options.options['printer.softpath'], (os.path.basename(options.options['printer.softpath']), fn)) )
                    return opener
            else:
                return lambda fn: print_linux_filename(fn)
    
    def _findSXWOpener(self):
        if os.name == 'nt':
            return lambda fn: os.startfile(fn)
        else:
            if options.options['printer.softpath_html'] == 'none':
                prog = self._findInPath(['ooffice', 'ooffice2', 'openoffice', 'soffice'])
                def opener(fn):
                    pid = os.fork()
                    if not pid:
                        pid = os.fork()
                        if not pid:
                            os.execv(prog, (os.path.basename(prog),fn))
                        time.sleep(0.1)
                        sys.exit(0)
                    os.waitpid(pid, 0)
                return opener
            else:
                def opener(fn):
                    pid = os.fork()
                    if not pid:
                        pid = os.fork()
                        if not pid:
                            os.execv(options.options['printer.softpath_html'], (os.path.basename(options.options['printer.softpath_html']),fn))
                        time.sleep(0.1)
                        sys.exit(0)
                    os.waitpid(pid, 0)
                return opener

    def print_file(self, fname, ftype, preview=False):
        app_to_run = None
        try:
            filetypes = eval( options.options['extensions.filetype'] )
            (app, app_print) = filetypes[ftype]
            if options.options['printer.preview'] or preview:
                app_to_run = app
            else:
                app_to_run = app_print
        except:
            pass

        if app_to_run:
            def open_file( cmd, filename ):
                cmd = cmd % filename
                pid = os.fork()
                if not pid:
                    pid = os.fork()
                    if not pid:
                        prog, args = cmd.split(' ', 1)
                        args = [os.path.basename(prog)] + args.split(' ')
                        try:
                            os.execvp(prog, args)
                        except:
                            pass
                    time.sleep(0.1)
                    sys.exit(0)
                os.waitpid(pid, 0)

            if sys.platform in ['win32','nt']:
                if app_to_run:
                    open_file( app_to_run, fname )
                else:
                    os.startfile( fname )
            else:
                open_file( app_to_run, fname )
        else:
            finderfunc = self.openers.get(ftype)
            if not finderfunc:
                raise Exception(_('Unable to handle %s filetype') % ftype)
            opener = finderfunc()
            opener(fname)
            gc.collect()


printer = Printer()

def print_linux_filename(filename):
    common.message(_('Linux Automatic Printing not implemented.\nUse preview option !'))

def print_w32_filename(filename):
    import win32api
    win32api.ShellExecute (0, "print", filename, None, ".", 0)

def print_data(data):
    if 'result' not in data:
        common.message(_('Error no report'))
    if data.get('code','normal')=='zlib':
        import zlib
        content = zlib.decompress(base64.decodestring(data['result']))
    else:
        content = base64.decodestring(data['result'])

    if data['format'] in printer.openers.keys():
        import tempfile
        if data['format']=='html' and os.name=='nt':
            data['format']='doc'
        (fileno, fp_name) = tempfile.mkstemp('.'+data['format'], 'openerp_')
        fp = file(fp_name, 'wb+')
        fp.write(content)
        fp.close()
        os.close(fileno)
        printer.print_file(fp_name, data['format'])
    else:
        fname = common.file_selection(_('Save As...'), filename='report.' + data['format'],
                action=gtk.FILE_CHOOSER_ACTION_SAVE)
        if fname:
            try:
                fp = file(fname,'wb+')
                fp.write(content)
                fp.close()
            except:
                common.message(_('Error writing the file!'))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

