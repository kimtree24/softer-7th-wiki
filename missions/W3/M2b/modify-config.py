import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

CONFIG_DIR = Path(sys.argv[1])
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

def modify_xml(path, updates):
    tree = ET.parse(path)
    root = tree.getroot()

    for k, v in updates.items():
        found = False
        for prop in root.findall("property"):
            if prop.find("name").text == k:
                prop.find("value").text = v
                found = True
        if not found:
            p = ET.SubElement(root, "property")
            ET.SubElement(p, "name").text = k
            ET.SubElement(p, "value").text = v

    tree.write(path)

def main():
    BACKUP_DIR.mkdir(exist_ok=True)

    print("Backing up config files...")
    for f in SETTINGS:
        shutil.copy(CONFIG_DIR / f, BACKUP_DIR / f)

    print("Modifying XML files...")
    for f, updates in SETTINGS.items():
        modify_xml(CONFIG_DIR / f, updates)
        print(f"  Modified {f}")

    print("\nRestarting Hadoop services...")
    subprocess.run([
        "docker", "exec", "master", "bash", "-c",
        "stop-dfs.sh && stop-yarn.sh && start-dfs.sh && start-yarn.sh"
    ], check=True)

    print("\nConfiguration applied and Hadoop restarted")

if __name__ == "__main__":
    main()