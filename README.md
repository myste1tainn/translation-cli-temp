# Setting up

NOTE: If you found problems, go to [How to reset](#how-to-reset)

1. Make sure you run the right version, only once is needed

```bash
poetry env use python3.11
```

2. Install all the dependecies

```bash
poetry install --with dev
```

3. If you have the need to add new dependecies, modify the pyproject.toml as needed then

```bash
poetry lock ; poetry install --with dev
```

# How to run

```bash
poetry run fst "{command}" "{input_file_for_the_command}"
```

# How to reset

Sometimes there might be problems with current caches from poetry, to reset runs the followings:

```bash
poetry env remove python
rm poetry.lock
find . -type d -name '__pycache__' -exec rm -r {} +
find . -type d -name '.pytest_cache' -exec rm -r {} +
find . -type d -name '.mypy_cache' -exec rm -r {} +
```
