# Mypy development releases

Development releases for [mypy](https://github.com/python/mypy). Use at your own risk!

### Using mypy-dev with pre-commit:

Add this to your `.pre-commit-config.yaml`

```yaml
- repo: https://github.com/cdce8p/mypy-dev-pre-commit
  rev: ''  # Use the sha / tag you want to point at
  hooks:
    - id: mypy
```
