import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

CONFIG_DIR = Path("config")
BACKUP_DIR = Path("config_backup")

SETTINGS = {
    "core-site.xml": {
        "fs.defaultFS": "hdfs://namenode:9000",
        "hadoop.tmp.dir": "/hadoop/tmp",
        "io.file.buffer.size": "131072"
    },
    "hdfs-site.xml": {
        "dfs.replication": "2",
        "dfs.blocksize": "134217728",
        "dfs.namenode.name.dir": "/hadoop/dfs/name"
    },
    "mapred-site.xml": {
        "mapreduce.framework.name": "yarn",
        "mapreduce.jobhistory.address": "namenode:10020",
        "mapreduce.task.io.sort.mb": "256"
    },
    "yarn-site.xml": {
        "yarn.resourcemanager.address": "namenode:8032",
        "yarn.nodemanager.resource.memory-mb": "8192",
        "yarn.scheduler.minimum-allocation-mb": "1024"
    }
}


def modify_xml(file_path, updates):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for key, value in updates.items():
        found = False
        for prop in root.findall("property"):
            if prop.find("name").text == key:
                prop.find("value").text = value
                found = True
                break

        if not found:
            prop = ET.SubElement(root, "property")
            ET.SubElement(prop, "name").text = key
            ET.SubElement(prop, "value").text = value

    tree.write(file_path)
    print(f"  ✔ Modified {file_path.name}")


def main():
    print("=== Hadoop Configuration Modification ===")

    if not CONFIG_DIR.exists():
        print("ERROR: config directory not found")
        return

    BACKUP_DIR.mkdir(exist_ok=True)

    # 1️⃣ Backup
    for file in SETTINGS:
        src = CONFIG_DIR / file
        dst = BACKUP_DIR / file

        if not src.exists():
            print(f"ERROR: {file} not found")
            return

        shutil.copy(src, dst)
        print(f"Backup created: {dst}")

    # 2️⃣ Modify XML
    for file, updates in SETTINGS.items():
        print(f"Modifying {file}")
        modify_xml(CONFIG_DIR / file, updates)

    # 3️⃣ Restart Hadoop cluster
    print("\nStopping Hadoop cluster...")
    subprocess.run(["docker-compose", "down"], check=True)

    print("Starting Hadoop cluster...")
    subprocess.run(["docker-compose", "up", "-d"], check=True)

    print("\nConfiguration changes applied and Hadoop restarted successfully.")


if __name__ == "__main__":
    main()