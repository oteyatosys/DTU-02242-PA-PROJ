# DTU-02242-PA-PROJ

## Directory structure:
- java-example: Contains a sample java program and test suite
- run.sh: Script to compile java-example and decompile output file
- data: Temporary dir for a single run
    - classes: Contains class files of java-example
    - bytecode: Contains the bytecode of the class files (jvm2json files)

# Requirements
- maven
- java 23

# Running

Run the script `run.sh` to build the java-example and decompile files.
The output can be found in data/bytecode
