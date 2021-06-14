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

import importlib
import requests
import json
import os
import logging
import sys
import getpass
import time
import types
import inspect
from src.utility.utilities import Utilities
import src.command

class Command:

  def __init__(self, args, yamldoc):
    # get params
    self.args = args
    self.yamldoc = yamldoc

    # get derived objects
    self.objtype = self.yamldoc["kind"]
    self.vcip = self.yamldoc["metadata"]["vcenter"]
    self.datacenter = self.yamldoc["metadata"]["datacenter"]
    self.cluster = self.yamldoc["metadata"]["cluster"]
    self.spec = self.yamldoc["spec"]
    self.session = requests.Session()
    self.session.verify = False

    # get optionals and environmentals
    if args.userid:
      self.userid = args.userid
    else:
      if not os.environ.get('WCP_USERNAME'):
        self.userid = "administrator@vsphere.local"
      else:
        self.userid = os.environ.get('WCP_USERNAME')

    if not os.environ.get('WCP_PASSWORD'):
      self.password = getpass.getpass(prompt='Password: ')
    else:
      self.password = os.environ.get('WCP_PASSWORD')

    if not os.environ.get('SKIP_COMPAT_CHECK'):
      self.skip_compat = False
    else:
      self.skip_compat = True

    # skip the following if this is a test command
    if self.objtype.find("test") != 0-1:
      self.token_header = {'vmware-api-session-id': 'test'}
      self.datacenter_id = "test"
      self.cluster_id = "test"
      return

    # Connect to VCenter and start a session
    vcsession = self.session.post('https://' + self.vcip + '/rest/com/vmware/cis/session', auth=(self.userid, self.password))
    if not vcsession.ok:
      logging.error("Session creation is failed, please check vcenter connection")
      sys.exit()
    self.session_token = json.loads(vcsession.text)["value"]
    self.token_header = {'vmware-api-session-id': self.session_token}

    # Based on the datacenter get all datacenters
    datacenter_object = self.session.get('https://' + self.vcip + '/rest/vcenter/datacenter?filter.names=' + self.datacenter)
    if len(json.loads(datacenter_object.text)["value"]) == 0:
      logging.error("No datacenter found, please enter valid datacenter name")
      sys.exit()
    self.datacenter_id = json.loads(datacenter_object.text)["value"][0].get("datacenter")

    # Based on the cluster name get the cluster_id
    cluster_object = self.session.get(
      'https://' + self.vcip + '/rest/vcenter/cluster?filter.names=' + self.cluster + '&filter.datacenters=' + self.datacenter_id)
    if len(json.loads(cluster_object.text)["value"]) == 0:
      logging.error("No cluster found, please enter valid cluster name")
      sys.exit()
    self.cluster_id = json.loads(cluster_object.text)["value"][0].get("cluster")

  def __del__(self):
    # Clean up and exit...
    session_delete = self.session.delete('https://' + self.vcip + '/rest/com/vmware/cis/session', auth=(self.userid, self.password))

  def create(self):
    # create instance of the class and call creation method
    module = importlib.import_module("src.command")
    obj_type = getattr(module, self.objtype)
        
    try:
      obj_instance = obj_type(self.args, self.yamldoc, self.token_header, self.cluster_id, self.skip_compat, self.datacenter_id, self.session)
      obj_instance.create()
    except:
      e = sys.exc_info()[0]
      logging.error("There was an error when creating object type: {0} : {1}".format(self.objtype, sys.exc_info()[1]))

  def delete(self):
    # create instance of the class and call creation method
    module = importlib.import_module("src.command")
    obj_type = getattr(module, self.objtype)

    try:
      obj_instance = obj_type(self.args, self.yamldoc, self.token_header, self.cluster_id, self.skip_compat, self.datacenter_id, self.session)
      obj_instance.delete()
    except:
      e = sys.exc_info()[0]
      logging.error("There was an error when deleting object type: {0} : {1}".format(self.objtype, e))

  def apply(self):
    # create instance of the class and call creation method
    module = importlib.import_module("src.command")
    obj_type = getattr(module, self.objtype)

    try:
      obj_instance = obj_type(self.args, self.yamldoc, self.token_header, self.cluster_id, self.skip_compat, self.datacenter_id, self.session)
      obj_instance.apply()
    except:
      e = sys.exc_info()[0]
      logging.error("There was an error when applying object type: {0} : {1}".format(self.objtype, e))
  
  def describe(self):
    # create instance of the class and call creation method
    module = importlib.import_module("src.command")
    obj_type = getattr(module, self.objtype)

    try:
      obj_instance = obj_type(self.args, self.yamldoc, self.token_header, self.cluster_id, self.skip_compat, self.datacenter_id, self.session)
      obj_instance.describe()
    except:
      e = sys.exc_info()[0]
      logging.error("There was an error when describing object type: {0} : {1}".format(self.objtype, e))
  