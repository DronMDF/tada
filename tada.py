#!/usr/bin/env python3
# coding: utf-8

"""TODO control action module."""

import itertools
import hashlib
import os
import re
import sys
from github import Github


class Todo:
	"""TODO class."""

	def __init__(self, file, nl, marker='@todo'):
		"""Constructor."""
		self.file = file
		self.marker = marker
		self.prefix = self.get_prefix(nl[0][1], marker)
		if self.prefix:
			self.todo = list(itertools.takewhile(
				lambda line: line.startswith(self.prefix),
				(line[1] for line in nl)
			))
		else:
			# If line start ftom marker - this is a plain text format
			# todo is oneline always
			self.todo = [nl[0][1]]
		self.begin = nl[0][0]
		self.end = self.begin + len(self.todo)

	@staticmethod
	def get_prefix(line, marker):
		"""Method determine todo prefix."""
		match = re.match(r'^(.*)\s*%s' % marker, line)
		return match.group(1)

	def brief(self):
		"""Method return issue title."""
		return re.sub(
			r'^%s\s*%s\s+(#\d+\s+)?' % (self.prefix, self.marker),
			'',
			self.todo[0]
		)

	def lines(self):
		"""Method return original todo lines."""
		return self.todo

	def hash(self):
		"""Todo hash value."""
		return hashlib.sha1(
			' '.join((
				re.sub(r'^%s\s*%s\s+' % (self.prefix, self.marker), '', self.todo[0]),
				*(re.sub(r'^%s\s*' % self.prefix, '', tline) for tline in self.todo[1:])
			)).encode('utf8')
		).hexdigest()

	def related(self):
		"""List of related issue numbers."""
		match = re.search(r'\s+#(\d+)\s+', self.todo[0])
		if match:
			return [int(match.group(1))]
		return []


class Todos:
	"""TODO list class."""

	def __init__(self, todos):
		"""Constructor."""
		self.tmap = {todo.hash(): todo for todo in todos}

	def create_new(self, imap, repo):
		"""Create new issue for all new todo."""
		for todoid, todo in self.tmap.items():
			if todoid not in imap:
				body = '\n'.join((
					'Related issue: %s' % ', '.join(('#%u' % num for num in todo.related())),
					'',
					'```',
					*todo.lines(),
					'```',
					'',
					'This issue created automatically.',
					'It will be closed after remove marker from code.',
					'',
					'todo-id: %s' % todoid
				))
				repo.create_issue(todo.brief(), body, labels=['todo'])

	def has(self, todoid):
		"""Check todo id."""
		return todoid in self.tmap


class File:
	"""File parser."""

	def __init__(self, lines=None, filename=None, marker='@todo'):
		"""Constructor."""
		self.marker = marker
		if filename is not None:
			self.filename = filename
			with open(self.filename, 'r', encoding='utf8') as fio:
				self.lines = fio.read().split('\n')
		else:
			assert isinstance(lines, list), 'Invalid lines'
			self.filename = 'unknown'
			self.lines = lines

	def istodo(self, line):
		"""Check for todo line."""
		return any((
			re.search(r'\s+%s\s+' % self.marker, line),
			re.search(r'^%s\s+' % self.marker, line)
		))

	def todos(self):
		"""List of all todo from file."""
		nlt = [
			(lineno, line, self.istodo(line))
			for lineno, line in enumerate(self.lines)
		]
		for lineno in (ln for ln, _, marked in nlt if marked):
			tnl = itertools.takewhile(
				lambda nlti, ln=lineno: nlti[0] == ln or not nlti[2],
				nlt[lineno:]
			)
			yield Todo(self.filename, list(tnl), marker=self.marker)


def ipair(repo):
	"""Create key/value list of issues. Key is a todo hash."""
	for issue in repo.get_issues(state='open'):
		match = re.search(r'todo-id:\s+([\da-fA-F]+)', issue.body)
		if match:
			yield match.group(1), issue


def main(*argv):
	"""Main method."""
	todos = []

	for path in argv:
		for root, dirs, files in os.walk(path, topdown=True):
			if '.git' in dirs:
				dirs.remove('.git')
			for file in files:
				todos.extend(File(filename=os.path.join(root, file)).todos())

	if 'GITHUB_TOKEN' not in os.environ:
		raise RuntimeError('No token')

	github = Github(os.environ['GITHUB_TOKEN'])
	repo = github.get_repo(os.environ['GITHUB_REPOSITORY'])

	imap = dict(ipair(repo))
	tmap = Todos(todos)

	# @todo #17 Test logic with creation/removing issue
	#  Under style work this is degraded
	for todoid, issue in imap.items():
		if not tmap.has(todoid):
			print('Close issue #%d, marker %s removed from code' % (
				issue.number,
				todoid
			))
			issue.create_comment('Marker removed from code, issue is closed now.')
			issue.edit(state='closed')

	tmap.create_new(imap, repo)


if __name__ == '__main__':
	main(*sys.argv[1:])
