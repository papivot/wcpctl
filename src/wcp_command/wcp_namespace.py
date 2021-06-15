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

class wcpNamespace(CommandBase): # class name is looked up dynamically

  def create(self):
    # create wcpNamespace
    if self.objtype == "wcpNamespace":
      logging.info("Found {} type in yaml, proceeding to create".format(__class__.__name__))

      namespace_id = Utilities.check_wcp_ns_status(self.spec["namespace"], self.vcip, self.token_header)
      if namespace_id == 0:
        self.spec.update({"cluster": self.cluster_id})

        i = 0
        # Update variables and proceed
        for sp in self.spec["storage_specs"]:
          temp1 = Utilities.get_storage_policy(sp["policy"], self.vcip, self.token_header)
          if temp1:
            self.spec["storage_specs"][i].update({"policy": temp1})
          else:
            logging.error("wcpNamespace/" + self.spec["namespace"] + " invalid storage policy specified")
            sys.exit(-1)
          i = i + 1

        json_payload = json.loads(json.dumps(self.spec))
        json_response = self.session.post('https://'+self.vcip+'/api/vcenter/namespaces/instances',headers=self.token_header,json=json_payload)
        if json_response.ok:
          logging.info("wcpNamespace/" + self.spec["namespace"] + " created")
        else:
          logging.error("wcpNamespace/" + self.spec["namespace"] + " creation failed")
          logging.error(json_response.text)
      elif namespace_id > 0:
        logging.warning("wcpNamespace/" + self.spec["namespace"] + " already exists. No changes made")
      else:
        logging.error("wcpNamespace failed to create")
        sys.exit(-1)

  def delete(self):
    # delete wcpNamespace
    if self.objtype == "wcpNamespace":
      logging.info("Found {} type in yaml, proceeding to delete".format(__class__.__name__))

      json_response = self.session.delete('https://' + self.vcip + '/api/vcenter/namespaces/instances/' + self.spec["namespace"], headers=self.token_header)
      if (json_response.ok):
        logging.info("wcpNamespace/" + self.spec["namespace"] + " deleted")
      else:
        logging.error("wcpNamespace/" + self.spec["namespace"] + " deletion failed")
        logging.error(json_response.text)
        sys.exit(-1)

  def apply(self):
    # apply wcpNamespace
    if self.objtype == "wcpNamespace":
      logging.info("Found {} type in yaml, proceeding to apply".format(__class__.__name__))

      namespace_id = Utilities.check_wcp_ns_status(self.spec["namespace"], self.vcip, self.token_header)
      if namespace_id > 0:
        self.spec.update({"cluster": self.cluster_id})
        logging.info("Found namespace, will attempt to update")
        i = 0
        # Update variables and proceed
        for sp in self.spec["storage_specs"]:
          temp1 = Utilities.get_storage_policy(sp["policy"], self.vcip, self.token_header)
          if temp1:
            self.spec["storage_specs"][i].update({"policy": temp1})
          else:
            logging.error("wcpNamespace/" + self.spec["namespace"] + " invalid storage policy specified")
            sys.exit(-1)
          i = i + 1

        json_payload = json.loads(json.dumps(self.spec))
        json_response = self.session.put('https://'+self.vcip+'/api/vcenter/namespaces/instances/'+self.spec["namespace"],headers=self.token_header,json=json_payload)
        if json_response.ok:
          logging.info("wcpNamespace/" + self.spec["namespace"] + " updated")
        else:
          logging.error("wcpNamespace/" + self.spec["namespace"] + " update failed")
          logging.error(json_response.text)
      elif namespace_id == 0:
        self.spec.update({"cluster": self.cluster_id})
        logging.info("Did not find namespace, will attempt to create")

        i = 0
        # Update variables and proceed
        for sp in self.spec["storage_specs"]:
          temp1 = Utilities.get_storage_policy(sp["policy"], self.vcip, self.token_header)
          if temp1:
            self.spec["storage_specs"][i].update({"policy": temp1})
          else:
            logging.error("wcpNamespace/" + self.spec["namespace"] + " invalid storage policy specified")
            sys.exit(-1)
          i = i + 1

        json_payload = json.loads(json.dumps(self.spec))
        json_response = self.session.post('https://'+self.vcip+'/api/vcenter/namespaces/instances',headers=self.token_header,json=json_payload)
        if json_response.ok:
          logging.info("wcpNamespace/" + self.spec["namespace"] + " created")
        else:
          logging.error("wcpNamespace/" + self.spec["namespace"] + " creation failed")
          logging.error(json_response.text)
          sys.exit(-1)
      else:
        logging.error("Failed to get status on wcpNamespace/{}".format(self.spec["namespace"]))

  def describe(self):
    # describe wcpNamespace
    if self.objtype == "wcpNamespace":
      logging.info("Found {} type in yaml, proceeding to describe".format(__class__.__name__))

      json_response = self.session.get('https://' + self.vcip + '/api/vcenter/namespaces/instances',headers=self.token_header)
      if (json_response.ok):
        results = json.loads(json_response.text)
        for result in results:
          if result["cluster"] == self.cluster_id:
            json_response = self.session.get('https://'+self.vcip+'/api/vcenter/namespaces/instances/'+result["namespace"],headers=self.token_header)
            if (json_response.ok):
              nsresult = json.loads(json_response.text)
              logging.info(json.dumps(nsresult, indent=2, sort_keys=True))
            else:
              logging.error("wcpNamespace" + result["namespace"] + " error describing")
      else:
        logging.error("wcpNamespace error describing: {} code: {}".format(self.spec["namespace"], json_response.status_code))
        logging.error("wcpNamespace error response: {}".format(json_response.raw))
        sys.exit(-1)