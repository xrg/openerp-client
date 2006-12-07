try:
	set()
except NameError:
	from sets import Set as set


class ObservatorRegistry(object):
	def __new__(cls):
		if not hasattr(cls, '_inst'):
			cls._inst = object.__new__(cls)
		return cls._inst

	def __init__(self):
		self._observables = {}
		self._receivers = {}

	def add_observable(self, oid, obj):
		self._observables[oid] = obj

	def add_receiver(self, signal, callable):
		if signal not in self._receivers:
			self._receivers[signal] = []
		self._receivers[signal].append(callable)
	
	def remove_receiver(self, signal, callable):
		self._receivers[signal].remove(callable)

	def warn(self, *args):
		for receiver in self._receivers.get(args[0], []):
			receiver(*args[1:])

oregistry = ObservatorRegistry()


class Observable(object):
	def __init__(self):
		oregistry.add_observable(id(self), self)

	def warn(self, *args):
		oregistry.warn(args[0], self, *args[1:])
