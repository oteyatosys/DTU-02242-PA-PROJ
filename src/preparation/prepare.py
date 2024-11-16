import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)

data_dir = project_root / "data"
tmp_dir = data_dir / "tmp"
new_dir = data_dir / "new"
old_dir = data_dir / "old"

# Set the path to the jvm2json command (if not set already)
JVM2JSON_PATH = os.getenv("JVM2JSON_PATH", "jvm2json/result/bin/jvm2json")

# Helper function to convert class files to JSON with pretty print
def convert_classes_to_json(src_dir, dest_dir):
    for file in Path(src_dir).rglob("*.class"):
        # Set the output file path
        out_file = Path(dest_dir) / file.relative_to(src_dir).with_suffix(".json")

        # Make sure the target folder exists
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert the class to JSON bytecode
        result = subprocess.run(
            f"{JVM2JSON_PATH} < \"{file}\"",
            shell=True,
            capture_output=True,
            text=True
        )

        # Check if the subprocess ran successfully
        if result.returncode != 0 or not result.stdout:
            raise RuntimeError(f"Error running jvm2json for {file}: {result.stderr}")

        # Load the JSON output from jvm2json, then pretty-print it
        json_data = json.loads(result.stdout)
        with open(out_file, "w") as out_f:
            json.dump(json_data, out_f, indent=4)

def perform_rotation(maven_project: Path):
    shutil.rmtree(tmp_dir, ignore_errors=True)

    try:
        # Run maven to compile the Java code
        result = subprocess.run(["mvn", "-q", "-f", str(maven_project / "pom.xml"), "clean", "package", "-DskipTests"])

        if result.returncode != 0:
            raise RuntimeError("Error: Maven build failed")

        # Create a tmp directory
        tmp_dir.mkdir(parents=True, exist_ok=True)  # Make sure the tmp directory exists
        
        # Copy sources and classes to tmp directory
        shutil.copytree(maven_project / "src/main/java",       tmp_dir / "source")
        shutil.copytree(maven_project / "src/test/java",       tmp_dir / "test-source")
        shutil.copytree(maven_project / "target/classes",      tmp_dir / "classes")
        shutil.copytree(maven_project / "target/test-classes", tmp_dir / "test-classes")

        # Convert classes to JSON bytecode
        convert_classes_to_json(tmp_dir / "classes",      tmp_dir / "bytecode")
        convert_classes_to_json(tmp_dir / "test-classes", tmp_dir / "test-bytecode")

        # Rotate the data directories
        shutil.rmtree(old_dir, ignore_errors=True)
        new_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(new_dir), str(old_dir))
        shutil.move(str(tmp_dir), str(new_dir))

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
    finally:
        # Cleanup tmp directory
        shutil.rmtree(tmp_dir, ignore_errors=True)