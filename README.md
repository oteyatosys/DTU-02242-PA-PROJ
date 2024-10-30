# DTU-02242-PA-PROJ

## Directory structure:
- data: Temporary dir for a single run
    - classes: Contains class files of java-example
    - bytecode: Contains the bytecode of the class files (jvm2json files)
- java-example: Contains a sample java program and test suite
- jvm2json: Git submodule containing the source code for jvm2json
- scripts: Python main files
- src: Python modules
- run.sh: Script to compile java-example and decompile output file

# Requirements
- maven
- java 23

# Running

Run the script `run.sh` to build the java-example and decompile files.
The output can be found in the `data` folder.

Once files are generated you can call the command `pdm run analyse`.
