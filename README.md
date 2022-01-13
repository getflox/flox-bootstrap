# flox bootstrap engine

Create your projects in seconds with [flox](https://github.com/getflox/flox) using shared templates. 

## Installation

```bash
$ flox plugin install flox-bootstrap
```

or

```bash
$ pip install flox-bootstrap
```

## Configuration

You can use this plugin without any configuration, but if you like you can add your own custom repository 
which may contain additional or customised templates. 

```bash
$ flox config --plugin bootstrap --scope=user
```


## Bootstrap project using templates

```bash
$ flox bootstrap python                                                                                                                                                                                                                                                                            12:14:05
 → Create library project [y/N]: n
 → Python Version [3.8.12]:
 
$ ls -la .
drwxr-xr-x   4 me  staff  128 Jan 13 11:54 .flox
drwxr-xr-x  13 me  staff  416 Jan 13 12:14 .git
-rw-r--r--   1 me  staff    6 Jan 13 12:14 .python-version
-rw-r--r--   1 me  staff   14 Jan 13 11:54 README.md
drwxr-xr-x   3 me  staff   96 Jan 13 11:54 flox_project
-rw-r--r--   1 me  staff  454 Jan 13 12:14 pyproject.toml
```

flox templates may contain extra parameters which can be changed during bootstrap proces. 


## Template repository structure

You can create your own repository or fork default one https://github.com/getflox/flox-templates
Your template repository should be structured like that:

```
.
├── github-actions
│         ├── hooks.py
│         └── template
├── python
│         ├── template
│         │         ├── <project_name_underscore>
│         │         │         └── __init__.py
│         │         └── pyproject.toml.j2
│         └── variables.py
└── serverless-python
    ├── template
    │         ├── package.json.j2
    │         └── serverless.yml.py.j2
    └── variables.py
```

Where:

- first level directory is a name of the template which can be passed as parameter to bootstrap command
- `variables.py` is a simple python script containing one variable called `VARIABLES` which should be a list of `ParamDefinition` objects defining parameters
- `hooks.py`  a simple script which may contain two functions `pre_install` and `post_install` which will be executed before and after bootstrap template is added to your project. 
 additionally `pre_install` function will get all variables and all features installed for given project with the ability to filter template files which should be installed
