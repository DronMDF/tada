#!/usr/bin/env python3
'''
TODO control action module
'''

import itertools
import hashlib
import os
import re
import sys
from github import Github


class Todo:
	'''
	TODO class
	'''

	def __init__(self, file, nl):
		''' Constructor '''
		# @todo Init todo with args
		#  and test for multiline comment
		self.file = file
		pfx, self.brief = self.firstline(nl[0][1])
		self.todo = self.lastlines((l for _, l, _ in nl[1:]), pfx)
		self.begin = nl[0][0]
		self.end = self.begin + len(self.todo)

	@staticmethod
	def firstline(line):
		''' Method detect first line format '''
		match = re.match(r'^(.*)\s+@todo\s+(.*)$', line)
		return match.group(1), match.group(2)

	@staticmethod
	def lastlines(lines, prefix):
		''' Method fetch continuation lines of todo '''
		return [
			l[len(prefix):]
			for l in itertools.takewhile(lambda l: l.startswith(prefix), lines)
		]

	def __str__(self):
		''' String todo representation '''
		return '\n'.join((
			"%s[%u:%u]" % (self.file, self.begin, self.end),
			self.brief,
			*self.todo
		))

	def hash(self):
		''' todo hash value '''
		return hashlib.sha1(
			' '.join((self.brief, *self.todo)).encode('utf8')
		).hexdigest()


def read_todo(file):
	''' Read todo's from file '''
	with open(file, 'r', encoding='utf8') as fio:
		content = fio.read().split('\n')
		nlt = [(n, l, re.search(r'\s+@todo\s+', l)) for n, l in enumerate(content)]
		for lineno in (n for n, _, t in nlt if t):
			tnl = itertools.takewhile(
				lambda nlti, ln=lineno: nlti[0] == ln or not nlti[2],
				nlt[lineno:]
			)
			yield Todo(file, list(tnl))


def ipair(repo):
	''' Create key/value list of issues. Key is a todo hash '''
	for issue in repo.get_issues(state='open'):
		match = re.search(r'todo-hash:\s+([\da-fA-F]+)', issue.body)
		if match:
			yield match.group(1), issue


def main(*argv):
	todos = []

	for path in argv:
		for root, dirs, files in os.walk(path, topdown=True):
			if '.git' in dirs:
				dirs.remove('.git')
			for f in files:
				todos.extend(read_todo(os.path.join(root, f)))

	if 'GITHUB_TOKEN' not in os.environ:
		raise RuntimeError("No token")

	gh = Github(os.environ['GITHUB_TOKEN'])
	repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])

	imap = dict(ipair(repo))
	tmap = dict((t.hash(), t) for t in todos)

	# @todo #17 Test logic with creation/removing issue
	#  Under style work this is degraded
	for todoid, issue in imap.items():
		if todoid not in tmap:
			print("Close issue #%d, marker %s removed from code" % (
				issue.number,
				todoid
			))
			issue.create_comment('Marker removed from code, issue is closed now.')
			issue.edit(state='closed')

	for todoid, todo in tmap.items():
		if todoid not in imap:
			print("Create issue, marker %s discovered in code" % todoid)
			# @todo Paste marked fragment of code as verbatim block
			body = '\n'.join((
				'',
				*todo.todo,
				'',
				'This issue created automatically.',
				'It will be closed after remove marker from code.',
				'',
				'todo-hash: %s' % todoid
			))
			repo.create_issue(todo.brief, body, labels=['todo'])


if __name__ == "__main__":
	main(sys.argv[1:])
