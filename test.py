#!/usr/bin/env python3

import unittest
from tada import Todo


class TodoTest(unittest.TestCase):
	''' tests for Todo class '''

	# @todo #8 Remove extra space from hashed todo message
	def testPersistantHashValue(self):
		todo1 = Todo(
			'test.py',
			[(10, '... @todo first', True), (11, '... next', False)]
		)
		todo2 = Todo(
			'test2.py',
			[(15, '... @todo first  next', True)]
		)
		self.assertEqual(todo1.hash(), todo2.hash())

	def testOriginalTextBlock(self):
		todo = Todo(
			'test.py',
			[(10, '# @todo first', True), (11, '# next', False)]
		)
		self.assertListEqual(
			todo.lines(),
			[ '# @todo first', '# next' ]
		)


if __name__ == '__main__':
	unittest.main()
