# How to write your own tapa

A good way to start creating your tapa is to generate template with special tapa:

```
tapas tapa
```

Link to repository [is here](https://github.com/tapas-scaffold-tool/tapa-tapa).


## Tapa structure

Tapa consists of folowing parts:

- `template` directory
- `tapa.py` file


## Jinja

Tapas uses [jinja2 template engine](http://jinja.pocoo.org/).
Almost everything in template directory can be template.
You can substitute values into directory names, file names and file content.


## tapa.py structure

Tapas reads two functions from `tapa.py` file:
- `ask`
- `post_init`

Both functions and even `tapa.py` file are optional.


## ask function

`ask` function will be called after `tapa.py` file loading.
The main goal of this function is to collect variable values to for template engine.
To request value from user call `prompt` from `tapas.tools` module: 
This functions expect user input or input via `--params` json object.
If parameter was set by `params` json object, function will use this value and will not ask user value.

Setup example:

```python
from tapas.tools import prompt


def ask():
    prompt('directory_name')
    prompt('file_name')
    prompt('value_in_file')
``` 
 
Output example:
 
```sh
su0@tower:~$ tapas test-tapa
Enter directory_name value: abc
Enter file_name value: def
Enter value_in_file value: jkl
```


### Redefine prompt string

You can define your own prompt string with `prompt_string` parameter:

```python
from tapas.tools import prompt


def ask():
    prompt('directory_name', prompt_string='What is directory name? ')
    prompt('file_name', prompt_string='What is file name? ')
    prompt('value_in_file', prompt_string='And what file content would you like? ')
```

Output example:

```sh
su0@tower:~$ tapas test-tapa
What is directory name? abc
What is file name? def
And what file content would you like? jkl
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


## post_init function

`post_init` function (if present) will be called after project generation.
There is no any restriction on what can be in this function.

Possible use cases:

- Init git repository
- Fine tuning of generated files (e.g. chmod)


## Adding license file

To ask license file add following calls to your `tapa.py`:

```python
from tapas.tools import prompt_license, generate_license_file


def ask():
    prompt_license()


def post_init(license: str):
    generate_license_file(license)
``` 

It results in next prompt to user:

```
Add license (afl3 | agpl3 | apache | bsd2 | bsd3 | cc0 | cc_by | cc_by_nc | cc_by_nc_nd | cc_by_nc_sa | cc_by_nd | cc_by_sa | cddl | epl | gpl2 | gpl3 | isc | lgpl | mit | mpl | wtfpl | zlib)? [none]:
```

And adds `LICENSE` files.

This functions uses [lice](https://github.com/licenses/lice) to generate files.


## Publishing your tapa

Most common place to publish your tapa is github.
Simply create repository and publish all tapa files in it.


## Adding your tapa to tapas-index

To provide possibility to use your tapa via its name you should add record to 
[index.yml](https://github.com/tapas-scaffold-tool/tapas-index/blob/master/index.yml) file
in [tapas-index repository](https://github.com/tapas-scaffold-tool/tapas-index).

You must use the following format:

```yaml
{desired-tapa-name}:
  repository: github:{login-or-organisation}/{repository-name}
  description: Add here short description of what your tapa do
```
 
Also it is good to add your tapa name and short description into [README.md](https://github.com/tapas-scaffold-tool/tapas-index/blob/master/README.md)
in the same repository.
