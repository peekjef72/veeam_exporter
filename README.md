# veeam_exporter

## Overview

![dashboard overview](./screenshots/veeam_general_dash.png)

## Description
Prometheus exporter for Veeam Entreprise Manager

This exporter collects metrics from Veeam Enterprise Manager HTTP API.

It is a python HTTP server that exposes metrics to http (default port 9247) that can be then scrapped by Prometheus.

Several Veeam server can be polled by adding them to the YAML config file, by adding a host section:

**Config**: (see config.yml)

```yaml
veeams:
  - host: host.domain
    port: 9398
    user: 'user'
    password: 'password'
    auth:
      # should be basic or encrypted
      type: basic
#   protocol: https
#   verify_ssl: false
#   timeout: 20
#   keep_session: true # default
#   default_labels:
#     - name: veeam_em
#       value: my_veeam_em_server.domain
#   proxy:
#     url: http://my.proxy.domain:port/
#     protocol: https

weblisten:
  address: 0.0.0.0
  port: 9247

logger:
  level: info
  facility: syslog

metrics_file: "conf/metrics/*_metrics.yml"
```

## Usage

The exporter may run as a unix command with module installation or as standalone python script without instalation.
<summary>Usage as a system command</summary>

the easiest way is to install from pip:

```shell
pip3 install --upgrade veeam_exporter
```

then you can use the entry point, createc by the installer of the module in /usr/local/bin/veeam_exporter or in [venv]/bin/veeam_exporter for venv context.
The recommanded usage is in venv.

<summary>Usage as a Python Script</summary>

<br>

To use the exporter, few packages needs to be installed. This can be done using:

```shell
pip3 install -r pip_requirements.txt
```

<details>

Contents of requirements.txt

```python
Prometheus-client>=0.8.0
requests==2.23.0
PyYAML==5.3.1
tenacity==6.2.0
urllib3>=1.25.9
Jinja2>=2.11.2
python-dateutil>=0.6.12
pycryptodome>=3.17.0
```

</details>

+ Consider, to extract the archiv file in /tmp folder; this will generate a folder /tmp/veeam_exporter_[version].
+ create a directory where you want, by example /opt/veeam_exporter_[version],
+ move the /tmp/veeam_exporter_[version]/veeam_exporter_package directory to /opt/eeam_exporter_[version]
+ create a command file to launch the exporter in dir /opt/veeam_exporter_[version]
```shell
vi /opt/veeam_exporter_X.Y.Z/veeam_exporter_cmd
#!/usr/libexec/platform-python
# -*- coding: utf-8 -*-
import re
import sys
from veeam_exporter.veeam_exporter import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())

```
+ Then edit the conf/config.yml file and add your settings.
+ Try your config by executing the command in try mode

example with the default dummy config file:
```shell
python3 veeam_exporter_cmd -n -v
veeam_exporter[647132]: level=INFO - veeam_exporter 1.0.3 starting....
veeam_exporter[647132]: level=DEBUG - config is {'veeams': [{'host': 'host.domaine', 'port': 9398, 'user': 'user', 'password': 'password', 'verify_ssl': False, 'timeout': 20}], 'weblisten': {'address': '0.0.0.0', 'port': 9247}, 'logger': {'level': 'info', 'facility': 'syslog'}, 'metrics_file': 'conf/metrics/*_metrics.yml'}
veeam_exporter[647132]: level=ERROR - Connection Exception: Host host.domaine: HTTPSConnectionPool(host='host.domaine', port=9398): Max retries exceeded with url: /api/sessionMngr/?v=latest (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7fa9e4eab9b0>: Failed to establish a new connection: [Errno -2] Name or service not known',))
veeam_exporter[647132]: level=DEBUG - # HELP veeam_em_up probe success  login status: 0 Down / 1 Up
veeam_exporter[647132]: level=DEBUG - # TYPE veeam_em_up gauge
veeam_exporter[647132]: level=DEBUG - veeam_em_up 0.0
veeam_exporter[647132]: level=INFO - veeam_exporter 1.0.3 stopped.
```

## exporter command line options

to start the exporter:

```shell
./veeam_exporter &
```

By default, it will load the file config.yml to perform action.

<details>
<summary>Detail options</summary>

