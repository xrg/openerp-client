import service
import common

def wkf_print(datas):
	datas['nested']=True
	obj = service.LocalService('action.main')
	obj.exec_report('workflow.instance.graph', datas)
	return True

def wkf_print_simple(datas):
	datas['nested']=False
	obj = service.LocalService('action.main')
	obj.exec_report('workflow.instance.graph', datas)
	return True
