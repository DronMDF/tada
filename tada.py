#!/usr/bin/env python3

import os
import re
import sys
from github import Github

# @todo Check all todos in repository issues
# @todo Create new issues
# @todo Remove closed issues

def readTodo(f):
	with open(f, 'r', encoding='utf8') as f:
		content = f.read()
	return [l for l in content.split('\n') if re.search('\s+@todo\s+', l)]


todos = []

for p in sys.argv[1:]:
	for root, dir, files in os.walk(p, topdown=True):
		if '.git' in dir:
			dir.remove('.git')
		for f in files:
			todos.extend(readTodo(os.path.join(root, f)))

for t in todos:
	print(t)

if 'GITHUB_TOKEN' not in os.environ:
	raise RuntimeError("No token")

gh = Github(os.environ['GITHUB_TOKEN'])
repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
for i in repo.get_issues(state='open'):
	print(i)
