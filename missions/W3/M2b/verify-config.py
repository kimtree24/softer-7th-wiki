import subprocess

CHECKS = [
    ("hdfs", "fs.defaultFS", "hdfs://namenode:9000"),
    ("hdfs", "hadoop.tmp.dir", "/hadoop/tmp"),
    ("hdfs", "io.file.buffer.size", "131072"),
    ("hdfs", "dfs.replication", "2"),
    ("hdfs", "dfs.blocksize", "134217728"),
    ("hdfs", "dfs.namenode.name.dir", "/hadoop/dfs/name"),

    ("hdfs", "mapreduce.framework.name", "yarn"),
    ("hdfs", "mapreduce.jobhistory.address", "namenode:10020"),
    ("hdfs", "mapreduce.task.io.sort.mb", "256"),

    ("hdfs", "yarn.resourcemanager.address", "namenode:8032"),
    ("hdfs", "yarn.nodemanager.resource.memory-mb", "8192"),
    ("hdfs", "yarn.scheduler.minimum-allocation-mb", "1024"),
]


def getconf(cmd, key):
    return subprocess.check_output(
        ["docker", "exec", "master", cmd, "getconf", "-confKey", key],
        text=True
    ).strip()


def main():
    for tool, key, expected in CHECKS:
        actual = getconf(tool, key)
        if actual == expected:
            print(f"PASS: [{tool} getconf {key}] -> {actual}")
        else:
            print(f"FAIL: [{tool} getconf {key}] -> {actual} (expected {expected})")

    print("Testing HDFS replication...")
    subprocess.run([
    "docker", "exec", "master", "bash", "-c",
    """
    echo testdata > /tmp/test.txt
    hdfs dfs -rm -r -f /rep_test
    hdfs dfs -mkdir /rep_test
    hdfs dfs -put /tmp/test.txt /rep_test/test.txt
    """
])

    rep = subprocess.check_output(
        ["docker", "exec", "master", "hdfs", "dfs", "-stat", "%r", "/rep_test/test.txt"],
        text=True
    ).strip()

    if rep == "2":
        print("PASS: Replication factor is 2")
    else:
        print(f"FAIL: Replication factor is {rep} (expected 2)")


if __name__ == "__main__":
    main()