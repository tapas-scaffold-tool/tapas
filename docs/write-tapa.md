# How to write your own tapa

A good way to start creating your tapa is to generate template with special tapa:

```
tapas tapa
```

Link to repository [is here](https://github.com/tapas-scaffold-tool/tapa-tapa).


## Tapa structure

Tapa consists of following parts:

- `template` directory
- `tapa.py` file

## Jinja

Tapas uses [jinja2 template engine](http://jinja.pocoo.org/).
Almost everything in template directory can be template.
You can substitute values into directory names, file names and file content.

## tapa.py structure

Tapas reads two functions from `tapa.py` file:

- `get_params`
- `post_init`

Both functions and even `tapa.py` file are optional.

## Project generation lifecycle

Project generation lifecycle consists of 5 steps:

1. Read `tapa.py` file.
2. Collect project params from `get_params` function if present.
3. Ask for params from user to build environment or load them from `--param` argument.
4. Generate files with `template` directory.
5. Call `post_init` function if present.
6. Call tapas system actions (e.g. generating license, init git repository etc.).

## get_params function

`get_params` function must return list of parameter descriptions. 

Setup example:


```python
from tapas.params import StrParameter


def get_params():
    return [
        StrParameter("directory_name"),
        StrParameter("file_name"),
        StrParameter("value_in_file"),
    ]
``` 
 
Output example:
 
```sh
su0@tower:~$ tapas test-tapa
Enter directory_name value: abc
Enter file_name value: def
Enter value_in_file value: jkl
```


### Redefine prompt string

You can define your own prompt string with `prompt` parameter:

```python
from tapas.params import StrParameter


def get_params():
    return [
        StrParameter("param.id", prompt="Please enter parameter value"),
    ]
```

Output example:

```sh
su0@tower:~$ tapas test-tapa
Please enter parameter value: jkl
```


### Default value

You can set default value with `default_value` parameter:

```python
from tapas.tools import prompt


def ask():
    prompt('directory_name', prompt_string='What is directory name?', default_value='some-default-value')
    prompt('file_name', default_value='default-file-name')
    prompt('value_in_file')
```

Output example:

```sh
su0@tower:~$ tapas test-tapa
What is directory name? dir-name
Enter file_name value [default-file-name]: 
Enter value_in_file value: jkl
```

Default value will be used in case of empty user input.


## Tapas system params

Tapas has some special parameters to pass into returning environment.
Those parameters can configure prompt and actions for many common cases like license file generation or git repo init.

### Adding license file

Tapas uses uses [lice](https://github.com/licenses/lice) to generate license file.
To add license generation prompt add `TAPAS_SYSTEM_LICENSE_PARAMETER` to `get_params` function:

```python
from tapas.tools.license import TAPAS_SYSTEM_LICENSE_PARAMETER


def get_params():
    return [
        TAPAS_SYSTEM_LICENSE_PARAMETER,
    ]
```

### Init git repository

Tapas can init git repository.
To add init git repo prompt add `TAPAS_SYSTEM_INIT_GIT_PARAMETER` to `get_params` function: 

```python
from tapas.tools.git import TAPAS_SYSTEM_INIT_GIT_PARAMETER


def get_params():
    return [
        TAPAS_SYSTEM_INIT_GIT_PARAMETER,
    ]
```

## post_init function

`post_init` function (if present) will be called after project generation but before tapas system calls.
There is no any restriction on what can be in this function.

Possible use cases:

- Fine tuning of generated files (e.g. chmod)

## Publishing your tapa

The best place to publish your tapa is github.
Simply create repository and publish all tapa files in it.


## Adding your tapa to tapas-index

To provide possibility to use your tapa via its name you should add record to 
[index.yml](https://github.com/tapas-scaffold-tool/tapas-index/blob/master/index.yml) file
in [tapas-index repository](https://github.com/tapas-scaffold-tool/tapas-index).

Please check requirements in [contributing section](https://github.com/tapas-scaffold-tool/tapas-index/blob/master/contributing.md).
