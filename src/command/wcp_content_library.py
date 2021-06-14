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

from command.command_base import CommandBase
import json
import logging
import sys
from wcp_utility import *
from command.command_base import CommandBase

class wcpContentLibrary(CommandBase): # class name is looked up dynamically

  def create(self):
    # create wcpContentLibrary
    if self.objtype == "wcpContentLibrary":
      if not Utilities.get_content_library(self.yamldoc["spec"].get("name"), self.vcip):
        del self.yamldoc["kind"]
        del self.yamldoc["metadata"]
        client_token = Utilities.generate_random_uuid()
        self.yamldoc.update({"client_token": client_token})
        i = 0
        for sb in self.yamldoc["spec"]["storage_backings"]:
          temp1 = Utilities.get_storage_id(sb["datastore_id"], self.datacenter_id, self.vcip)
          if temp1:
            self.yamldoc["spec"]["storage_backings"][i].update({"datastore_id": temp1})
          else:
            logging.error("wcpContentLibrary invalid storage name specified")
            sys.exit()
          i = i + 1
        self.yamldoc["create_spec"] = self.yamldoc.pop("spec")
        json_payload = json.loads(json.dumps(self.yamldoc))
        self.headers.update({'vmware-api-session-id': self.token})
        json_response = self.session.post('https://'+self.vcip+'/rest/com/vmware/content/subscribed-library',headers=self.headers,json=json_payload)
        if json_response.ok:
          logging.info("wcpContentLibrary/Subscribed_library created")
        else:
          logging.info("wcpContentLibrary/Subscribed_library created")
          logging.info(json_response.text)
      else:
        logging.info("wcpContentLibrary/Subscribed_library already running")

  def delete(self):
    # delete wcpContentLibrary
    if self.objtype == "wcpContentLibrary":
      contentlibrary_id = Utilities.get_content_library(self.yamldoc["spec"].get("name"), self.vcip)
      if contentlibrary_id:
        json_response = self.session.delete('https://'+self.vcip+'/rest/com/vmware/content/subscribed-library/id:'+contentlibrary_id)
        if (json_response.ok):
          logging.info("wcpContentLibrary/Subscribed_library successfully deleted")
        else:
          logging.error("wcpContentLibrary/Subscribed_library deletion failed")
          result = json.loads(json_response.text)
          logging.error(json.dumps(result, indent=2, sort_keys=True))
      else:
        logging.warning("wcpContentLibrary/Subscribed library not found")

  def apply(self):
    # apply wcpContentLibrary
    if self.objtype == "wcpContentLibrary":
      if not Utilities.get_content_library(self.yamldoc["spec"].get("name"), self.vcip):
        del self.yamldoc["kind"]
        del self.yamldoc["metadata"]
        client_token = Utilities.generate_random_uuid()
        self.yamldoc.update({"client_token": client_token})
        i = 0
        for sb in self.yamldoc["spec"]["storage_backings"]:
          temp1 = Utilities.get_storage_id(sb["datastore_id"], self.datacenter_id, self.vcip)
          if temp1:
            self.yamldoc["spec"]["storage_backings"][i].update({"datastore_id": temp1})
          else:
            logging.error("wcpContentLibrary invalid storage name specified")
            sys.exit()
          i = i + 1
        self.yamldoc["create_spec"] = self.yamldoc.pop("spec")
        json_payload = json.loads(json.dumps(self.yamldoc))
        json_response = self.session.post('https://'+self.vcip+'/rest/com/vmware/content/subscribed-library',headers=self.token_header,json=json_payload)
        if json_response.ok:
          logging.info("wcpContentLibrary/Subscribed_library created")
        else:
          logging.info("wcpContentLibrary/Subscribed_library created")
          logging.info(json_response.text)
      else:
        logging.warning("wcpContentLibrary/Subscribed_library already running")

  def describe(self):
    # describe wcpContentLibrary
    if self.objtype == "wcpContentLibrary":
      contentlibrary_id = Utilities.get_content_library(self.yamldoc["spec"].get("name"), self.vcip)
      if contentlibrary_id:
        json_response = self.session.get('https://'+self.vcip+'/rest/com/vmware/content/subscribed-library/id:'+contentlibrary_id)
        if (json_response.ok):
          result = json.loads(json_response.text)
          logging.info(json.dumps(result, indent=2, sort_keys=True))
        else:
          logging.error("wcpContentLibrary/Subscribed library error describing")
      else:
        logging.warning("wcpContentLibrary/Subscribed library not found")