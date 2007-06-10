import matplotlib
matplotlib.use('GTKCairo')

from pylab import arange
from matplotlib.font_manager import FontProperties

colorline = [ '#%02x%02x%02x' % (25+((r+9)%11)*23,5+(g%11)*20,25+((b+3)%11)*23) for r in range(11) for g in range(11) for b in range(11) ]
def choice_colors(n):
	#base=['#FF0000','#009000','#9400D3','#7CFC00','#FF4500','#00BFFF','#FF1493','#8B0000','#9932CC','#E9967A','#8FBC8F','#483D8B','#2F4F4F','#00CED1','#9400D3','#FF1493','#00BFFF']
	#return base[0:n]
	if n:
		print  colorline[0:-1:len(colorline)/n]

		return colorline[0:-1:len(colorline)/n]
	return []


def tinygraph(subplot, type='pie', axis={}, axis_data={}, datas=[], axis_group_field=[], orientation='horizontal'):
	subplot.clear()
	operators = {
		'+': lambda x,y: x+y,
		'*': lambda x,y: x*y,
		'min': lambda x,y: min(x,y),
		'max': lambda x,y: max(x,y),
		'**': lambda x,y: x**y
	}
	axis_group = {}
	keys = {}
	data_axis = []
	for field in axis[1:]:
		data_all = {}
		#group = axis_data[field].get('group', 'True')
		for d in datas:
			group_eval = ','.join(map(lambda x: d[x], axis_group_field))
			axis_group[group_eval] = 1

			data_all.setdefault(d[axis[0]], {})
			keys[d[axis[0]]] = 1

			if group_eval in  data_all[d[axis[0]]]:
				oper = operators[axis_data[field].get('operator', '+')]
				data_all[d[axis[0]]][group_eval] = oper(data_all[d[axis[0]]][group_eval], d[field])
			else:
				data_all[d[axis[0]]][group_eval] = d[field]
		data_axis.append(data_all)
	axis_group = axis_group.keys()
	axis_group.sort()
	keys = keys.keys()
	keys.sort()

	if not datas:
		return False
	font_property = FontProperties(size=8)
	if type == 'pie':
		labels = tuple(data_all.keys())
		value = tuple(map(lambda x: reduce(lambda x,y=0: x+y, data_all[x].values(), 0), labels))

		#value = tuple([x[1] for x in datas_axis])   # Try if works without adding [0]
		#labels = tuple([x[0] for x in datas])
		import random
		explode = map(lambda x: (x%4==2) and 0.06 or 0.0,range(len(value)))
		subplot.pie(value,autopct='%1.1f%%',shadow=True, explode=explode)
		labels = map(lambda x: x.split('/')[-1], labels)
		subplot.legend(labels,shadow=True)

	elif type == 'bar':
		n = len(axis)-1
		gvalue = []
		gvalue2 = []
		width =  0.9 / float(n)
		ind = map(lambda x: x+width*n/2, arange(len(keys)))
		if orientation=='horizontal':
			subplot.set_yticks(ind)
			subplot.set_yticklabels(tuple(keys), visible=True, ha='right', size=8)
			subplot.xaxis.grid(True,'major',linestyle='-',color='gray')
		else:
			subplot.set_xticks(ind)
			subplot.set_xticklabels(tuple(keys), visible=True, ha='right', size=8, rotation='vertical')
			subplot.yaxis.grid(True,'major',linestyle='-',color='gray')

		colors = choice_colors(max(n,len(axis_group)))
		for i in range(n):
			datas = data_axis[i]
			ind = map(lambda x: x+width*i, arange(len(keys)))
			yoff = map(lambda x:0.0, keys)

			for y in range(len(axis_group)):
				value = [ datas[x].get(axis_group[y],0.0) for x in keys]
				if len(axis_group)>1:
					color = colors[y]
				else:
					color = colors[i]
				if orientation=='horizontal':
					aa = subplot.barh(ind, tuple(value), width, left=yoff, color=color, edgecolor="#999999")[0]
				else:
					aa = subplot.bar(ind, tuple(value), width, bottom=yoff, color=color, edgecolor="#999999")[0]
				gvalue2.append(aa)
				for j in range(len(yoff)):
					yoff[j]+=value[j]
			gvalue.append(aa)

		if True:
			if len(axis_group)>1:
				axis_group = map(lambda x: x.split('/')[-1], axis_group)
				subplot.legend(gvalue2,axis_group,shadow=True,loc='best',prop = font_property)
			else:
				t1 = [ axis_data[x]['string'] for x in axis[1:]]
				subplot.legend(gvalue,t1,shadow=True,loc='best',prop = font_property)
		else:
			pass
			#subplot.set_xticks(ind)
			#subplot.set_xticklabels(labels, visible=True, ha='left', rotation='vertical')
			#subplot.bar(ind, value, 1/n)
#-               ind = arange(len(data))
#-               n = float(len(data[0])-1)
#-               for i in range(n):
#-                       value = tuple([x[1+i] for x in data])
#-                       labels = tuple([x[0] for x in data])
#-                       subplot.set_xticks(ind)
#-                       subplot.set_xticklabels(labels, visible=True, ha='left', rotation='vertical', va='bottom')
#-                       subplot.bar(ind+i/n, value, 1/n)

	else:
		raise 'Graph type '+type+' does not exist !'
