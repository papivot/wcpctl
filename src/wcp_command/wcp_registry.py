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
import time
from wcp_utility import *
from wcp_command.command_base import CommandBase

class wcpRegistry(CommandBase): # class name is looked up dynamically

  def create(self):
    # create wcpRegistry
    if self.objtype == "wcpRegistry":
      logging.info("Found {} type in yaml, proceeding to create".format(__class__.__name__))

      response = Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip, self.token_header)
      if response == 0:
        del self.yamldoc["kind"]
        del self.yamldoc["metadata"]
        client_token = Utilities.generate_random_uuid()
        self.yamldoc.update({"client_token": client_token})
        self.yamldoc["spec"].update({"cluster": self.cluster_id})

        reg_creation_started = 0
        i = 0
        # Update variables and proceed
        for sp in self.yamldoc["spec"]["storage"]:
          temp1 = Utilities.get_storage_policy(sp["policy"], self.vcip, self.token_header)
          if temp1:
            self.yamldoc["spec"]["storage"][i].update({"policy": temp1})
          else:
            logging.error("wcpNamespace/" + self.spec["namespace"] + " invalid storage policy specified")
            sys.exit(-1)
          i = i + 1

        json_payload = json.loads(json.dumps(self.yamldoc))
        json_response = self.session.post('https://'+self.vcip+'/rest/vcenter/content/registries/harbor',headers=self.token_header,json=json_payload)
        if json_response.ok:
          logging.info("wcpRegistry/Harbor creation started")
          reg_creation_started = 1
        else:
          logging.error("wcpRegistry/Harbor failed")
          logging.error(json_response.text)
          sys.exit(-1)

        if reg_creation_started == 1:
          while not Utilities.check_wcp_harbor_ui_url_status(self.cluster_id, self.vcip, self.token_header):
            logging.info("Sleeping for 20 sec...")
            time.sleep(20)
        logging.info("wcpRegistry/Harbor access URL " + Utilities.check_wcp_harbor_ui_url_status(self.cluster_id, self.vcip, self.token_header))
      elif response > 0:
        logging.info("wcpRegistry/Harbor already running")
      else:
        logging.error("Received an invalid error code when checking Harbor status")
        sys.exit(-1)
      
  
  def delete(self):
    # delete wcpRegistry
    if self.objtype == "wcpRegistry":
      logging.info("Found {} type in yaml, proceeding to delete".format(__class__.__name__))

      reg_destruction_started = 0
      harbor_id = Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip, self.token_header)
      if harbor_id > 0:
        logging.info("Found Harbor registry")
        json_response = self.session.delete('https://'+self.vcip+'/rest/vcenter/content/registries/harbor/'+harbor_id, headers=self.token_header)
        if (json_response.ok):
          logging.info("wcpRegistry/Harbor deletion started")
          reg_destruction_started = 1
        else:
          logging.error("wcpRegistry/Harbor deletion failed")
          logging.error(json_response.text)
          sys.exit(-1)

        if reg_destruction_started == 1:
          while Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip, self.token_header): # TODO fix this loop so it exits after a timeout
            logging.info("Sleeping for 20 sec...")
            time.sleep(20)
          logging.info("wcpRegistry/Harbor deleted successfully")
      elif harbor_id == 0:
        logging.warning("wcpRegistry/Harbor not found")
      else:
        logging.error("Error retrieving harbor information")
        sys.exit(-1)

  def apply(self):
    # apply wcpRegistry
      if self.objtype == "wcpRegistry":
        logging.info("Found {} type in yaml, proceeding to apply".format(__class__.__name__))

        # same as create as no modify option
        harbor_id = Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip, self.token_header)
        if harbor_id == 0:
          del self.yamldoc["kind"]
          del self.yamldoc["metadata"]
          client_token = Utilities.generate_random_uuid()
          self.yamldoc.update({"client_token": client_token})
          self.yamldoc["spec"].update({"cluster": self.cluster_id})
          
          i = 0
          # Update variables and proceed
          for sp in self.yamldoc["spec"]["storage"]:
            temp1 = Utilities.get_storage_policy(sp["policy"], self.vcip, self.token_header)
            if temp1:
              self.yamldoc["spec"]["storage"][i].update({"policy": temp1})
            else:
              logging.error("wcpNamespace/" + self.spec["namespace"] + " invalid storage policy specified")
              sys.exit(-1)
            i = i + 1

          json_payload = json.loads(json.dumps(self.yamldoc))
          json_response = self.session.post('https://'+self.vcip+'/rest/vcenter/content/registries/harbor',headers=self.token_header,json=json_payload)
          if json_response.ok:
            logging.info("wcpRegistry/Harbor created")
            reg_creation_started = 1
          else:
            logging.error("wcpRegistry/Harbor failed")
            logging.error(json_response.text)
            sys.exit(-1)

          if reg_creation_started == 1:
            # TODO fix this loop too
            while not Utilities.check_wcp_harbor_ui_url_status(self.cluster_id, self.vcip, self.token_header):
              logging.info("Sleeping for 20 sec...")
              time.sleep(20)
            logging.info("wcpRegistry/Harbor applied changes successfully")
          
          logging.info("wcpRegistry/Harbor access URL " + Utilities.check_wcp_harbor_ui_url_status(self.cluster_id, self.vcip, self.token_header))
        elif harbor_id > 0:
          logging.warning("wcpRegistry/Harbor already running")
        else:
          logging.error("wcpRegistry/Harbor status check failed")
          sys.exit(-1)

  def describe(self):
    # describe wcpRegistry
    if self.objtype == "wcpRegistry":
      logging.info("Found {} type in yaml, proceeding to describe".format(__class__.__name__))

      harbor_id = Utilities.check_wcp_harbor_status(self.cluster_id, self.vcip, self.token_header)
      if harbor_id > 0:
        logging.info("Found harbor registry")
        json_response = self.session.get('https://' + self.vcip + '/rest/vcenter/content/registries/harbor/' + harbor_id, headers=self.token_header)
        if (json_response.ok):
          result = json.loads(json_response.text)
          logging.info(json.dumps(result, indent=2, sort_keys=True))
        else:
          logging.error("wcpRegistry/Harbor error describing")
      elif harbor_id == 0:
        logging.warning("wcpRegistry/Harbor not found")
      else: 
        logging.error("wcpRegsitry/Harbor status failed")
        sys.exit(-1)