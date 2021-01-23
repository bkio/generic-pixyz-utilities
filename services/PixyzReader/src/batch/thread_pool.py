from queue import Queue
from .worker import Worker

class ThreadPool:
	"""Pool of threads consuming tasks from a queue"""
	def __init__(self, num_threads):
		self.tasks = Queue(num_threads)
		for _ in range(num_threads): Worker(self.tasks)

	def AddTask(self, func, *args, **kargs):
		"""Add a task to the queue"""
		self.tasks.put((func, args, kargs))

	def WaitCompletion(self):
		"""Wait for completion of all the tasks in the queue"""
		self.tasks.join()