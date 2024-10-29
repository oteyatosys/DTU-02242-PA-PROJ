#!/bin/bash

# Change directory to the directory of the script
cd "$(dirname "$0")"

# Set the path to the jvm2json command (if vbariable is not set already)
if [ -z "$JVM2JSON_PATH" ]; then
    # JVM2JSON_PATH="docker run --platform linux/amd64 --rm -i kalhauge/jvm2json:latest jvm2json"
    JVM2JSON_PATH="jvm2json/result/bin/jvm2json"
fi

# Set the default pretty print command (if variable is not set already)
if [ -z "$PRETTY_PRINT_CMD" ]; then
    PRETTY_PRINT_CMD="python3 -m json.tool"
fi

# Prepare the data directory
rm -rf ./data
mkdir -p ./data

# Clean and build the java-example
mvn -q -f java-example/pom.xml clean package

# Copy the java-example to ./data/classes
cp -r java-example/target/classes data/

# Convert all classes to bytecode
for file in $(find data/classes -name "*.class"); do

    # Set the output file path
    out_file=${file/classes/bytecode}
    out_file=${out_file%.class}.json

    # Make sure the target folder exists
    mkdir -p $(dirname ${file/classes/bytecode})

    # Convert the class to bytecode
    eval "$JVM2JSON_PATH < \"$file\" | $PRETTY_PRINT_CMD > \"$out_file\""
done
