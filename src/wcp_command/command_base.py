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

class CommandBase:

  # constructor to handle the common values
  def __init__(self, args, yamldoc, token_header, cluster_id, skip_compat, datacenter_id, session: requests.session, vcip, objtype):
    # get params
    self.args = args
    self.yamldoc = yamldoc
    self.token_header = token_header
    self.cluster_id = cluster_id
    self.skip_compat = skip_compat
    self.datacenter_id = datacenter_id
    self.session = session
    self.vcip = vcip
    self.objtype = objtype

    # get derived objects
    if (args.verb != 'describe'):
      self.datacenter = self.yamldoc["metadata"]["datacenter"]
      self.cluster = self.yamldoc["metadata"]["cluster"]
      self.spec = self.yamldoc["spec"]

  def create(self):
    raise ImplementationError("This method is not currently implemented!")
  def delete(self):
    raise ImplementationError("This method is not currently implemented!")
  def apply(self):
    raise ImplementationError("This method is not currently implemented!")
  def describe(self):
    raise ImplementationError("This method is not currently implemented!")

class ImplementationError(ValueError):
    pass