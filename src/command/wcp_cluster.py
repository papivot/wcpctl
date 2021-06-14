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

import requests
import json
import logging
import sys
from wcp_utility import *
from command.command_base import CommandBase

class wcpCluster(CommandBase): # class name is looked up dynamically
  
  def create(self):
    # create wcpCluster
    if self.objtype == "wcpCluster":
      del self.yamldoc["kind"]
      del self.yamldoc["metadata"]
      if Utilities.check_wcp_cluster_compatibility(self.cluster_id, self.yamldoc["spec"]["network_provider"], self.skip_compat, self.vcip):
        if not Utilities.check_wcp_cluster_status(self.cluster_id):

          temp1 = Utilities.get_storage_policy(self.yamldoc["spec"].get("ephemeral_storage_policy"), self.vcip)
          if not temp1:
            logging.error("wcpCluster/" + self.cluster + " check value for ephemeral_storage_policy")
            sys.exit()
          temp2 = Utilities.get_storage_policy(self.yamldoc["spec"].get("master_storage_policy"), self.vcip)
          if not temp2:
            logging.error("wcpCluster/" + self.cluster + " check value for master_storage_policy")
            sys.exit()
          temp3 = Utilities.get_storage_policy(self.yamldoc["spec"]["image_storage"].get("storage_policy"), self.vcip)
          if not temp3:
            logging.error("wcpCluster/" + self.cluster + " check value for storage_policy")
            sys.exit()
          temp4 = Utilities.get_content_library(self.yamldoc["spec"].get("default_kubernetes_service_content_library"), self.vcip)
          if not temp4:
            logging.error ("wcpCluster/"+self.cluster+" check value for default_kubernetes_service_content_library")
            sys.exit()
          temp5 = Utilities.get_mgmt_network(self.yamldoc["spec"]["master_management_network"].get("network"), self.datacenter_id, self.vcip)  
          if not temp5:
            logging.error("wcpCluster/" + self.cluster + " check value for master_management_network - network")
            sys.exit()

          #Process for NSX config
          if self.yamldoc["spec"]["network_provider"] == "NSXT_CONTAINER_PLUGIN":
            temp6 = Utilities.get_nsx_switch(self.cluster_id, self.vcip)
            if not temp6:
              logging.error("wcpCluster/" + self.cluster + " no compatiable NSX switch for cluster")
              sys.exit()
            temp7 = Utilities.get_nsx_edge_cluster(self.cluster_id, temp6, self.vcip)
            if not temp7:
              logging.error("wcpCluster/" + self.cluster + " no compatiable NSX edge cluster")
              sys.exit()
            self.yamldoc["spec"]["ncp_cluster_network_spec"].update({"cluster_distributed_switch": temp6})
            self.yamldoc["spec"]["ncp_cluster_network_spec"].update({"nsx_edge_cluster": temp7})

          # Process BYO LB
          else:
            temp6 = Utilities.get_mgmt_network(self.yamldoc["spec"]["workload_networks_spec"]["supervisor_primary_workload_network"]["vsphere_network"].get("portgroup"), self.datacenter_id, self.vcip)
            if not temp6:
              logging.error("wcpCluster/" + self.cluster + " check value for master_management_network - network")
              sys.exit()
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
        else:
          logging.warning("wcpCluster/"+self.cluster+" already operational at https://"+Utilities.check_wcp_cluster_status(self.cluster_id, self.vcip))
      else:
        logging.warning("wcpCluster/" + self.cluster + " not compatiable")
  
  def delete(self):
    # delete wcpCluster
    if self.objtype == "wcpCluster":
      if Utilities.check_wcp_cluster_status(self.cluster_id, self.vcip):
        # Check if you want to delete ???
        json_response = self.session.post('https://'+self.vcip+'/api/vcenter/namespace-management/clusters/'+self.cluster_id+'?action=disable')
        if json_response.ok:
            logging.info("wcpCluster/" + self.cluster + " delete initiated")
        else:
            logging.error("wcpCluster/" + self.cluster + " delete failed")
            logging.error(json_response.text)
      else:
        logging.warning("wcpCluster/" + self.cluster + " not operational")

  def apply(self):
    # apply wcpCluster
    if self.objtype == "wcpCluster":
      del self.yamldoc["kind"]
      del self.yamldoc["metadata"]
      if Utilities.check_wcp_cluster_compatibility(self.cluster_id, self.yamldoc["spec"]["network_provider"], self.skip_compat, self.vcip):
        if not Utilities.check_wcp_cluster_status(self.cluster_id, self.vcip):

          temp1 = Utilities.get_storage_policy(self.yamldoc["spec"].get("ephemeral_storage_policy"), self.vcip)
          temp2 = Utilities.get_storage_policy(self.yamldoc["spec"].get("master_storage_policy"), self.vcip)
          temp3 = Utilities.get_storage_policy(self.yamldoc["spec"]["image_storage"].get("storage_policy"), self.vcip)
          temp4 = Utilities.get_content_library(self.yamldoc["spec"].get("default_kubernetes_service_content_library"), self.vcip)
          temp5 = Utilities.get_mgmt_network(self.yamldoc["spec"]["master_management_network"].get("network"), self.datacenter_id, self.vcip)  
          if not temp5:
            logging.error("wcpCluster/" + self.cluster + " check value for master_management_network - network")
            sys.exit()

          #Process for NSX config
          if self.yamldoc["spec"]["network_provider"] == "NSXT_CONTAINER_PLUGIN":
            temp6 = Utilities.get_nsx_switch(self.cluster_id, self.vcip)
            if not temp6:
              logging.error("wcpCluster/" + self.cluster + " no compatiable NSX switch for cluster")
              sys.exit()
            temp7 = Utilities.get_nsx_edge_cluster(self.cluster_id, temp6, self.vcip)
            if not temp7:
              logging.error("wcpCluster/" + self.cluster + " no compatiable NSX edge cluster")
              sys.exit()
            self.yamldoc["spec"]["ncp_cluster_network_spec"].update({"cluster_distributed_switch": temp6})
            self.yamldoc["spec"]["ncp_cluster_network_spec"].update({"nsx_edge_cluster": temp7})

          # Process BYO LB
          else:
            temp6 = Utilities.get_mgmt_network(self.yamldoc["spec"]["workload_networks_spec"]["supervisor_primary_workload_network"]["vsphere_network"].get("portgroup"), self.datacenter_id, self.vcip)
            if not temp6:
              logging.error("wcpCluster/" + self.cluster + " check value for master_management_network - network")
              sys.exit()
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
        else:
          logging.warning ("wcpCluster/"+self.cluster+" already operational at https://"+Utilities.check_wcp_cluster_status(self.cluster_id), self.vcip)
      else:
        logging.warning("wcpCluster/" + self.cluster + " not compatiable")

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
      if Utilities.check_wcp_cluster_status(self.cluster_id, self.vcip):
        json_response = self.session.get('https://'+self.vcip+'/api/vcenter/namespace-management/clusters/'+self.cluster_id)
        if json_response.ok:
          result = json.loads(json_response.text)
          logging.info(json.dumps(result, indent=2, sort_keys=True))
        else:
          logging.error("wcpCluster/" + self.cluster + " error describing")
      else:
        logging.warning("wcpCluster/" + self.cluster + " not ready")