```shell

Usage: veeam_exporter [-h] [-b BASE_PATH] [-c CONFIG_FILE]
                      [-f LOGGER.FACILITY] [-l {error,warning,info,debug}]
                      [-o  METRICS_FILE] [-m  METRIC] [-n] [-t  TARGET]
                      [-w WEB.LISTEN_ADDRESS] [-V] [-v]

collector for veeam server.

optional arguments:
  -h, --help            show this help message and exit
  -b BASE_PATH, --base_path BASE_PATH
                        set base directory to find default files.
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        path to config files.
  -f LOGGER.FACILITY, --logger.facility LOGGER.FACILITY
                        logger facility (syslog or file path).
  -l {error,warning,info,debug}, --logger.level {error,warning,info,debug}
                        logger level.
  -o  METRICS_FILE, --metrics_file METRICS_FILE
                        collect the metrics from the specified file instead of
                        config.
  -m  METRIC, --metric METRIC
                        collect only the specified metric name from the
                        metrics_file.
  -n , --dry_mode       collect the metrics then exit; display results to
                        stdout.
  -t  TARGET, --target TARGET
                        In dry_mode collect metrics on specified target.i
                        Default first from config file.
  -w WEB.LISTEN_ADDRESS, --web.listen-address WEB.LISTEN_ADDRESS
                        Address to listen on for web interface and telemetry.
  -V, --version         display program version and exit..
  -v , --verbose        verbose mode; display log message to stdout.
```

</details>

To test your configuration you can launch the exporter in dry_mode:

```shell
./veeam_exporter -v -n -t host.domain
```

This command will try to connect to the 'host.domain' veeam server with parameters specified in config.yml, expose the collected metrics, and eventually the warning or errors, then exits.

## Prometheus config

Since several veeam servers can be set in the exporter, Prometheus addresses each server by adding a target parameter in the url. The "target" must be the same (lexically) that in exporter config file.

```yaml
  - job_name: "veeam"
    scrape_interval: 120s
    scrape_timeout: 60s
    metrics_path: /metrics

    static_configs:
      - targets: [ veeamhost.domain ]
        labels:
          environment: "PROD"
#    file_sd_configs:
#      - files: [ "/etc/prometheus/veeam_exp/*.yml" ]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: "veeam-exporter-hostname.domain:9247"  # The veeam exporter's real hostname.

```

## Metrics

The collected metrics are defined in separate files positioned the folder conf/metrics.
All Values, computations, labels are defined in the metrics files, meaning that the exporter does nothing internally on values. The configuration fully drives how values are rendered.

### Collected Metrics

