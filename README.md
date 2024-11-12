# DTU-02242-PA-PROJ

## Directory structure:
- data:
    - old: 
        - source: Contains the java source code
        - classes: Contains class files of java-example
        - bytecode: Contains the bytecode of the class files (jvm2json files)
    - new: When analysing changes, we copy files to this directory
        - source 
        - classes 
        - bytecode
- java-example: Contains a sample java program and test suite
- jvm2json: Git submodule containing the source code for jvm2json
- scripts: Python main files
- src: Python modules
- run.sh: Script to compile java-example and decompile output file

# Requirements
- maven
- java 23

# Running

To generate files needed for analysis, run `pdm run prepare`.
Once files are generated you can call the command `pdm run analyse`.
