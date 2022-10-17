# STATUS

- Code has been tested and is working on Linux and Windows (create dedicated enviroment). Not tested on Mac.


# Development Setup
We strongly recommend using the mamba package manager.

## USING MAMBA

Environment creation:

```bash
$ mamba create -n ccdr-tools --file Top-down/notebooks/win_env.yml
```

Updating the environment spec (e.g., if package version changed or a package is added/removed):

```bash
$ mamba list -n ccdr-tools --explicit > win_env.yml
```

Updating the environment (e.g., after code updates)

```bash
$ mamba update -n ccdr-tools --file Top-down/notebooks/win_env.yml
```

## USING CONDA

Environment creation:

```bash
$ conda create -name ccdr-tools --file Top-down/notebooks/win_env.yml
```

Updating the environment (e.g., after code updates)

```bash
$ conda update -name ccdr-tools --file Top-down/notebooks/win_env.yml
```