All metrics are defined in the configuration file (conf/metrics/*.yml). You can retrive all metric names here. Most of them have help text too.

file | domain | metrics
---- | ------ | -------
veeam_overview_metrics.yml | general results | count by type "backup", "proxy", "repository", "scheduled_jobs", "successful_vms", "warning_vms"
vm_overview_metrics.yml | general vm results | VMs count by protection type "protected","backedup","replicated","restore_points"<br>VMs total size in bytes by type "full_backup_points", "incremental_backup_points", "replica_restore_points", "source_vms"<br>percent of sucessful backup of VMs
repositories_metrics.yml | repositories | total and free size and in bytes of each repository by name and type
jobs_overview_metrics.yml | jobs generics | various count of job types "running", "scheduled", "scheduled_backup" "scheduled_replica_jobs_count"<br>total number of job runs by type "total", "successfull", "warning", "failed"<br>max duration for job by type and name of longuest
backup_agent_metrics.yml | backup agent | backup agent status 1 Online / 2 Offline labeled by nae , type and version
backup_servers_metrics.yml | backup servers | config of each backup server labeled by name, description, port, version: no value collect (1 returned)
backup_jobs_sessions_metrics.yml | backup jobs runs | last backup job run info state, duration, retries labeled by backup server, jobname, jobtype
vm_backup_jobs_sessions_metrics.yml| vm backup jobs runs | last vm backup job runs info state, duration, retries, total_bytes labeled by backup server, jobname, vmname, taskname, message

## Extending metrics

Exported metrics, are defined the YAML config file. The value can use Jinja2 templating language. The format of the configuration is inspired from Ansible task representation.
So a metric configuration file, consists in a list of action to perform.

There are five possible actions:

- url: to collect metrics from HTTP API
- set_fact: to assign vlaue to variables
- actions: to perform a list of (sub-)actions
- metrics: to define metrics to expose/return to Prometheus
- debug: to display debug text to logger.

All actions have default "attributes":

- name: the name of action or metric counter for metrics action.
- vars: to set vars to global symbols' table.
- with_items: to loop on current action with a list of items.
- loop_var: to set the name of the variable that will receive the current value in the loop. Default is 'item'.
- when: a list of condition (and) that must be check and be true to perform the action.

The "attributes" are analyzed in the order specified in previous table; it means that you can't use "item" var (obtained from 'with_items' directive) in the vars section because it is not yet defined when the 'vars' section is evaluated. If you need that feature, you will have to consider 'with_items' in an 'actions' section (see metrics/backup_jobs_sessions_metrics.yml).

action | parameter | description | remark
------ | ----------- | ------ | ------
url | &nbsp; |a string that's representing the entity to collect without '/api' | http://host.domain:port/api**[url]**. e.g.: /reports/summary/overview
 &nbsp; | var_name |the name of the variable to store the results. Default is '_root' meaning that the resulting JSON object is directly store in symbols table. | &nbsp;
 &nbsp; | &nbsp; | &nbsp; | &nbsp; 
 set_fact | &nbsp; | list of variable to define | &nbsp; 
 &nbsp; | var_name: value| &nbsp;  
 &nbsp; | &nbsp; | &nbsp; | &nbsp; 
metrics | &nbsp; | define the list of metrics to expose
 &nbsp; | metric_prefix | a prefix to add to all metric name | final name will be [metric_prefix]_[metric_name]
 'a metric' | name | the name of the metric
 &nbsp; | help | the help message added to the metric (and displayed in grafana explorer)
 &nbsp; | type 'gauge' or 'counter' | the type of the prometheus metric | &nbsp;
 &nbsp; | value | the numeric value itself | &nbsp;
 &nbsp; | labels | a list of name value pairs to qualify the metric | &nbsp;

# Password encryption

There is no miracle solution since no user interaction is possible, including the launching time of the exporter.
This exporter now includes a basic method to crypt/decrypt password based a symetric 128 bits key (16 bytes) shared between prometheus and the exporter.

How it works:
- generate and store a 16 or 32 bytes password in your favorite password tool (keepass by example). It will be used as a shared secret key.
- use the provided tool to encrypt the password (passwd_crypt). It generates an encrypted base64 text.
- set the exporter config file with the encrypted password and set a property to inform the exporter that the password is encrypted.
- set the Prometheus configuration to add a parameter authkey set to the shared secret key to scrap the target.

The exporter config file now doesn't expose the password in clear text, and it can authenticate to the Veeam Server when it requires by decrypting the password with the authkey send by Prometheus.

The authkey is not kept by the exporter: it is received, used if login is required, then dropt. Same for the decrypted password: it is used to build the basic authorisation header then zeroed (but may remained in memory because of python immutable string...)

Most of the time, the exporter will use the authentication token received after a successfull login unless you set keep_session to false for the target. So decryption has a litle impact on performance.

## Usage

```shell
$ ./passwd_crypt -h
usage: passwd_crypt [-h] [-d] [-k KEY] [-p  PASSWORD]

Generate encrypted password with shared key.

optional arguments:
  -h, --help            show this help message and exit
  -d , --decrypt        decrypt the provided text.
  -k KEY, --key KEY     set the key to encrypted set password.
  -p  PASSWORD, --password PASSWORD
                        password to crypt.
```

### generate an encrypted password 

```shell
$ ./passwd_crypt
shared key:
password to encypt:
encrypted result: jW8ZeHnrNTViBfEJ5ce62PYI0P9uwWGwkCuS6sPAyErwBffzsi4u8U35
```
you can verify the password:

```shell
$ ./passwd_crypt -d
shared key:
password to decrypt:
content: b'my_password'
```

### Store encrypted password in configuration file

```yaml
veeams:
  - host: host.domain
    port: 9398
    user: user
    password: jW8ZeHnrNTViBfEJ5ce62PYI0P9uwWGwkCuS6sPAyErwBffzsi4u8U35
    auth:
      # should be basic or encrypted
      type: encrypted
```
### Check the exporter

At this point you can start the exporter in dry_mode and check the authentication to the target.
Use a simple curl command:

```shell
./veeam_exporter -n -b /etc/veeam_exporter/ --config_file /etc/veeam_exporter/config.yml
veeam_exporter[794831]: level=INFO - veeam_exporter 1.1.2 starting....
veeam_exporter[794831]: level=DEBUG - config is {'veeams': [{'host': 'host.domain', 'port': 9398, 'user': 'user', 'password': 'REMOVED', 'authmode': {'type': 'encrypted'}, 'verify_ssl': False, 'timeout': 20}], 'weblisten': {'address': '0.0.0.0', 'port': 9247}, 'logger': {'level': 'info', 'facility': 'syslog'}, 'metrics_file': 'metrics/*_metrics.yml'}
target required encrypted auth!
authkey:
veeam_exporter[794831]: level=INFO - Veeam Entreprise Manager Session Login Successful on host.domain
veeam_exporter[794831]: level=DEBUG - task: Overview of the Veeam Agents.
veeam_exporter[794831]: level=DEBUG - task: collect elements.
veeam_exporter[794831]: level=DEBUG - task: procceed elements.
veeam_exporter[794831]: level=DEBUG - task: Overview of Backup Job Sessions.
...
veeam_exporter[794831]: level=DEBUG - # TYPE veeam_em_overview_vms_count gauge
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_count{type="protected"} 2152.0
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_count{type="backedup"} 2152.0
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_count{type="replicated"} 0.0
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_count{type="restore_points"} 2189.0
veeam_exporter[794831]: level=DEBUG - # HELP veeam_em_overview_vms_total_bytes VMs total size in bytes by type "full_backup_points", "incremental_backup_points", "replica_restore_points", "source_vms"
veeam_exporter[794831]: level=DEBUG - # TYPE veeam_em_overview_vms_total_bytes gauge
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_total_bytes{type="full_backup_points"} 3.8789074898944e+013
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_total_bytes{type="incremental_backup_points"} 1.856634806272e+013
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_total_bytes{type="replica_restore_points"} 0.0
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_total_bytes{type="source_vms"} 3.2752758516237e+014
veeam_exporter[794831]: level=DEBUG - # HELP veeam_em_overview_vms_sucess_backup_percent percent of sucessful backup of VMs
veeam_exporter[794831]: level=DEBUG - # TYPE veeam_em_overview_vms_sucess_backup_percent gauge
veeam_exporter[794831]: level=DEBUG - veeam_em_overview_vms_sucess_backup_percent 100.0
veeam_exporter[794831]: level=INFO - veeam_exporter 1.1.2 stopped.
$
```

if something went wrong:

```shell
veeam_exporter[794427]: level=INFO - veeam_exporter 1.1.2 starting....
veeam_exporter[794427]: level=DEBUG - config is {'veeams': [{'host': 'host.domain', 'port': 9398, 'user': 'user', 'password': 'REMOVED', 'authmode': {'type': 'encrypted'}, 'verify_ssl': False, 'timeout': 20}], 'weblisten': {'address': '0.0.0.0', 'port': 9247}, 'logger': {'level': 'info', 'facility': 'syslog'}, 'metrics_file': 'metrics/*_metrics.yml'}
target required encrypted auth!
authkey:
veeam_exporter[794427]: level=ERROR - Login Session Failed on host.domain: Incorrect AES key length (4 bytes)
veeam_exporter[794427]: level=DEBUG - # HELP veeam_em_up probe success  login status: 0 Down / 1 Up
veeam_exporter[794427]: level=DEBUG - # TYPE veeam_em_up gauge
veeam_exporter[794427]: level=DEBUG - veeam_em_up 0.0
veeam_exporter[794427]: level=INFO - veeam_exporter 1.1.2 stopped.
$
```

### Configure Prometheus job

If you have a same shared key for all targets you can only add the directive "param" in the job:
```yaml
  - job_name: "veeam"
    scrape_interval: 120s
    scrape_timeout: 60s
    metrics_path: /metrics
    params:
      auth_key: mwscDtQqIGtlnAxCzwz6hoz3ehjetMnP

    static_configs:
      - targets: [ veeamhost.domain ]
        labels:
          environment: "PROD"

#    file_sd_configs:
#      - files: [ "/etc/prometheus/veeam_exp/*.yml" ]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - source_labels: [__auth_key]
        target_label: __param_authkey
      - target_label: __address__
        replacement: "veeam-exporter-hostname.domain:9247"  # The veeam exporter's real hostname.
```

but if each target has its own shared key, the it as a label of the target and set it by relabeling:

```yaml
  - job_name: "veeam"
    scrape_interval: 120s
    scrape_timeout: 60s
    metrics_path: /metrics

    static_configs:
      - targets: [ veeamhost.domain ]
        labels:
          environment: "PROD"
          __auth_key: mwscDtQqIGtlnAxCzwz6hoz3ehjetMnP

#    file_sd_configs:
#      - files: [ "/etc/prometheus/veeam_exp/*.yml" ]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - source_labels: [__auth_key]
        target_label: __param_authkey
      - target_label: __address__
        replacement: "veeam-exporter-hostname.domain:9247"  # The veeam exporter's real hostname.
```
