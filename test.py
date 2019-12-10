#!/usr/bin/env python3
'''
Tada unittest module
'''

import unittest
from tada import Todo, Todos


class TodoTest(unittest.TestCase):
	''' tests for Todo class '''

	# @todo #8 Remove extra space from hashed todo message
	def test_persistant_hash_value(self):
		''' Hash value should be equals, if todo words is persistent '''
		todo1 = Todo(
			'test.py',
			[(10, '... @tada first', True), (11, '... next', False)],
			marker='@tada'
		)
		todo2 = Todo(
			'test2.py',
			[(15, '... @tada first  next', True)],
			marker='@tada'
		)
		self.assertEqual(todo1.hash(), todo2.hash())

	def test_original_text_block(self):
		''' todo should return origin lines, for paste into new issue '''
		todo = Todo(
			'test.py',
			[(10, '# @tada first', True), (11, '# next', False)],
			marker='@tada'
		)
		self.assertListEqual(
			todo.lines(),
			['# @tada first', '# next']
		)


class TestRepo():
	''' Test github repository '''
	def __init__(self):
		self.issues = []
		self.title = None
		self.body = None
		self.labels = None

	def get_issues(self, state):
		''' Get issues list '''
		return [i for i in self.issues if i.state == state]

	def create_issue(self, title, body, labels):
		''' Create issue '''
		self.title = title
		self.body = body
		self.labels = labels


class TodosTest(unittest.TestCase):
	''' Test for todo list '''
	def test_create_new(self):
		''' New todo should be translated into issue '''
		todo = Todo(
			'test.py',
			[(1, '... @tada first', True), (3, '... next', False)],
			marker='@tada'
		)
		todos = Todos([todo])
		repo = TestRepo()
		todos.create_new(dict(), repo)
		self.assertIn(
			'\n'.join((
				'```',
				'# @tada first',
				'# next',
				'```'
			)),
			repo.body
		)


if __name__ == '__main__':
	unittest.main()
