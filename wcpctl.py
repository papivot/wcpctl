#!/usr/bin/env python3
import requests
import json
import time
import yaml
import sys
import uuid
import argparse
import getpass

parser = argparse.ArgumentParser(description='wcpctl controls for managing Supervisor Clusters in vSphere 7 with K8s. Uses YAML configuration files to setup and manage the Supervisor Cluster. For additionalinformation at: https://github.io/papivot/wcpctl')
parser.add_argument('verb', action="store", help='Provide action to perform. Currently supports create/apply/delete')
parser.add_argument('filename', action="store", help='yaml file with WCP configuration. See examples for help')
parser.add_argument('-u', action="store", dest="userid", help='VCenter userid. If not provided, will default to administrator@vsphere.local')

parser.add_argument('--version', action='version',version='%(prog)s v0.1')
cmd = parser.parse_args()

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
headers = {'content-type':'application/json'}

verb = cmd.verb
filename = cmd.filename
if cmd.userid:
    userid = cmd.userid
else:
    userid = "administrator@vsphere.local"

password = getpass.getpass(prompt='Password: ')

########### Enable for debugging
############
#verb = "create"
#verb = "delete"
#verb = "apply"
#filename = 'wcpall-haas.yaml'
#userid = "administrator@vsphere.local"
#password = "VMware1!"

def generate_random_uuid():
    return str(uuid.uuid4())

def get_storage_policy(sp_name):
    json_response = s.get('https://'+vcip+'/rest/vcenter/storage/policies')
    if json_response.ok:
        results = json.loads(json_response.text)["value"]
        for result in results:
            if result["name"] == sp_name:
                return result["policy"]
        else:
            return 0
    else:
        return 0
    return 0

def get_content_library(cl_name):
    json_response = s.get('https://'+vcip+'/rest/com/vmware/content/library')
    if json_response.ok:
        results = json.loads(json_response.text)["value"]
        for result in results:
            json_response = s.get('https://'+vcip+'/rest/com/vmware/content/library/id:'+result)
            if json_response.ok:
                cl_library = json.loads(json_response.text)["value"]
                if cl_library["name"] == cl_name:
                    return cl_library["id"]
    else:
        return 0
    return 0

def get_nsx_switch(cluster):
    json_response = s.get('https://'+vcip+'/api/vcenter/namespace-management/distributed-switch-compatibility?cluster='+cluster+'&compatible=true')
    if json_response.ok:
        results = json.loads(json_response.text)
        # Making assumption that there is only 1 distributed switch.
        nsx_sw_id=results[0]['distributed_switch']
        return nsx_sw_id
    else:
        return 0

def get_nsx_edge_cluster(cluster,dvs):
    json_response = s.get('https://'+vcip+'/api/vcenter/namespace-management/edge-cluster-compatibility?cluster='+cluster+'&compatible=true&distributed_switch='+dvs)
    if json_response.ok:
        results = json.loads(json_response.text)
        edge_id=results[0]['edge_cluster']
        return edge_id
    else:
        return 0

def get_mgmt_network(mgmt_nw_name, dc):
    json_response=s.get('https://'+vcip+'/rest/vcenter/network?filter.datacenters='+dc)
    if json_response.ok:
        results = json.loads(json_response.text)["value"]
        for result in results:
            if result["name"] == mgmt_nw_name:
                return result["network"]
    else:
        return 0
    return 0

def check_wcp_cluster_compatibility(cluster):
    json_response = s.get('https://'+vcip+'/api/vcenter/namespace-management/cluster-compatibility')
    if json_response.ok:
        results = json.loads(json_response.text)
        res = next((sub for sub in results if sub['cluster'] == cluster), None)
        if res['compatible'] == True:
            return 1
        else:
            return 0
    else:
        return 0

def check_wcp_cluster_status(cluster):
    json_response = s.get('https://'+vcip+'/api/vcenter/namespace-management/clusters/'+cluster)
    if json_response.ok:
        result = json.loads(json_response.text)
        if result["config_status"] == "RUNNING":
            if result["kubernetes_status"] == "READY":
                return result["api_server_cluster_endpoint"]
        else:
            return 0
    else:
        return 0

