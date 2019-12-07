#!/usr/bin/env python3

import itertools
import hashlib
import os
import re
import sys
from github import Github

class Todo:
	def __init__(self, file, nl):
		# @todo Init todo with args
		#  and test for multiline comment
		self.file = file
		pfx, self.brief = self.firstline(nl[0][1])
		self.todo = self.lastlines((l for _, l, _ in nl[1:]), pfx)
		self.begin = nl[0][0]
		self.end = self.begin + len(self.todo)

	def firstline(self, l):
		tm = re.match(r'^(.*)\s+@todo\s+(.*)$', l)
		return tm.group(1), tm.group(2)

	def lastlines(self, ls, pfx):
		return [l[len(pfx):] for l in itertools.takewhile(lambda l: l.startswith(pfx), ls)]

	def __str__(self):
		return '\n'.join((
			"%s[%u:%u]" % (self.file, self.begin, self.end),
			self.brief,
			*self.todo
		))

	def hash(self):
		return hashlib.sha1(' '.join((self.brief, *self.todo)).encode('utf8')).hexdigest()


def readTodo(file):
	with open(file, 'r', encoding='utf8') as f:
		content = f.read().split('\n')
		nlt = [(n, l, re.search(r'\s+@todo\s+', l)) for n, l in enumerate(content)]
		for n in (n for n, _, t in nlt if t):
			tnl = itertools.takewhile(lambda nlti: nlti[0] == n or not nlti[2], nlt[n:])
			yield Todo(file, list(tnl))


todos = []

for p in sys.argv[1:]:
	for root, dir, files in os.walk(p, topdown=True):
		if '.git' in dir:
			dir.remove('.git')
		for f in files:
			todos.extend(readTodo(os.path.join(root, f)))

if 'GITHUB_TOKEN' not in os.environ:
	raise RuntimeError("No token")

gh = Github(os.environ['GITHUB_TOKEN'])
repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])

def ipair(repo):
	for i in repo.get_issues(state='open'):
		m = re.search(r'todo-hash:\s+([\da-fA-F]+)', i.body)
		if m:
			yield m.group(1), m

imap = dict(ipair(repo))
tmap = dict((t.hash(), t) for t in todos)

for h, i in imap.items():
	if h not in tmap:
		printf("Close issue #%d, marker %s removed from code" % (i.number, h))
		i.create_comment('Marker removed from code, issue is closed now.')
		i.edit(state='closed')

for h, t in tmap:
	if h not in imap:
		printf("Create issue, marker %s discovered in code" % h)
		# @todo Paste marked fragment of code as verbatim block
		body = '\n'.join((
			'',
			*t.todo,
			'',
			'This issue created automatically.',
			'It will be closed after remove @todo lines from code.',
			'',
			'todo-hash: %s' % h
		))
		repo.create_issue(t.brief, body, labels=['todo'])
