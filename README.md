# WCPCTL
## A `kubectl` style command line tool to interact with vSphere 7 with Tanzu Supervisor Cluster.
## Now with support for vSphere 7.0 U1. 
### This can be used to spin up NSX-T or vSphere NW based Supervisor Cluster.

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
* Install the package using pip: `pip3 install .` in the base directory
* Modify the YAML config files provided in the `sample-config-yaml` folder. 
* Execute the `wcpctl` code.

```
$ wcpctl -h  
=============================================================================

usage: wcpctl [-h] [--version] {create,apply,delete,describe} ...

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
wcpctl create some-wcp-cluster-config.yaml -u administrator@vsphere.local
```

#### To disable the Supervisor Cluster, 
```
wcpctl delete some-wcp-cluster-config.yaml
```


#### To modify Namespace(s) 
```
wcpctl apply some-namespaceconfig.yaml
```

#### To create a Registry 
```
wcpctl create some-regconfig.yaml
```

#### To describe Registry 
```
wcpctl describe some-nsconfigfile.yaml
```

#### To create a WCP content library
```
wcpctl create some-contentlibconfigfile.yaml
```


### Feedback

Would love feedback from users. 

# How to add features

There has been significant change to the wcpctl file and the repo structure in general. First off, there is no singular file containing all code any longer. Command-line-specific code has been kept within wcpctl (and renamed) and specific implementation code has been moved into the src/command directory.

Each object type/kind supported (at this writing, wcpCluster, wcpContentLibrary, wcpNamespace, and wcpRegistry) have been extracted into classes that inherit from a common base. Each of these implement a create/delete/apply/describe method that is dynmically called by the Commands class. This dynamic pattern reduces if/else toil when handling command-line parameters. The top-level create/delete/apply/describe methods are defined in the commands module. Each will reach out to attempt to call the applicable method within the type/kind specified in the input yaml file(s).

To add a new object type/kind, simply implement the CommandBase class and its 4 methods (see existing modules in src/commands for examples).

# TODO
* Update Utilities class methods to share sessions from the command objects.