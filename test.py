#!/usr/bin/env python3
'''
Tada unittest module
'''

import unittest
from tada import Todo


class TodoTest(unittest.TestCase):
	''' tests for Todo class '''

	# @todo #8 Remove extra space from hashed todo message
	def test_persistant_hash_value(self):
		''' Hash value should be equals, if todo words is persistent '''
		todo1 = Todo(
			'test.py',
			[(10, '... @todo first', True), (11, '... next', False)]
		)
		todo2 = Todo(
			'test2.py',
			[(15, '... @todo first  next', True)]
		)
		self.assertEqual(todo1.hash(), todo2.hash())

	def test_original_text_block(self):
		''' todo should return origin lines, for paste into new issue '''
		todo = Todo(
			'test.py',
			[(10, '# @todo first', True), (11, '# next', False)]
		)
		self.assertListEqual(
			todo.lines(),
			['# @todo first', '# next']
		)


if __name__ == '__main__':
	unittest.main()
