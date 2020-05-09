# WCPCTL
## A `kubectl` like commandline tool to interact with vSphere 7 with Kubernetes Supervisor Cluster.

---

vSPhere 7 with Kubernetes brings some amazing features that enable you to run K8s nativly on your compute clusters. While the product is amazing, currently most of the interaction to the platform is currently limited to interaction with the vCenter UI. While the user interactions are minimal, the thought process for this project was to take those interactions thru a CLI tool. If its a CLI tool, why not make it `kubectl` style, with simple, user friendly `yaml` files to provide the configurations.

---

* Language - Python (tested on v3.7, MacOS and Linux)
* Required modules - requests, json, time, yaml, uuid, argparse, getpass

---

Currently the following actions are supported - 
* Creation of the Supervisor Cluster
* Creation of Namespaces
* Creation of Harbor registry (WIP)
* Reconfiguration of Namespaces
* Deletion of Namespaces
* Deletion of Harbor registry (WIP)
* Deletion of Supervisor cluster

---

