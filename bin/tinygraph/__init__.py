import matplotlib
matplotlib.use('GTKCairo')

from pylab import arange

def tinygraph(subplot, type='pie', axis={}, axis_data={}, datas=[]):

	subplot.clear()

	operators = {
		'+': lambda x,y: x+y,
		'*': lambda x,y: x*y,
		'min': lambda x,y: min(x,y),
		'max': lambda x,y: max(x,y),
		'**': lambda x,y: x**y
	}
	for field in axis_data:
		group = axis_data[field].get('group', False)
		if group:
			keys = {}
			for d in datas:
				if d[field] in keys:
					for a in axis:
						if a<>field:
							oper = operators[axis_data[a].get('operator', '+')]
							keys[d[field]][a] = oper(keys[d[field]][a], d[a])
				else:
					keys[d[field]] = d
			datas = keys.values()

	data = []
	for d in datas:
		res = []
		for x in axis:
			res.append(d[x])
		data.append(res)

	if not data:
		return False

	if type == 'pie':
		value = tuple([x[1] for x in data])
		labels = tuple([x[0] for x in data])
		subplot.pie(value, labels=labels, autopct='%1.1f%%')
	elif type == 'bar':
		ind = arange(len(data))
		n = float(len(data[0])-1)
		for i in range(n):
			value = tuple([x[1+i] for x in data])
			labels = tuple([x[0] for x in data])
			subplot.set_xticks(ind)
			subplot.set_xticklabels(labels, visible=True, ha='left', rotation='vertical', va='bottom')
			subplot.bar(ind+i/n, value, 1/n)
	else:
		raise 'Graph type '+type+' does not exist !'
