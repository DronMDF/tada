#!/usr/bin/env python3
# coding: utf-8

"""Tada unittest module."""

import unittest
from tada import Todo, Todos, File


class TodoTest(unittest.TestCase):
	"""tests for Todo class."""

	# @todo #8 Remove extra space from hashed todo message
	def test_persistant_hash_value(self):
		"""Hash value should be equals, if todo words is persistent."""
		todo1 = Todo(
			'test.py',
			[(10, '... @tada first', True), (11, '... next', False)],
			marker='@tada'
		)
		todo2 = Todo(
			'test2.py',
			[(15, '... @tada first next', True)],
			marker='@tada'
		)
		self.assertEqual(todo1.hash(), todo2.hash())

	def test_original_text_block(self):
		"""Todo should return origin lines, for paste into new issue."""
		todo = Todo(
			'test.py',
			[(10, '# @tada first', True), (11, '# next', False)],
			marker='@tada'
		)
		self.assertListEqual(
			todo.lines(),
			['# @tada first', '# next']
		)

	def test_original_text_block_with_strange_prefix(self):
		"""Todo should return origin lines, with prefix and spaces."""
		todo = Todo(
			'test.py',
			[(10, '%%%%% @tada  first', True), (11, '%%%%%  next', False)],
			marker='@tada'
		)
		self.assertListEqual(
			todo.lines(),
			['%%%%% @tada  first', '%%%%%  next']
		)

	def test_todo_from_begin_line_hash(self):
		"""Check oneline plaintext todo hashing."""
		self.assertEqual(
			Todo('test', [(1, '@tada woho', True)], marker='@tada').hash(),
			'2994f58e05ad62949210dabd2c585d8dc60a9435'
		)


class TestRepo():
	"""Test github repository."""

	def __init__(self):
		"""Constructor."""
		self.issues = []
		self.title = None
		self.body = None
		self.labels = None

	def get_issues(self, state):
		"""Get issues list."""
		return [issue for issue in self.issues if issue.state == state]

	def create_issue(self, title, body, labels):
		"""Create issue."""
		self.title = title
		self.body = body
		self.labels = labels


class TodosTest(unittest.TestCase):
	"""Test for todo list."""

	def test_create_new(self):
		"""New todo should be translated into issue."""
		todo = Todo(
			'test.py',
			[(1, '... @tada first', True), (3, '... next', False)],
			marker='@tada'
		)
		todos = Todos([todo])
		repo = TestRepo()
		todos.create_new({}, repo)
		self.assertIn(
			'\n'.join((
				'```',
				'... @tada first',
				'... next',
				'```'
			)),
			repo.body
		)

	def test_add_reference_to_text(self):
		"""Issue text should contain references."""
		todo = Todo('test.py', [(1, '@tada #15 References', True)], marker='@tada')
		todos = Todos([todo])
		repo = TestRepo()
		todos.create_new({}, repo)
		self.assertIn('Related issue: #15', repo.body)


class FileTest(unittest.TestCase):
	"""File parser test."""

	def test_from_line_begin(self):
		"""Marker at the begin of line."""
		self.assertEqual(
			len(list(File(['@tada from begin of line'], marker='@tada').todos())),
			1
		)


if __name__ == '__main__':
	unittest.main()
