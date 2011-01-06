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
from tools import user_locale_format
HM_FORMAT = ' %H:%M:%S'
from datetime import datetime

import matplotlib
matplotlib.use('GTKCairo')

from matplotlib.font_manager import FontProperties

colorline = ['#%02x%02x%02x' % (25+((r+10)%11)*23,5+((g+1)%11)*20,25+((b+4)%11)*23) for r in range(11) for g in range(11) for b in range(11) ]
def choice_colors(n):
    if n:
        return colorline[0:-1:len(colorline)/(n+1)]
    return []


def tinygraph(subplot, type='pie', axis={}, axis_data={}, datas=[], axis_group_field={}, orientation='horizontal', overlap=1.0):
    subplot.clear()
    operators = {
        '+': lambda x,y: x+y,
        '*': lambda x,y: x*y,
        'min': lambda x,y: min(x,y),
        'max': lambda x,y: max(x,y),
        '**': lambda x,y: x**y
    }
    axis_group = {}
    dic_lable = {}
    data_axis = []
    data_all = {}
    axis_type = axis_data[axis[0]].get('type',False)
    for field in axis[1:]:
        data_all = {}
        for d in datas:
            group_eval = ','.join(map(lambda x: d[x], axis_group_field.keys()))
            axis_group[group_eval] = 1

            data_all.setdefault(d[axis[0]], {})
            dic_lable[d[axis[0]]] = 1

            if group_eval in  data_all[d[axis[0]]]:
                oper = operators[axis_data[field].get('operator', '+')]
                data_all[d[axis[0]]][group_eval] = oper(data_all[d[axis[0]]][group_eval], d[field])
            else:
                data_all[d[axis[0]]][group_eval] = d[field]
        data_axis.append(data_all)

    axis_group = axis_group.keys()
    axis_group.sort()
    axis_lable = dic_lable.keys()
    axis_lable.sort()

    tmp = {}
    except_tmp = []
    if axis_type == 'datetime':
        for lable in axis_lable:
            try:
                tmp[lable] = datetime.strptime(lable, user_locale_format.get_datetime_format(True))
            except:
                except_tmp += [lable]
        axis_lable = sorted(tmp, key=tmp.__getitem__) + except_tmp

    if axis_type == 'date':
        for lable in axis_lable:
            try:
                tmp[lable] = datetime.strptime(lable, user_locale_format.get_date_format())
            except:
                except_tmp += [lable]
        axis_lable = sorted(tmp, key=tmp.__getitem__) + except_tmp

    if not datas:
        return False
    font_property = FontProperties(size=8)
    if type == 'pie':
        labels = tuple(data_all.keys())
        value = tuple(map(lambda x: reduce(lambda x,y=0: x+y, data_all[x].values(), 0), labels))
        explode = map(lambda x: (x%4==2) and 0.06 or 0.0,range(len(value)))
        colors = choice_colors(len(value))
        aa = subplot.pie(value, autopct='%1.1f%%', shadow=True, explode=explode, colors=colors)
        labels = map(lambda x: x.split('/')[-1], labels)
        subplot.legend(aa[0], labels, shadow = True, loc = 'best', prop = font_property)

    elif type == 'bar':
        n = len(axis)-1
        gvalue = []
        gvalue2 = []
        if float(n):
            width =  0.9 / (float(n))
        else:
            width = 0.9
        ind = map(lambda x: x+width*n/2, xrange(len(axis_lable)))
        if orientation=='horizontal':
            subplot.set_yticks(ind)
            subplot.set_yticklabels(tuple(axis_lable), visible=True, ha='right', size=8)
            subplot.xaxis.grid(True,'major',linestyle='-',color='gray')
        else:
            subplot.set_xticks(ind)
            subplot.set_xticklabels(tuple(axis_lable), visible=True, ha='right', size=8, rotation='vertical')
            subplot.yaxis.grid(True,'major',linestyle='-',color='gray')

        colors = choice_colors(max(n,len(axis_group)))
        for i in range(n):
            datas = data_axis[i]
            ind = map(lambda x: x+width*i*overlap+((1.0-overlap)*n*width)/4, xrange(len(axis_lable)))
            #ind = map(lambda x: x, xrange(len(keys)))
            yoff = map(lambda x:0.0, axis_lable)
            
            for y in range(len(axis_group)):
                value = [ datas[x].get(axis_group[y],0.0) for x in axis_lable]
                if len(axis_group)>1:
                    color = colors[y]
                else:
                    color = colors[i]
                if orientation=='horizontal':
                    aa = subplot.barh(ind, tuple(value), width, left=yoff, color=color, edgecolor="#333333")[0]
                    subplot.set_ylim(0, len(ind))
                else:
                    aa = subplot.bar(ind, tuple(value), width, bottom=yoff, color=color, edgecolor="#333333")[0]
                    subplot.set_xlim(0, len(ind))
                gvalue2.append(aa)
                for j in range(len(yoff)):
                    yoff[j]+=value[j]
            gvalue.append(aa)
        if True:
            if len(axis_group)>1:
                axis_group = map(lambda x: x.split('/')[-1], axis_group)
                gvalue2 = map(lambda x:gvalue2[x], range(len(axis_group)))
                subplot.legend(gvalue2,axis_group,shadow=True,loc='best',prop = font_property)
            else:
                t1 = [ axis_data[x]['string'] for x in axis[1:]]
                subplot.legend(gvalue,t1,shadow=True,loc='best',prop = font_property)
        else:
            pass
    else:
        raise Exception, 'Graph type '+type+' does not exist !'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

