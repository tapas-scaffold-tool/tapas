# Quick start

Tapas is a simple scaffold tool to create project template.
You can set up your template to interactively ask user what to do.

Also tapas are spanish appetizer, tapa for single. 
That's why I sometimes call project template tapa.  
  

## Installation

To install tapas use pip:

```
pip install tapas
```


## Simple usage

Call tapas with tapa name in target directory and enter requested parameters in command line.

```
tapas {tapa-name}
```

Tapas use tapas-index, stored in [GitHub repository](https://github.com/tapas-scaffold-tool/tapas-index)
to define tapa source by tapa name.

To show list of available tapas pass `--list` flag to tapas:

```shell script
tapas --list
```


## Generate project in another directory

If you want to generate project in specific directory pass this directory as second argument:

```
tapas {template-name} {target-directory}
```

If target directory does not exist it will be created.


## Rewrite files on generation

You can pass flag `--force` (or `-f`) to make tapas rewrite existing files.
It can be useful when incorrect data was entered.


## Use tapa that is not in index

You can use tapa that is not registered in tapas-index.
For that you should pass first argument in following format:

`tapas {tapa-source-type}:{tapa-source-location}`

Where `tapa-source-type` is one of:

- `index` - default value, look tapa name in index
- `directory` or `dir` - look for tapa in directory `tapa-source-location` on local machine, usefull for testing
- `github` or `gh` - look for tapa in `tapa-source-location` repository on github 


## Use custom index

You can use custom index file.
To use custom index you should pass index location to `--index` parameter in following format:

`tapas --index {index-source-type}:{index-source-location} {tapa-name}`

Where `index-source-type` is one of:

- `directory` or `dir` - look for `index.yml` file in in directory `index-source-location` on local machine
- `github` or `gh` - look for `index.yml` in `index-source-location` repository on github


## Show version

To show version pass `--version` argument.
