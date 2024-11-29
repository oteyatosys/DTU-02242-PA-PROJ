# Predictive Test Selection with Abstract Interpretation and Syntactic Analysis

## Overview

This project performs static analysis on Java code to reduce the number of unit tests that need to be executed after code changes. By using techniques such as abstract interpretation, the analysis estimates which lines are affected, allowing for more efficient testing.

The repository contains several components, including a Java example application, scripts for various analyses, and the core Python code for the static analysis pipeline. The structure of this project is designed to analyze changes in Java bytecode, optimize test coverage, and generate meaningful reports for developers.

## Folder Structure

- **data/**: A temporary directory used to store Java source code, bytecode, and related files after compilation and conversion. This data is used during the analysis process and can be regenerated as needed.

  - **new/** and **old/**: Contain bytecode, compiled classes, source code, and test classes for both the current and previous versions of the Java project. These files are generated and stored temporarily during the analysis.

- **java-example/**: A simple Java project used as an example.

  - **src/main/java**: Contains the Java source files.
  - **src/test/java**: Contains the Java unit tests.
  - **target/**: Contains the compiled classes and Maven-generated files.

- **jvm2json/**: A git submodule for converting JVM bytecode to JSON format.

  - This tool is used to convert Java classes to JSON for analysis. It is an external project included for convenience, but we do not maintain it. It was created by our course instructor, and the project can be found here: [jvm2json GitLab](https://gitlab.gbar.dtu.dk/chrg/jvm2json).

- **scripts/**: Python scripts for executing various analysis tasks.

  - `analyse.py`, `interpret.py`, `rotate.py`, and `evaluate.py`.

- **src/**: The core Python implementation for static analysis.

  - **static\_analysis/**: Contains the static analysis logic, including interpreters for abstract interpretation.
  - **prediction/**: Predictors for determining the impact of changes on tests.
  - **evaluation/**: Modules for evaluating the results of static analysis.
  - **preparation/** and **reader/**: Modules for preparing data and reading input files.
  - **syntactic\_analysis/**: Handles syntactic analysis, including scanning and bytecode call graph analysis.

- **tests/**: Unit tests for validating the Python static analysis.

  - **scenario/**: Contains tests related to change scenarios.

## Getting Started

### Prerequisites

- **Python 3.13**: Required for running the static analysis pipeline.
- **Java 8+**: Required for compiling and running the Java example.
- **Maven**: Required for building the Java example.
- **jvm2json**: One of the following tools is required:
  - **Haskell** (optional): Required for building the `jvm2json` tool if not using Nix.
  - **Docker** (optional): Provides an alternative way to use `jvm2json` without building from source.
  - **Nix** (optional): Used for setting up dependencies for the `jvm2json` project.

### Installation

1. Clone the repository, including the `jvm2json` submodule:

   ```sh
   git clone --recurse-submodules <repository-url>
   cd <repository-directory>
   ```

2. Set up the Python environment using PDM:

   ```sh
   pdm install
   ```

3. Set up the `jvm2json` tool:

   ```sh
   cd jvm2json
   # Follow the instructions in the project's README to set up `jvm2json`
   ```

## Running the Static Analysis

### Preparing the Data

To prepare the Java example project for interpretation, use the following command:

```sh
pdm run rotate
```

The `rotate` script performs the following actions:

- Moves the current `data/new` directory to `data/old`.
- Copies the `java-example` project to `data/new`.
- Compiles the Java project and converts the bytecode to JSON for analysis.

Changes can be made in the `java-example` project, and `rotate` can be run again to create two program versions (`data/old` and `data/new`) for analysis to manually test change detection.

### Running the Analysis

Run the analysis:

```sh
pdm run analyse -h
```

**Usage**:

```
usage: -c [-h] [--new NEW] [--old OLD] {sign,interval,callgraph}

Debug tool to run a predictive test selection using specified program directories.

positional arguments:
  {sign,interval,callgraph}
                        The predictor to use for the analysis.

options:
  -h, --help            show this help message and exit
  --new NEW             Path to the new program directory.
  --old OLD             Path to the old program directory.
```

### Interpreting the Results

Run the interpreter on a test method:

```sh
pdm run interpret -h
```

**Usage**:

```
 usage: -c [-h] [--skip-rotation] [-v] [--select SELECT] {sign,interval}

Run the interpreter on all test methods.

positional arguments:
  {sign,interval}  The interpreter to use.

options:
  -h, --help       show this help message and exit
  --skip-rotation  Skip data rotation.
  -v, --verbose    Enable debug logging.
  --select SELECT  Select only methods where the name contains this string.
```

## Evaluating Results

To evaluate the impact of code changes on test coverage, run the evaluation script:

```sh
pdm run evaluate -h
```

**Usage**:

```
usage: -c [-h] [--no-threads] {sign,interval,callgraph}

Run test suite evaluation with the specified predictor.

positional arguments:
  {sign,interval,callgraph}  The predictor to use for the evaluation.

options:
  -h, --help                 Show this help message and exit
  --no-threads               Disable threading for the evaluation.
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

