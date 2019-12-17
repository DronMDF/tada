# Tada is a todo management system

Special marked code blocks turn into project issues.
Issue are closed automatically if the marked code block is removed.

This project inspired by [0pdd](http://www.0pdd.com).

## Syntax

Any form of comments is accepted.
First line should be marked with **@todo**.
Subsequent lines must have the same prefix as the marked line.

```
// @tada [#id] Title
// Detailed descriptions
```

The marker can be located at the beginning of the line, but in this case the text can only be single-line.

```
@tada Signle line plain text todo
```

Use **@todo** instead **@tada** in you repository, I cannot do this without consequences.

## Configurations

### Manage issues on master branch

```yml
on:
  push:
    branches:
      - master

jobs:
  todo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v1
      - uses: DronMDF/tada@v0
```

### Check TODOS for pull requests

@todo Describe branch and pr scenarios
