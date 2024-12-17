# `pants`

## Setup

When the current version of `pants` starts failing, we may need to download a
new `pants` launch script. Please see this:

<https://www.pantsbuild.org/docs/installation>

## flake8 task

It has been developed in-house. When you upgrade `pants`, you may need to update
this file too:

```none
build_support/pants/pants-plugins/flake8_task/flake8_task.py
```

## Useful commands

- `./pants goals`

  Lists all goals

- `./pants help`

  Prints generic help

- `./pants clean-all`

  Deletes all build products, creating a clean workspace.

## Additional information

A pretty good starting resource to enable additional debugging information,
improve caching, or track down any dependency issues is the pants
troubleshooting page:

<https://www.pantsbuild.org/docs/troubleshooting>

## Pants caching

Pants has the ability to store local intermediates to make builds consistent and
repeatable <https://www.pantsbuild.org/docs/how-does-pants-work#caching>

the `~/.cache` directory can fill up so much that NCBI accounts mounted on
`\\snowman` can fill up. It is recommended that the following are added to your
~/.bash_profile to route caching products to a directory in `/tmp` with a new
`bash` session

```
export XDG_CACHE_HOME=/tmp/${USER}/.cache
export PANTS_SETUP_CACHE=${XDG_CACHE_HOME}/pants/setup

mkdir -p $XDG_CACHE_HOME $PANTS_SETUP_CACHE

export PANTS_NAMED_CACHES_DIR=${XDG_CACHE_HOME}/named_caches
export PANTS_LOCAL_STORE_DIR=${XDG_CACHE_HOME}/local_stores
```
