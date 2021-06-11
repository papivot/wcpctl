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
import time
from src.utility.utilities import Utilities

class wcpRegistry: # class name is looked up dynamically
  def __init__(self, args, yamldoc, token_header, cluster_id, skip_compat, datacenter_id):
    # get params
    self.args = args
    self.yamldoc = yamldoc
    self.token_header = token_header
    self.cluster_id = cluster_id
    self.skip_compat = skip_compat
    self.datacenter_id = datacenter_id

    # get derived objects
    self.objtype = self.yamldoc["kind"]
    self.vcip = self.yamldoc["metadata"]["vcenter"]
    self.datacenter = self.yamldoc["metadata"]["datacenter"]
    self.cluster = self.yamldoc["metadata"]["cluster"]
    self.spec = self.yamldoc["spec"]
    self.session = "Global"
    self.session = requests.Session()
    self.session.verify = False

  def create(self):
    # create wcpRegistry
    if self.objtype == "wcpRegistry":
      if not Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip):
        del self.yamldoc["kind"]
        del self.yamldoc["metadata"]
        client_token = Utilities.generate_random_uuid()
        self.yamldoc.update({"client_token": client_token})
        self.yamldoc["spec"].update({"cluster": self.cluster_id})
        reg_creation_started = 0
        i = 0
        # Update variables and proceed
        for sp in self.yamldoc["spec"]["storage"]:
          temp1 = Utilities.get_storage_policy(sp["policy"], self.vcip)
          if temp1:
            self.yamldoc["spec"]["storage"][i].update({"policy": temp1})
          else:
            logging.error("wcpNamespace/" + self.spec["namespace"] + " invalid storage policy specified")
            sys.exit()
          i = i + 1
        json_payload = json.loads(json.dumps(self.yamldoc))
        self.headers.update({'vmware-api-session-id': self.token})
        json_response = self.session.post('https://'+self.vcip+'/rest/vcenter/content/registries/harbor',headers=self.headers,json=json_payload)
        if json_response.ok:
          logging.info("wcpRegistry/Harbor creation started")
          reg_creation_started = 1
        else:
          logging.error("wcpRegistry/Harbor failed")
          logging.error(json_response.text)

        if reg_creation_started == 1:
          while not Utilities.check_wcp_harbor_ui_url_status(self.cluster_id, self.vcip):
            logging.info("Sleeping for 20 sec...")
            time.sleep(20)
        print("wcpRegistry/Harbor access URL " + Utilities.check_wcp_harbor_ui_url_status(self.cluster_id), self.vcip)
      else:
        print("wcpRegistry/Harbor already running")
  
  def delete(self):
    # delete wcpRegistry
    if self.objtype == "wcpRegistry":
      reg_destruction_started = 0
      harbor_id = Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip)
      if harbor_id:
        json_response = self.session.delete('https://'+self.vcip+'/rest/vcenter/content/registries/harbor/'+harbor_id, headers=self.token_header)
        if (json_response.ok):
          logging.info("wcpRegistry/Harbor deletion started")
          reg_destruction_started = 1
        else:
          logging.error("wcpRegistry/Harbor deletion failed")
          logging.error(json_response.text)

        if reg_destruction_started == 1:
          while Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip):
            logging.info("Sleeping for 20 sec...")
            time.sleep(20)
      else:
        logging.warning("wcpRegistry/Harbor not found")

  def apply(self):
    # apply wcpRegistry
      if self.objtype == "wcpRegistry":
        # same as create as no modify option
        if not Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip):
          del self.yamldoc["kind"]
          del self.yamldoc["metadata"]
          client_token = Utilities.generate_random_uuid()
          self.yamldoc.update({"client_token": client_token})
          self.yamldoc["spec"].update({"cluster": self.cluster_id})
          i = 0
          # Update variables and proceed
          for sp in self.yamldoc["spec"]["storage"]:
            temp1 = Utilities.get_storage_policy(sp["policy"], self.vcip)
            if temp1:
              self.yamldoc["spec"]["storage"][i].update({"policy": temp1})
            else:
              logging.error("wcpNamespace/" + self.spec["namespace"] + " invalid storage policy specified")
              sys.exit()
            i = i + 1
          json_payload = json.loads(json.dumps(self.yamldoc))
          json_response = self.session.post('https://'+self.vcip+'/rest/vcenter/content/registries/harbor',headers=self.token_header,json=json_payload)
          if json_response.ok:
            logging.info("wcpRegistry/Harbor created")
            reg_creation_started = 1
          else:
            logging.error("wcpRegistry/Harbor failed")
            logging.error(json_response.text)

          if reg_creation_started == 1:
            while not Utilities.check_wcp_harbor_ui_url_status(self.cluster_id, self.vcip):
              logging.info("Sleeping for 20 sec...")
              time.sleep(20)
          logging.info("wcpRegistry/Harbor access URL " + Utilities.check_wcp_harbor_ui_url_status(self.cluster_id), self.vcip)
        else:
          logging.warning("wcpRegistry/Harbor already running")

  def describe(self):
    # describe wcpRegistry
    if self.objtype == "wcpRegistry":
      harbor_id = Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip)
      if harbor_id:
        json_response = self.session.get('https://' + self.vcip + '/rest/vcenter/content/registries/harbor/' + harbor_id)
        if (json_response.ok):
          result = json.loads(json_response.text)
          logging.info(json.dumps(result, indent=2, sort_keys=True))
        else:
          logging.error("wcpRegistry/Harbor error describing")
      else:
        logging.warning("wcpRegistry/Harbor not found")