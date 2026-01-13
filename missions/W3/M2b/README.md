## W3/M2b Hadoop Configuration

This mission updates Hadoop XML configuration files, provides a script to apply
the changes with backups and service restarts, and a script to verify the
configuration and cluster behavior.

### Files

- `missions/W3/M2b/config/core-site.xml`
- `missions/W3/M2b/config/hdfs-site.xml`
- `missions/W3/M2b/config/mapred-site.xml`
- `missions/W3/M2b/config/yarn-site.xml`
- `missions/W3/M2b/scripts/modify-config.py`
- `missions/W3/M2b/scripts/verify-config.py`

### Requirements

- Python 3
- Hadoop CLI available in `PATH` (`hdfs`, `hadoop`, `yarn`)
- `HADOOP_HOME` and `HADOOP_CONF_DIR` set appropriately for cluster commands

### Apply configuration changes

This script backs up the original XML files, applies the required settings, and
restarts Hadoop services if available.

```bash
python3 missions/W3/M2b/scripts/modify-config.py /path/to/hadoop/etc/hadoop
```

Backups are created next to the originals with a timestamp suffix like
`core-site.xml.bak.20240113153000`.

### Verify configuration changes

This script checks Hadoop configuration values, verifies HDFS replication with a
test file, runs a small MapReduce job, and queries YARN total memory.

```bash
python3 missions/W3/M2b/scripts/verify-config.py /path/to/hadoop/etc/hadoop
```

If you already have `HADOOP_CONF_DIR` set, you can omit the argument.
