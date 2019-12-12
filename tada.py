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
		self.todo = list(itertools.takewhile(
			lambda line: line.startswith(self.prefix),
			(line[1] for line in nl)
		))
		self.begin = nl[0][0]
		self.end = self.begin + len(self.todo)

	@staticmethod
	def get_prefix(line, marker):
		"""Method determine todo prefix."""
		match = re.match(r'^(.*)\s+%s' % marker, line)
		return match.group(1)

	def brief(self):
		"""Method return issue title."""
		return re.sub(r'%s\s+%s\s+' % (self.prefix, self.marker), '', self.todo[0])

	def lines(self):
		"""Method return original todo lines."""
		return self.todo

	def hash(self):
		"""Todo hash value."""
		return hashlib.sha1(
			' '.join((
				re.sub(r'%s\s+%s\s+' % (self.prefix, self.marker), '', self.todo[0]),
				*(re.sub(r'%s\s+' % self.prefix, '', tline) for tline in self.todo[1:])
			)).encode('utf8')
		).hexdigest()


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
					'',
					'```',
					*todo.lines(),
					'```',
					'',
					'This issue created automatically.',
					'It will be closed after remove marker from code.',
					'',
					'todo-hash: %s' % todoid
				))
				repo.create_issue(todo.brief(), body, labels=['todo'])

	def has(self, todoid):
		"""Check todo id."""
		return todoid in self.tmap


def read_todo(file):
	"""Read todo's from file."""
	with open(file, 'r', encoding='utf8') as fio:
		content = fio.read().split('\n')
		nlt = [
			(lineno, line, re.search(r'\s+@todo\s+', line))
			for lineno, line in enumerate(content)
		]
		for lineno in (ln for ln, _, marked in nlt if marked):
			tnl = itertools.takewhile(
				lambda nlti, ln=lineno: nlti[0] == ln or not nlti[2],
				nlt[lineno:]
			)
			yield Todo(file, list(tnl))


def ipair(repo):
	"""Create key/value list of issues. Key is a todo hash."""
	for issue in repo.get_issues(state='open'):
		match = re.search(r'todo-hash:\s+([\da-fA-F]+)', issue.body)
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
				todos.extend(read_todo(os.path.join(root, file)))

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
