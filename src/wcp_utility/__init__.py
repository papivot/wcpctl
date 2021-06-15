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
import requests
import uuid
import logging

class Utilities:
  @staticmethod
  def generate_random_uuid():
      return str(uuid.uuid4())

  @staticmethod
  def get_storage_id(storage_name: str, dc: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://'+vcip+'/rest/vcenter/datastore?filter.datacenters='+dc+'&filter.names='+storage_name, headers=token_header)
    if json_response.ok:
      results = json.loads(json_response.text)["value"]
      for result in results:
        if result["name"] == storage_name:
            return result["datastore"]
    else:
      return 0
    return 0

  @staticmethod
  def get_storage_policy(sp_name: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://' + vcip + '/rest/vcenter/storage/policies', headers=token_header)
    if json_response.ok:
      results = json.loads(json_response.text)["value"]
      for result in results:
        if result["name"] == sp_name:
          return result["policy"]
      else:
        return 0
    else:
      return 0

  def get_content_library(cl_name: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://' + vcip + '/rest/com/vmware/content/library', headers=token_header)
    if json_response.ok:
      results = json.loads(json_response.text)["value"]
      for result in results:
        json_response = s.get('https://' + vcip + '/rest/com/vmware/content/library/id:' + result, headers=token_header)
        if json_response.ok:
          cl_library = json.loads(json_response.text)["value"]
          if cl_library["name"] == cl_name:
            return cl_library["id"]
    else:
      return 0
    return 0

  @staticmethod
  def get_nsx_switch(cluster: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://'+vcip+'/api/vcenter/namespace-management/distributed-switch-compatibility?cluster='+cluster+'&compatible=true', headers=token_header)
    if json_response.ok:
      results = json.loads(json_response.text)
      # Making assumption that there is only 1 distributed switch.
      nsx_sw_id = results[0]['distributed_switch']
      return nsx_sw_id
    else:
      return 0

  @staticmethod
  def get_nsx_edge_cluster(cluster: str, dvs: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://'+vcip+'/api/vcenter/namespace-management/edge-cluster-compatibility?cluster='+cluster+'&compatible=true&distributed_switch='+dvs, headers=token_header)
    if json_response.ok:
      results = json.loads(json_response.text)
      edge_id = results[0]['edge_cluster']
      return edge_id
    else:
      return 0

  @staticmethod
  def get_mgmt_network(mgmt_nw_name: str, dc: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://' + vcip + '/rest/vcenter/network?filter.datacenters=' + dc, headers=token_header)
    if json_response.ok:
      results = json.loads(json_response.text)["value"]
      for result in results:
        if result["name"] == mgmt_nw_name:
            return result["network"]
    else:
      return 0
    return 0

  @staticmethod
  def check_wcp_cluster_compatibility(cluster: str, net_p: str , skip_compat: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    if skip_compat:
      return 1
    else:
      json_response = s.get('https://' + vcip + '/api/vcenter/namespace-management/cluster-compatibility?network_provider='+ net_p, headers=token_header)
      if json_response.ok:
        results = json.loads(json_response.text)
        res = next((sub for sub in results if sub['cluster'] == cluster), None)
        if res['compatible'] == True:
          return 1
        else:
          return 0
      else:
        return 0

  @staticmethod
  def check_wcp_cluster_status(cluster: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://' + vcip + '/api/vcenter/namespace-management/clusters/' + cluster, headers=token_header)
    if json_response.ok:
      result = json.loads(json_response.text)
      if result["config_status"] == "RUNNING":
        if result["kubernetes_status"] == "READY":
            return result["api_server_cluster_endpoint"]
      else:
        return 0
    else:
      return 0

  @staticmethod
  def check_wcp_harbor_status(cluster: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    logging.debug("Checking Harbor status")
    json_response = s.get('https://' + vcip + '/rest/vcenter/content/registries/harbor', headers=token_header)
    if json_response.ok:
      logging.debug("Got valid status response")
      results = json.loads(json_response.text)["value"]
      for result in results:
        if result["cluster"] == cluster:
            return result["registry"]
      else:
        logging.debug("Did not find any harbor registries on cluster {}".format(cluster))
        return 0
    else:
      logging.error("Bad REST response code: {}".format(json_response.status_code))
      logging.debug("Bad REST response: {}".format(json_response.raw))
      return -1

  @staticmethod
  def check_wcp_harbor_ui_url_status(cluster: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://' + vcip + '/rest/vcenter/content/registries/harbor', headers=token_header)
    if json_response.ok:
      results = json.loads(json_response.text)["value"]
      for result in results:
        if result["cluster"] == cluster:
            return result["ui_access_url"]
      else:
        return 0
    else:
      return 0

  @staticmethod
  def check_wcp_ns_status(ns_name: str, vcip: str, token_header: str):
    s = requests.Session()
    s.verify = False

    json_response = s.get('https://' + vcip + '/api/vcenter/namespaces/instances/' + ns_name, headers=token_header)
    if json_response.ok:
      result = json.loads(json_response.text)
      if result["config_status"] == "RUNNING":
        return 1
      else:
        return 0
    else:
      return 0