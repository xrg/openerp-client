##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

class Printer(object):

	def __init__(self):
		self.openers = {
			'pdf': self._findPDFOpener,
			'html': self._findHTMLOpener,
			'doc': self._findHTMLOpener,
			'xls': self._findHTMLOpener,
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
		if os.name == 'nt':
			return lambda fn: os.startfile(fn)
		else:
			if options.options['printer.softpath_html'] == 'none':
				prog = self._findInPath(['ooffice', 'ooffice2', 'openoffice', 'firefox', 'mozilla', 'galeon'])
				def opener(fn):
					pid = os.fork()
					if not pid:
						pid = os.fork()
						if not pid:
							os.execv(prog, (os.path.basename(prog),fn))
						sys.exit(0)
					os.wait()
				return opener
			else:
				def opener(fn):
					pid = os.fork()
					if not pid:
						pid = os.fork()
						if not pid:
							os.system(options.options['printer.softpath_html'] + ' ' + fn)
						sys.exit(0)
					os.wait()
				return opener

	def _findPDFOpener(self):
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
						pid = os.fork()
						if not pid:
							pid = os.fork()
							if not pid:
								os.execv(prog, (os.path.basename(prog), fn))
							sys.exit(0)
						os.wait()
					return opener
				else:
					def opener(fn):
						pid = os.fork()
						if not pid:
							pid = os.fork()
							if not pid:
								os.execv(options.options['printer.softpath'], (os.path.basename(options.options['printer.softpath']),fn))
							sys.exit(0)
						os.wait()
					return opener
			else:
				return lambda fn: print_linux_filename(fn)

	def print_file(self, fname, ftype):
		finderfunc = self.openers[ftype]
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
		(fileno, fp_name) = tempfile.mkstemp('.'+data['format'], 'tinyerp_')
		fp = file(fp_name, 'wb+')
		fp.write(content)
		fp.close()
		os.close(fileno)
		printer.print_file(fp_name, data['format'])
	else:
		fname = common.file_selection(_('Write Report to File'), data['format'])
		if fname:
			try:
				fp = file(fname,'wb+')
				fp.write(content)
				fp.close()
			except:
				common.message(_('Error writing the file!'))

