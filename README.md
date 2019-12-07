# Tada is a todo action

This action create issue on each marked comment in code.
And close issue, id marker removed from code.

## Inputs

## Outputs

## Example

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
      - uses: actions/tada@v0
```

### Check TODOS for pull requests

@todo Describe branch and pr scenarios
