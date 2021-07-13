#
# “Copyright 2021 VMware, Inc.”
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import logging
import sys
from wcp_utility import *
from wcp_command.command_base import CommandBase

class wcpCluster(CommandBase): # class name is looked up dynamically
  
  def create(self):
    # create wcpCluster
    if self.objtype == "wcpCluster":

      logging.info("Found {} type in yaml, proceeding to create".format(__class__.__name__))
      del self.yamldoc["kind"]
      del self.yamldoc["metadata"]

      # cluster = Utilities.check_wcp_cluster_compatibility(self.cluster_id, self.yamldoc["spec"]["network_provider"], self.skip_compat, self.vcip, self.token_header)
      # if cluster == 0:

      cluster_id, err = Utilities.check_wcp_cluster_status(self.cluster_id, self.vcip, self.token_header)
      if err != 0:
        logging.error("wcpCluster/"+self.cluster+" failed status check")
        sys.exit(-1)

      if cluster_id == "":
        temp1 = Utilities.get_storage_policy(self.yamldoc["spec"].get("ephemeral_storage_policy"), self.vcip, self.token_header)
        if not temp1:
          logging.error("wcpCluster/" + self.cluster + " check value for ephemeral_storage_policy")
          sys.exit(-1)
        temp2 = Utilities.get_storage_policy(self.yamldoc["spec"].get("master_storage_policy"), self.vcip, self.token_header)
        if not temp2:
          logging.error("wcpCluster/" + self.cluster + " check value for master_storage_policy")
          sys.exit(-1)
        temp3 = Utilities.get_storage_policy(self.yamldoc["spec"]["image_storage"].get("storage_policy"), self.vcip, self.token_header)
        if not temp3:
          logging.error("wcpCluster/" + self.cluster + " check value for storage_policy")
          sys.exit(-1)
        temp4,err = Utilities.get_content_library(self.yamldoc["spec"].get("default_kubernetes_service_content_library"), self.vcip, self.token_header)
        if err != 0:
          logging.error("wcpCluster/{self.cluster} failed to find default content library")
          sys.exit(-1)
        elif not temp4:
          logging.error ("wcpCluster/"+self.cluster+" check value for default_kubernetes_service_content_library")
          sys.exit(-1)
        temp5 = Utilities.get_mgmt_network(self.yamldoc["spec"]["master_management_network"].get("network"), self.datacenter_id, self.vcip, self.token_header)  
        if not temp5:
          logging.error("wcpCluster/" + self.cluster + " check value for master_management_network - network")
          sys.exit(-1)

        #Process for NSX config
        if self.yamldoc["spec"]["network_provider"] == "NSXT_CONTAINER_PLUGIN":
          temp6 = Utilities.get_nsx_switch(self.cluster_id, self.vcip, self.token_header)
          if not temp6:
            logging.error("wcpCluster/" + self.cluster + " no compatiable NSX switch for cluster")
            sys.exit(-1)
          temp7 = Utilities.get_nsx_edge_cluster(self.cluster_id, temp6, self.vcip, self.token_header)
          if not temp7:
            logging.error("wcpCluster/" + self.cluster + " no compatiable NSX edge cluster")
            sys.exit(-1)
          self.yamldoc["spec"]["ncp_cluster_network_spec"].update({"cluster_distributed_switch": temp6})
          self.yamldoc["spec"]["ncp_cluster_network_spec"].update({"nsx_edge_cluster": temp7})

        # Process BYO LB
        else:
          temp6 = Utilities.get_mgmt_network(self.yamldoc["spec"]["workload_networks_spec"]["supervisor_primary_workload_network"]["vsphere_network"].get("portgroup"), self.datacenter_id, self.vcip, self.token_header)
          if not temp6:
            logging.error("wcpCluster/" + self.cluster + " check value for master_management_network - network")
            sys.exit(-1)
          self.yamldoc["spec"]["workload_networks_spec"]["supervisor_primary_workload_network"]["vsphere_network"].update({"portgroup": temp6})

          # Update ...if any of the above is 0 then quit
          self.yamldoc["spec"].update({"ephemeral_storage_policy": temp1})
          self.yamldoc["spec"].update({"master_storage_policy": temp2})
          self.yamldoc["spec"]["image_storage"].update({"storage_policy": temp3})
          self.yamldoc["spec"].update({"default_kubernetes_service_content_library": temp4})
          self.yamldoc["spec"]["master_management_network"].update({"network": temp5})

          json_payload = json.loads(json.dumps(self.yamldoc["spec"]))
          json_response = self.session.post('https://'+self.vcip+'/api/vcenter/namespace-management/clusters/'+self.cluster_id+'?action=enable', headers=self.token_header,json=json_payload)
          if json_response.ok:
            logging.info("wcpCluster/" + self.cluster + " creation started")
          else:
            logging.error("wcpCluster/" + self.cluster + " creation failed")
            logging.error(json_response.text)
            sys.exit(-1)
      else:
        url,err = Utilities.check_wcp_cluster_status(self.cluster_id, self.vcip, self.token_header)
        logging.warning(f"wcpCluster/"+self.cluster+" already operational at https://{url}")
  
  def delete(self):
    # delete wcpCluster
    if self.objtype == "wcpCluster":
      logging.info("Found {} type in yaml, proceeding to delete".format(__class__.__name__))

      cluster,err = Utilities.check_wcp_cluster_status(self.cluster_id, self.vcip, self.token_header)
      if err != 0:
        logging.error("wcpCluster/" + self.cluster + " failed status check")
        sys.exit(-1)

      if cluster:
        # Check if you want to delete ???
        json_response = self.session.post('https://'+self.vcip+'/api/vcenter/namespace-management/clusters/'+self.cluster_id+'?action=disable', headers=self.token_header)
        if json_response.ok:
            logging.info("wcpCluster/" + self.cluster + " delete initiated")
        else:
            logging.error("wcpCluster/" + self.cluster + " delete failed")
            logging.error(json_response.text)
            sys.exit(-1)
      else:
        logging.warning("wcpCluster/" + self.cluster + " not operational")

  def apply(self):
    # apply wcpCluster
    if self.objtype == "wcpCluster":
      logging.info("Found {} type in yaml, proceeding to apply".format(__class__.__name__))

      del self.yamldoc["kind"]
      del self.yamldoc["metadata"]

      # not reliable
      # cluster = Utilities.check_wcp_cluster_compatibility(self.cluster_id, self.yamldoc["spec"]["network_provider"], self.skip_compat, self.vcip, self.token_header)
      # if cluster > 0:

      cluster_id,err = Utilities.check_wcp_cluster_status(self.cluster_id, self.vcip, self.token_header)
      if err != 0:
        logging.error("wcpCluster/"+self.cluster+" status failure")
        sys.exit(-1)

      if cluster_id:
        logging.info("WCP Cluster not found, creating...")
        temp1 = Utilities.get_storage_policy(self.yamldoc["spec"].get("ephemeral_storage_policy"), self.vcip, self.token_header)
        temp2 = Utilities.get_storage_policy(self.yamldoc["spec"].get("master_storage_policy"), self.vcip, self.token_header)
        temp3 = Utilities.get_storage_policy(self.yamldoc["spec"]["image_storage"].get("storage_policy"), self.vcip, self.token_header)
        temp4,err = Utilities.get_content_library(self.yamldoc["spec"].get("default_kubernetes_service_content_library"), self.vcip, self.token_header)
        if err != 0:
          logging.error("wcpCluster/{self.cluster} failed to find default content library")
          sys.exit(-1)
        temp5 = Utilities.get_mgmt_network(self.yamldoc["spec"]["master_management_network"].get("network"), self.datacenter_id, self.vcip, self.token_header)  
        if not temp5:
          logging.error("wcpCluster/" + self.cluster + " check value for master_management_network - network")
          sys.exit(-1)

        #Process for NSX config
        if self.yamldoc["spec"]["network_provider"] == "NSXT_CONTAINER_PLUGIN":
          temp6 = Utilities.get_nsx_switch(self.cluster_id, self.vcip, self.token_header)
          if not temp6:
            logging.error("wcpCluster/" + self.cluster + " no compatiable NSX switch for cluster")
            sys.exit(-1)
          temp7 = Utilities.get_nsx_edge_cluster(self.cluster_id, temp6, self.vcip, self.token_header)
          if not temp7:
            logging.error("wcpCluster/" + self.cluster + " no compatiable NSX edge cluster")
            sys.exit(-1)
          self.yamldoc["spec"]["ncp_cluster_network_spec"].update({"cluster_distributed_switch": temp6})
          self.yamldoc["spec"]["ncp_cluster_network_spec"].update({"nsx_edge_cluster": temp7})

        # Process BYO LB
        else:
          temp6 = Utilities.get_mgmt_network(self.yamldoc["spec"]["workload_networks_spec"]["supervisor_primary_workload_network"]["vsphere_network"].get("portgroup"), self.datacenter_id, self.vcip, self.token_header)
          if not temp6:
            logging.error("wcpCluster/" + self.cluster + " check value for master_management_network - network")
            sys.exit(-1)
          self.yamldoc["spec"]["workload_networks_spec"]["supervisor_primary_workload_network"]["vsphere_network"].update({"portgroup": temp6})

        # Update any of the above is 0 then quit
        self.yamldoc["spec"].update({"ephemeral_storage_policy": temp1})
        self.yamldoc["spec"].update({"master_storage_policy": temp2})
        self.yamldoc["spec"]["image_storage"].update({"storage_policy": temp3})
        self.yamldoc["spec"].update({"default_kubernetes_service_content_library": temp4})
        self.yamldoc["spec"]["master_management_network"].update({"network": temp5})

        json_payload = json.loads(json.dumps(self.yamldoc["spec"]))
        json_response = self.session.post('https://'+self.vcip+'/api/vcenter/namespace-management/clusters/'+self.cluster_id+'?action=enable', headers=self.token_header,json=json_payload)
        if json_response.ok:
          logging.info("wcpCluster/" + self.cluster + " creation started")
        else:
          logging.error("wcpCluster/" + self.cluster + " creation failed")
          logging.error(json_response.text)
          sys.exit(-1)
      else:
        logging.warning ("wcpCluster/"+self.cluster+" already operational at https://"+Utilities.check_wcp_cluster_status(self.cluster_id), self.vcip)


      # TO DO : stub to patch server
      #   json_response = s.patch('https://'+self.vcip+'/api/vcenter/namespace-management/clusters/'+self.cluster_id, headers=self.token_header,json=json_payload)
      #   if json_response.ok:
      #       print ("wcpCluster/"+cluster+" updated")
      #   else:
      #       print ("wcpCluster/"+cluster+" update failed")
      #       print (json_response.text)

      # To rotate password
      #   json_response = s.post('https://'+self.vcip+'/api/vcenter/namespace-management/clusters/'+self.cluster_id+'?action=rotate_password')
      #   if json_response.ok:
      #       print ("wcpCluster/"+cluster+" password rotated")
      #   else:
      #       print ("wcpCluster/"+cluster+" password rotation failed")
      #       print (json_response.text)

  def describe(self):
    # describe wcpCluster
    if self.objtype == "wcpCluster":
      logging.info(f"Found {__class__.__name__} type in request, proceeding to describe")

      cluster_name, err = Utilities.get_wcp_cluster_id(self.args.name, self.vcip, self.token_header)
      if err != 0:
        logging.error("wcpCluster/" + self.args.name + " could not be found")
        sys.exit(-1)

      cluster_id,err = Utilities.check_wcp_cluster_status(cluster_name, self.vcip, self.token_header)
      if err != 0:
        logging.error("wcpCluster/" + self.args.name + " failed status check")
        sys.exit(-1)
        
      if cluster_id:
        json_response = self.session.get('https://'+self.vcip+'/api/vcenter/namespace-management/clusters/'+cluster_name, headers=self.token_header)
        if json_response.ok:
          result = json.loads(json_response.text)
          logging.info(json.dumps(result, indent=2, sort_keys=True))
          print(json.dumps(result, indent=2, sort_keys=True))
        else:
          logging.error("wcpCluster/" + self.args.name + " describe failed")
          logging.error(json_response.text)
          sys.exit(-1)
      elif cluster_id == "":
        logging.warning("wcpCluster/" + self.args.name+ " not ready")