def check_wcp_harbor_status(cluster):
    json_response = s.get('https://'+vcip+'/rest/vcenter/content/registries/harbor')
    if json_response.ok:
        results = json.loads(json_response.text)["value"]
        for result in results:
            if result["cluster"] == cluster:
                return result["registry"]
        else:
            return 0
    else:
        return 0

def check_wcp_ns_status(ns_name):
    json_response = s.get('https://'+vcip+'/api/vcenter/namespaces/instances/'+ns_name)
    if json_response.ok:
        result = json.loads(json_response.text)
        if result["config_status"] == "RUNNING":
            return 1
        else:
            return 0
    else:
        return 0

with open(filename,) as f:
    yamldocs = yaml.load_all(f, Loader=yaml.FullLoader)
    for yamldoc in yamldocs:
        objtype = yamldoc["kind"]
        vcip = yamldoc["metadata"]["vcenter"]
        datacenter = yamldoc["metadata"]["datacenter"]
        cluster = yamldoc["metadata"]["cluster"]
        spec = yamldoc["spec"]
        s = "Global"
        s=requests.Session()
        s.verify=False

        # Connect to VCenter and start a session
        vcsession = s.post('https://'+vcip+'/rest/com/vmware/cis/session',auth=(userid,password))
        if not vcsession.ok:
            print ("Session creation is failed, please check vcenter connection")
            sys.exit()

        # Based on the datacenter get all datacenters
        datacenter_object=s.get('https://'+vcip+'/rest/vcenter/datacenter?filter.names='+datacenter)
        if len(json.loads(datacenter_object.text)["value"])==0:
            print ("No datacenter found, please enter valid datacenter name")
            sys.exit()
        datacenter_id=json.loads(datacenter_object.text)["value"][0].get("datacenter")

        # Based on the cluster name get the cluster_id
        cluster_object=s.get('https://'+vcip+'/rest/vcenter/cluster?filter.names='+cluster+'&filter.datacenters='+datacenter_id)
        if len(json.loads(cluster_object.text)["value"])==0:
            print ("No cluster found, please enter valid cluster name")
            sys.exit()
        cluster_id=json.loads(cluster_object.text)["value"][0].get("cluster")

        if verb == "create":

            ################ create wcpCluster
            if objtype == "wcpCluster":
                del yamldoc["kind"]
                del yamldoc["metadata"]
                if check_wcp_cluster_compatibility(cluster_id):
                    if not check_wcp_cluster_status(cluster_id):

                        temp1 = get_storage_policy(yamldoc["spec"].get("ephemeral_storage_policy"))
                        if not temp1:
                            print ("wcpCluster/"+cluster+" check value for ephemeral_storage_policy")
                            sys.exit()
                        temp2 = get_storage_policy(yamldoc["spec"].get("master_storage_policy"))
                        if not temp2:
                            print ("wcpCluster/"+cluster+" check value for master_storage_policy")
                            sys.exit()
                        temp3 = get_storage_policy(yamldoc["spec"]["image_storage"].get("storage_policy"))
                        if not temp3:
                            print ("wcpCluster/"+cluster+" check value for storage_policy")
                            sys.exit()
                        temp4 = get_content_library(yamldoc["spec"].get("default_kubernetes_service_content_library"))
                        if not temp4:
                            print ("wcpCluster/"+cluster+" check value for default_kubernetes_service_content_library")
                            sys.exit()
                        temp5 = get_mgmt_network(yamldoc["spec"]["master_management_network"].get("network"), datacenter_id)
                        if not temp5:
                            print ("wcpCluster/"+cluster+" check value for master_management_network - network")
                            sys.exit()
                        temp6 = get_nsx_switch(cluster_id)
                        if not temp6:
                            print ("wcpCluster/"+cluster+" no compatiable NSX switch for cluster")
                            sys.exit()
                        temp7 = get_nsx_edge_cluster(cluster_id, temp6)
                        if not temp7:
                            print ("wcpCluster/"+cluster+" no compatiable NSX edge cluster")
                            sys.exit()

                        #Update any of the above is 0 then quit

                        yamldoc["spec"].update({"ephemeral_storage_policy": temp1})
                        yamldoc["spec"].update({"master_storage_policy": temp2})
                        yamldoc["spec"]["image_storage"].update({"storage_policy": temp3})
                        yamldoc["spec"].update({"default_kubernetes_service_content_library": temp4})
                        yamldoc["spec"]["master_management_network"].update({"network": temp5})
                        yamldoc["spec"]["ncp_cluster_network_spec"].update({"cluster_distributed_switch": temp6})
                        yamldoc["spec"]["ncp_cluster_network_spec"].update({"nsx_edge_cluster": temp7})

                        json_payload = json.loads(json.dumps(yamldoc["spec"]))
                        json_response = s.post('https://'+vcip+'/api/vcenter/namespace-management/clusters/'+cluster_id+'?action=enable', headers=headers,json=json_payload)
                        if json_response.ok:
                            print ("wcpCluster/"+cluster+" creation started")
                        else:
                            print ("wcpCluster/"+cluster+" creation failed")
                            print (json_response.text)
                    else:
                        print ("wcpCluster/"+cluster+" already operational at https://"+check_wcp_cluster_status(cluster_id))
                else:
                    print ("wcpCluster/"+cluster+" not compatiable")

            ################ create wcpRegistry
            if objtype == "wcpRegistry":
                if not check_wcp_harbor_status(cluster_id):
                    del yamldoc["kind"]
                    del yamldoc["metadata"]
                    client_token=generate_random_uuid()
                    yamldoc.update({"client_token": client_token})
                    yamldoc["spec"].update({"cluster": cluster_id})
                    i = 0
                    # Update variables and proceed
                    for sp in yamldoc["spec"]["storage"]:
                        temp1 = get_storage_policy(sp["policy"])
                        if temp1:
                            yamldoc["spec"]["storage"][i].update({"policy": temp1})
                        else:
                            print ("wcpNamespace/"+spec["namespace"]+" invalid storage policy specified")
                            sys.exit()
                        i = i+1
                    json_payload = json.loads(json.dumps(yamldoc))

                    json_response = s.post('https://'+vcip+'/rest/vcenter/content/registries/harbor',headers=headers,json=json_payload)
                    if json_response.ok:
                        print ("wcpRegistry/Harbor created")
                        time.sleep(15)
                    else:
                        print ("wcpRegistry/Harbor failed")
                        print (json_response.text)
                else:
                    print("wcpRegistry/Harbor already running")

            ################ create wcpNamespace
            if objtype == "wcpNamespace":
                if not check_wcp_ns_status(spec["namespace"]):
                    spec.update({"cluster": cluster_id})
                    i = 0
                    # Update variables and proceed
                    for sp in spec["storage_specs"]:
                        temp1 = get_storage_policy(sp["policy"])
                        if temp1:
                            spec["storage_specs"][i].update({"policy": temp1})
                        else:
                            print ("wcpNamespace/"+spec["namespace"]+" invalid storage policy specified")
                            sys.exit()
                        i = i+1
                    json_payload = json.loads(json.dumps(spec))
                    json_response = s.post('https://'+vcip+'/api/vcenter/namespaces/instances',headers=headers,json=json_payload)
                    if json_response.ok:
                        print("wcpNamespace/"+spec["namespace"]+" created")
                    else:
                        print("wcpNamespace/"+spec["namespace"]+" creation failed")
                        print(json_response.text)
                else:
                    print("wcpNamespace/"+spec["namespace"]+" already exists. No changes made")

        elif verb == "delete":

            ################ delete wcpCluster
            if objtype == "wcpCluster":
                if check_wcp_cluster_status(cluster_id):
                    # Check if you want to delete ???
                    json_response = s.post('https://'+vcip+'/api/vcenter/namespace-management/clusters/'+cluster_id+'?action=disable')
                    if json_response.ok:
                        print ("wcpCluster/"+cluster+" delete initiated")
                    else:
                        print ("wcpCluster/"+cluster+" delete failed")
                        print (json_response.text)
                else:
                    print ("wcpCluster/"+cluster+" not operational")

            ################ delete wcpRegistry
            if objtype == "wcpRegistry":
                harbor_id = check_wcp_harbor_status(cluster_id)
                if harbor_id:
                    json_response = s.delete('https://'+vcip+'/rest/vcenter/content/registries/harbor/'+harbor_id)
                    if (json_response.ok):
                        print ("wcpRegistry/Harbor deleted")
                    else:
                        print ("wcpRegistry/Harbor deletion failed")
                        print (json_response.text)
                else:
                    print ("wcpRegistry/Harbor not found")
                    print (json_response.text)

            ################ delete wcpNamespace
            if objtype == "wcpNamespace":
                json_response = s.delete('https://'+vcip+'/api/vcenter/namespaces/instances/'+spec["namespace"])
                if (json_response.ok):
                    print ("wcpNamespace/"+spec["namespace"]+" deleted")
                else:
                    print ("wcpNamespace/"+spec["namespace"]+" deletion failed")
                    print (json_response.text)

        elif verb == "apply":

            ################ apply wcpCluster
            if objtype == "wcpCluster":
                del yamldoc["kind"]
                del yamldoc["metadata"]
                if check_wcp_cluster_compatibility(cluster_id):
                    if not check_wcp_cluster_status(cluster_id):

                        temp1 = get_storage_policy(yamldoc["spec"].get("ephemeral_storage_policy"))
                        temp2 = get_storage_policy(yamldoc["spec"].get("master_storage_policy"))
                        temp3 = get_storage_policy(yamldoc["spec"]["image_storage"].get("storage_policy"))
                        temp4 = get_content_library(yamldoc["spec"].get("default_kubernetes_service_content_library"))
                        temp5 = get_mgmt_network(yamldoc["spec"]["master_management_network"].get("network"), datacenter_id)
                        temp6 = get_nsx_switch(cluster_id)
                        temp7 = get_nsx_edge_cluster(cluster_id, temp6)

                        #Update any of the above is 0 then quit

                        yamldoc["spec"].update({"ephemeral_storage_policy": temp1})
                        yamldoc["spec"].update({"master_storage_policy": temp2})
                        yamldoc["spec"]["image_storage"].update({"storage_policy": temp3})
                        yamldoc["spec"].update({"default_kubernetes_service_content_library": temp4})
                        yamldoc["spec"]["master_management_network"].update({"network": temp5})
                        yamldoc["spec"]["ncp_cluster_network_spec"].update({"nsx_edge_cluster": temp6})
                        yamldoc["spec"]["ncp_cluster_network_spec"].update({"cluster_distributed_switch": temp7})

                        json_payload = json.loads(json.dumps(yamldoc["spec"]))
                        json_response = s.post('https://'+vcip+'/api/vcenter/namespace-management/clusters/'+cluster_id+'?action=enable', headers=headers,json=json_payload)
                        if json_response.ok:
                            print ("wcpCluster/"+cluster+" creation started")
                        else:
                            print ("wcpCluster/"+cluster+" creation failed")
                            print (json_response.text)
                    else:
                        print ("wcpCluster/"+cluster+" already operational at https://"+check_wcp_cluster_status(cluster_id))
                else:
                    print ("wcpCluster/"+cluster+" not compatiable")

               # json_payload = json.loads(json.dumps(mypayload))
               # aa = check_wcp_cluster_compatibility(cluster_id)
                #if check_wcp_cluster_status(cluster_id):
                    # To patch cluster
                 #   json_response = s.patch('https://'+vcip+'/api/vcenter/namespace-management/clusters/'+cluster_id, headers=headers,json=json_payload)
                 #   if json_response.ok:
                 #       print ("wcpCluster/"+cluster+" updated")
                 #   else:
                 #       print ("wcpCluster/"+cluster+" update failed")
                 #       print (json_response.text)

                    # To rotate password
                    #json_response = s.post('https://'+vcip+'/api/vcenter/namespace-management/clusters/'+cluster_id+'?action=rotate_password')
                    #if json_response.ok:
                    #    print ("wcpCluster/"+cluster+" password rotated")
                    #else:
                    #    print ("wcpCluster/"+cluster+" password rotation failed")
                    #    print (json_response.text)
               # else:
                #    print ("wcpCluster/"+cluster+" not operational")

            ################ apply wcpRegistry
            if objtype == "wcpRegistry":
                #same as create as no modify option
                if not check_wcp_harbor_status(cluster_id):
                    del yamldoc["kind"]
                    del yamldoc["metadata"]
                    client_token=generate_random_uuid()
                    yamldoc.update({"client_token": client_token})
                    yamldoc["spec"].update({"cluster": cluster_id})
                    i = 0
                    # Update variables and proceed
                    for sp in yamldoc["spec"]["storage"]:
                        temp1 = get_storage_policy(sp["policy"])
                        if temp1:
                            yamldoc["spec"]["storage"][i].update({"policy": temp1})
                        else:
                            print ("wcpNamespace/"+spec["namespace"]+" invalid storage policy specified")
                            sys.exit()
                        i = i+1
                    json_payload = json.loads(json.dumps(yamldoc))

                    json_response = s.post('https://'+vcip+'/rest/vcenter/content/registries/harbor',headers=headers,json=json_payload)
                    if json_response.ok:
                        print ("wcpRegistry/Harbor created")
                        time.sleep(15)
                    else:
                        print ("wcpRegistry/Harbor failed")
                        print (json_response.text)
                else:
                    print("wcpRegistry/Harbor already running")

            ################ apply wcpNamespace
            if objtype == "wcpNamespace":
                if check_wcp_ns_status(spec["namespace"]):
                    spec.update({"cluster": cluster_id})
                    i = 0
                    # Update variables and proceed
                    for sp in spec["storage_specs"]:
                        temp1 = get_storage_policy(sp["policy"])
                        if temp1:
                            spec["storage_specs"][i].update({"policy": temp1})
                        else:
                            print ("wcpNamespace/"+spec["namespace"]+" invalid storage policy specified")
                            sys.exit()
                        i = i+1
                    json_payload = json.loads(json.dumps(spec))
                    json_response = s.put('https://'+vcip+'/api/vcenter/namespaces/instances/'+spec["namespace"],headers=headers,json=json_payload)
                    if json_response.ok:
	                    print ("wcpNamespace/"+spec["namespace"]+" updated")
                    else:
                        print ("wcpNamespace/"+spec["namespace"]+" update failed")
                        print (json_response.text)
                else:
                    spec.update({"cluster": cluster_id})
                    i = 0
                    # Update variables and proceed
                    for sp in spec["storage_specs"]:
                        temp1 = get_storage_policy(sp["policy"])
                        if temp1:
                            spec["storage_specs"][i].update({"policy": temp1})
                        else:
                            print ("wcpNamespace/"+spec["namespace"]+" invalid storage policy specified")
                            sys.exit()
                        i = i+1
                    json_payload = json.loads(json.dumps(spec))
                    json_response = s.post('https://'+vcip+'/api/vcenter/namespaces/instances',headers=headers,json=json_payload)
                    if json_response.ok:
	                    print ("wcpNamespace/"+spec["namespace"]+" created")
                    else:
                        print ("wcpNamespace/"+spec["namespace"]+" creation failed")
                        print (json_response.text)

        # Clean up and exit...
        session_delete=s.delete('https://'+vcip+'/rest/com/vmware/cis/session',auth=("Administrator@vsphere.local","Passw0rd!"))