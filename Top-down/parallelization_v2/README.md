# STATUS

- Code has been tested and is working on Linux and Windows (create dedicated enviroment). Not tested on Mac.
- This version has some small changes with respect to the previous one:
-   i) Cores is now automatic, using all available cores for the first zonal_stats and then using 1 core per RP analysis (in case there are more RPs then available cores, it will use all cores and serialize the analysis accordingly).
-   ii) Split the RPs computation into Exposure/Impact and EAE/EAI computation, the later becoming a stand-alone function
-   iii) Computes now the EAE/EAI using 3 different formulation, a) Lower Bound LB; b) Upper Bound UB, and; c) Mean of the two
-   iv) Removed the RP_EAI columns for better presentation of the results

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
