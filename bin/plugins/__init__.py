import common
import re

import workflow_print

plugins_repository = {
	'workflow_print_simple': {'model':'.*', 'string':'Print Workflow', 'action': workflow_print.wkf_print_simple },
	'workflow_print': {'model':'.*', 'string':'Print Workflow (Complex)', 'action': workflow_print.wkf_print },
}

def execute(datas):
	result = {}
	for p in plugins_repository:
		if not 'model_re' in plugins_repository[p]:
			plugins_repository[p]['model_re'] = re.compile(plugins_repository[p]['model'])
		res = plugins_repository[p]['model_re'].search(datas['model'])
		if res:
			result[plugins_repository[p]['string']] = p
	if not len(result):
		common.message(_('No available plugin for this resource !'))
		return False
	sel = common.selection(_('Choose a Plugin'), result, alwaysask=True)
	if sel:
		plugins_repository[sel[1]]['action'](datas)
	return True

