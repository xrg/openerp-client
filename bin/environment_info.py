import os
import sys
import optparse
import xmlrpclib
import release

class environment(object):
    def __init__(self, login, password, dbname, host='localhost', port=8069, lang= False):
        self.login = login
        self.passwd = password
        self.db = dbname
        self.host = host
        self.port = port
        self.lang = lang

    def get_server_info(self):
        login_socket = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/common' % (self.host, self.port))
        self.uid = login_socket.login(self.db, self.login, self.passwd)
        print login_socket.get_server_environment(self.lang) + self.get_client_info()
        login_socket.logout(self.db, self.login, self.passwd)
        return True

    def get_client_info(self):
        try:
            if '.bzr' in os.listdir((os.getcwd()[0:-3])):
                fp = open(os.path.join(os.getcwd()[0:-3],'.bzr/branch/last-revision'))
                rev_no = fp.read()
                fp.close()
            else:
                rev_no = 'Bazaar Not Installed !'
        except:
            rev_no = 'Bazaar Not Installed !'
        environment ='OpenERP-Client Version : %s\n'\
                     'OpenERP-Client Last Revision ID : %s'\
                      %(release.version, rev_no)
        return environment

if __name__=="__main__":

    parser = optparse.OptionParser()

    group = optparse.OptionGroup(parser, "Note",
        "This script will provide you the full environment Information" \
        " about OpenERP-Server and OpenERP-Client")

    parser.add_option_group(group)

    parser.add_option("-L", "--login", dest="login", help="Login of the user in Open ERP")
    parser.add_option("-P", "--password", dest="password", help="Password of the user in Open ERP")
    parser.add_option("-d", "--dbname", dest="dbname", help="Database name",default='terp')
    parser.add_option("-p", "--port", dest="port", help="Port",default=8069)
    parser.add_option("-s", "--host", dest="host", help="Host",default='localhost')
    parser.add_option("-l", "--lang", dest="lang", help="Lang(if not specified will take OS environment Language)",default=False)

    (options, args) = parser.parse_args()

    def check_options(cond, msg):
        if cond:
            print msg +'\nfor list of options try --help option'
            sys.exit(1)
    check_options(not (options.login),'ERROR: No Login specified !')
    check_options(not (options.password),'ERROR: No Password specified !')

    parser = environment(options.login, options.password, dbname = options.dbname, host = options.host, port = options.port,lang = options.lang)
    parser.get_server_info()