#!/bin/bash

# Change directory to the directory of the script
cd "$(dirname "$0")"

new_dir="data/new"
old_dir="data/old"

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
rm -rf $old_dir
mkdir -p $new_dir

# Move all contents of new_dir to old_dir
mv $new_dir $old_dir
mkdir -p $new_dir

# Clean and build the java-example
mvn -q -f java-example/pom.xml clean package

# Copy the java-example class files to ./data/new/classes
cp -r java-example/target/classes/ $new_dir/classes/

# Copy the java-example class files to ./data/new/classes
cp -r java-example/target/test-classes/ $new_dir/test-classes/

# Copy the java-example source files to ./data/new/source
cp -r java-example/src/main/java/ $new_dir/source/

# Copy the java-example source files to ./data/new/test-source
cp -r java-example/src/test/java/ $new_dir/test-source/

# Convert all classes to bytecode
for file in $(find $new_dir/classes -name "*.class"); do

    # Set the output file path
    out_file=${file/classes/bytecode}
    out_file=${out_file%.class}.json

    # Make sure the target folder exists
    mkdir -p $(dirname ${file/classes/bytecode})

    # Convert the class to bytecode
    eval "$JVM2JSON_PATH < \"$file\" | $PRETTY_PRINT_CMD > \"$out_file\""
done


# Convert all test classes to test bytecode
for file in $(find $new_dir/test-classes -name "*.class"); do

    # Set the output file path
    out_file=${file/test-classes/test-bytecode}
    out_file=${out_file%.class}.json

    # Make sure the target folder exists
    mkdir -p $(dirname ${file/test-classes/test-bytecode})

    # Convert the class to bytecode
    eval "$JVM2JSON_PATH < \"$file\" | $PRETTY_PRINT_CMD > \"$out_file\""
done
