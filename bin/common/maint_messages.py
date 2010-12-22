# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 OpenERP SA. (<http://www.openerp.com>).
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

import gettext

message_no_contract = _("""
<b>An unknown error has been reported.</b>

<b>You do not have a valid OpenERP publisher warranty contract !</b>
If you are using OpenERP in production, it is highly suggested to subscribe
a publisher warranty program.

The OpenERP publisher warranty contract provides you a bugfix guarantee and an
automatic migration system so that we can fix your problems within a few
hours. If you had a publisher warranty contract, this error would have been sent
to the quality team of the OpenERP editor.

The publisher warranty program offers you:
* Automatic migrations on new versions,
* A bugfix guarantee,
* Monthly announces of potential bugs and their fixes,
* Security alerts by email and automatic migration,
* Access to the customer portal.

You can use the link bellow for more information. The detail of the error
is displayed on the second tab.
""")

message_partial_contract = _("""
<b>An unknown error has been reported.</b>

Your publisher warranty contract does not cover all modules installed in your system !
If you are using OpenERP in production, it is highly suggested to upgrade your
contract.

If you have developed your own modules or installed third party module, we
can provide you an additional publisher warranty contract for these modules. After
having reviewed your modules, our quality team will ensure they will migrate
automatically for all future stable versions of OpenERP at no extra cost.

Here is the list of modules not covered by your publisher warranty contract:
%s

You can use the link bellow for more information. The detail of the error
is displayed on the second tab.""")

#eof
