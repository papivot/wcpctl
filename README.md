# WCPCTL
## A `kubectl` style command line tool to interact with vSphere 7 with Kubernetes Supervisor Cluster.

---

*vSphere 7 with Kubernetes* brings some amazing features that enable you to run K8s nativly on your compute clusters. While the product is amazing, currently most of the interaction to the platform is limited to interaction with the vCenter UI. While the user interactions are minimal, the thought process for this project was to perform those interactions thru a CLI tool. If its a CLI tool, why not make it `kubectl` style, with simple, user friendly `yaml` files to provide the configurations and JSON style outputs??

Some guidance inspired from the awesome work of *vthinkbeyondvm.com*

---

* Language - Python (tested on v3.7, MacOS, Linux and Windows Server 2016)
* Required modules - requests, json, time, yaml, uuid, argparse, getpass 
  * Most are generally available. May require install of yaml using the following - `pip3 install -U PyYAML` . 
  * Windows additionally may require requests. This can be installed by `pip3 install requests`.

---

### Currently the following actions are supported - 
* Creation of the Supervisor Cluster
* Creation of Namespaces
* Creation of Harbor registry
* Creation of Subscribed Content Library
* Reconfiguration of Namespaces (Resource config is a WIP)
* Deletion of Namespaces
* Deletion of Harbor registry 
* Deletion of Supervisor cluster
* Deletion of Subscribed Content Library
* Describe Namespace(s) (JSON output)
* Describe WCP Registry (JSON output)
* Describe WCP Cluster (JSON output)
* Describe Subscribed Content Library

---

### Setup 
* Make sure Python3 is installed and working.
* Make sure the modules listed above are installed. May require pip3 to install.
* Make sure you have admin access to the vCenter server.
* Make sure the workstation where the `wcpctl` cli will run on has access to the VCenter server. 
* Clone this repo. 
* Execute `chmod +x wcpctl.py` if its not already set to execute. 
* Modify the YAML config files provided in the `sample-config-yaml` folder. 
* If possible, move the `wcpctl.py` file a folder in $PATH. E.g. `sudo cp wcpctl.py /usr/local/bin`
* Execute the `wcpctl` code.

```
$ wcpctl.py -h  
=============================================================================

usage: wcpctl.py [-h] [--version] {create,apply,delete,describe} ...

wcpctl controls for managing Supervisor Clusters in vSphere 7 with K8s. Uses
YAML configuration files to setup and manage the Supervisor Cluster. Find
additional information at: https://github.io/papivot/wcpctl

positional arguments:
  {create,apply,delete,describe}
                        Commands
    create              Create WCP object(s)
    apply               Apply configuration changes to WCP object(s)
    delete              Delete WCP object(s)
    describe            Describe a WCP object(s)

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  
```
### Sample Examples

#### To enable/create a Supervisor Cluster
* modify the `wcp-cluster.yaml` sample provided in the `sample-config-yaml` folder. Make sure that the following are enabled/configured (as per official docs) - 
  - Relevent Content Library
  - NSX configuration

```
wcpctl.py create some-wcp-cluster-config.yaml -u administrator@vsphere.local
```

#### To disable the Supervisor Cluster, 
```
wcpctl.py delete some-wcp-cluster-config.yaml
```


#### To modify Namespace(s) 
```
wcpctl.py apply some-namespaceconfig.yaml
```

#### To create a Registry 
```
wcpctl.py create some-regconfig.yaml
```

#### To describe Registry 
```
wcpctl.py describe some-nsconfigfile.yaml
```

#### To create a WCP content library
```
wcpctl.py create some-contentlibconfigfile.yaml
```


### Feedback

Would love feedback from users. 
