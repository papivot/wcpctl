# WCPCTL
## A `kubectl` like commandline tool to interact with vSphere 7 with Kubernetes Supervisor Cluster.

---

vSPhere 7 with Kubernetes brings some amazing features that enable you to run K8s nativly on your compute clusters. While the product is amazing, currently most of the interaction to the platform is currently limited to interaction with the vCenter UI. While the user interactions are minimal, the thought process for this project was to take those interactions thru a CLI tool. If its a CLI tool, why not make it `kubectl` style, with simple, user friendly `yaml` files to provide the configurations.

---

* Language - Python (tested on v3.7, MacOS and Linux)
* Required modules - requests, json, time, yaml, uuid, argparse, getpass

---

### Currently the following actions are supported - 
* Creation of the Supervisor Cluster
* Creation of Namespaces
* Creation of Harbor registry (WIP)
* Reconfiguration of Namespaces (Resource config is a WIP)
* Deletion of Namespaces
* Deletion of Harbor registry (WIP)
* Deletion of Supervisor cluster

---

### Setup 
* Make sure Python3 is installed and working.
* Make sure the modules listed above are installed. May require pip3 to install.
* Make sure you have admin access to the vCenter server.
* Make sure the workstation where the `wcpctl` cli will run on has access to the VCenter server. 
* Clone this repo. 
* Modify the YAML config files provided in the sample folder. 
* Execute the `wcpctl` code.

```
python3 wcpctl.py -h                                                                                    ✔  10182  19:55:49
usage: wcpctl.py [-h] [-u USERID] [--version] verb filename

wcpctl controls for managing Supervisor Clusters in vSphere 7 with K8s. Uses
YAML configuration files to setup and manage the Supervisor Cluster. For
additionalinformation at: https://github.io/papivot/wcpctl

positional arguments:
  verb        Provide action to perform. Currently supports
              create/apply/delete
  filename    yaml file with WCP configuration. See examples for help

optional arguments:
  -h, --help  show this help message and exit
  -u USERID   VCenter userid. If not provided, will default to
              administrator@vsphere.local
  --version   show program's version number and exit
```


