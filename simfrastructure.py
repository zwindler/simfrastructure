# -*- coding: utf-8 -*-
import sys
"""import getopt
import configparser"""

class sim_datacenter:
  """A datacenter that can contain racks"""
  rack_max = None
  racks = []
  
  def __init__(self, name):
    self.name = name

  """Set maximum number of racks in DC"""
  def set_rack_max(self, rack_max):
    self.rack_max = rack_max

  def add_rack(self, rack):
    if (not isinstance(rack, sim_rack)):
      return rack.name+" is not a rack!"
    if ( self.rack_max == None or len(racks) < self.rack_max ):
      self.racks = [rack]
    else:
      return self.name+" is full, can't add rack!"

  def __str__(self):
    output = "-Datacenter "+self.name+"\n"
    output += "  Datacenter size: "+str(self.rack_max)+"\n"
    output += "  Racks in this datacenter: \n"
    for rack in self.racks:
      output += str(rack)
    return output
  
class sim_rack:
  """A rack that can contain servers"""
  rack_size = 42
  servers = []
  
  def __init__(self, name):
    self.name = name

  """Set maximum number of servers units in rack"""
  def set_rack_size(self, rack_size):
    self.rack_size = rack_size

  def get_rack_usage(self):
    rack_usage = 0
    for server in self.servers:
      rack_usage += server.server_size
    return rack_usage

  def add_server(self, server):
    if (not isinstance(server, sim_server)):
      return server.name+" is not a server!"
    rack_usage = self.get_rack_usage()
    if ( self.rack_size == None or rack_usage < self.rack_size):
      self.servers = [server]
    else:
      return self.name+" is full, can't add server!"

  def __str__(self):
    output = "    +"+self.name+"\n"
    output += "      Rack usage: "+str(self.get_rack_usage())+"/"+str(self.rack_size)+"U\n"
    output += "      Servers in this rack: \n"
    for server in self.servers:
      output += str(server)
    return output

class sim_server:
  """A 2U server that may run containers or virtual machines or both"""
  server_size = 2
  vcpu_max_capacity = None
  ram_max_capacity = None
  can_run_vms = False
  vms = None
  can_run_containers = False
  containers = None
  
  def __init__(self, name):
    self.name = name

  """Set the ability to run VMs"""
  def set_server_can_run_vms(self, can_run_vms):
    self.can_run_vms = can_run_vms

  """Set the ability to run containers"""
  def set_server_can_run_containers(self, can_run_containers):
    self.can_run_containers = can_run_containers   

  """Set the vCPU limit on server"""
  def set_vcpu_max_capacity(self, vcpu_max_capacity):
    self.vcpu_max_capacity = vcpu_max_capacity

  """Set the RAM limit on server"""
  def set_ram_max_capacity(self, ram_max_capacity):
    self.ram_max_capacity = ram_max_capacity

  def get_server_usage(self):
    server_usage = {"vcpu" : 0, "ram" : 0}
    if self.vms or self.containers:
      for logical_object in self.vms + self.containers:
        server_usage["vcpu"] += logical_object.vcpu_alloc
        server_usage["ram"] += logical_object.gigabytes_ram_alloc
    return server_usage

  def __str__(self):
    output ="        *"+self.name+"\n"
    output += "          Server size : "+str(self.server_size)+"U\n"
    if self.vcpu_max_capacity:
      output += "          Server vCPU usage: "+str(self.get_server_usage()["vcpu"])+"/"+str(self.vcpu_max_capacity)+" vCPU\n"
    if self.ram_max_capacity:
      output += "          Server RAM usage: "+str(self.get_server_usage()["ram"])+"/"+str(self.ram_max_capacity)+" GB RAM\n"
    if self.can_run_vms:
      output += "          Can run VMs\n"
    if (self.vms):
      for vm in self.vms:
        output += str(vm)+"\n"
    if (self.can_run_containers):
      output += "          Can run containers\n"
    if (self.containers):
      for container in self.containers:
        output += str(container)+"\n"
    return output

class sim_logical_object:
  vcpu_alloc = None
  gigabytes_ram_alloc = None

  """Allocate vm or container in a specified DC"""
  def add_logical_object_in_dc(self, dc):
    print("TODO")

  """Force VM or container allocation on a specified server"""
  def add_logical_object_on_server(server):
    print("TODO")

  def __init__(self, name, vcpu_alloc, gigabytes_ram_alloc):
    self.name = name
    self.vcpu_alloc = vcpu_alloc
    self.gigabytes_ram_alloc = gigabytes_ram_alloc

  def __str__(self):
    output ="      VM name: "+self.name+"\n"
    
class sim_vm(sim_logical_object):
  """A VM on a server that can execute VMs"""
  can_run_containers = False
  containers = None

  """Set the ability to run containers"""
  def set_vm_can_run_containers(self, can_run_containers):
    self.can_run_containers = can_run_containers   
     
  def __str__(self):
    output ="      VM name: "+self.name+"\n"
    if (self.containers):
      for container in self.containers:
        output += str(container)+"\n"
    return output

class sim_container(sim_logical_object):
  """A container on a server that can execute containers"""
  
  """Force container allocation on a specified VM"""
  def add_container_on_vm(vm):
    print("TODO")

def init_infrastructure():
  dc1 = sim_datacenter("dc1")
  dc2 = sim_datacenter("dc2")

  rack1 = sim_rack("dc1_rack1")
  dc1.add_rack(rack1)
  rack2 = sim_rack("dc2_rack2")
  dc2.add_rack(rack2)

  srv1 = sim_server("dc1_rack1_srv1")
  srv1.set_server_can_run_vms(True)
  """Server with 2 sockets, 14 cores each socket, 4 vCPU each core"""
  srv1.set_vcpu_max_capacity(2*14*4)
  """Server with 12 sticks of 16GB of RAM"""
  srv1.set_ram_max_capacity(12*16)
  rack1.add_server(srv1)
  srv2 = sim_server("dc2_rack2_srv2")
  srv2.set_server_can_run_vms(True)
  rack2.add_server(srv2)

  vm1 = sim_vm("dc1_vm1", 2, 4)
  vm1.add_logical_object_in_dc(dc1)
  cont1 = sim_container("dc1_cont1", 1, 1)
  cont1.add_logical_object_in_dc(dc1)
  
  print(dc1)
  
def usage():
  return ''

def main():
  """#default, can be overriden  
  config_file_path = 'example.cfg'

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'c:h', ['config=', 'help'])
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  for o, a in opts:
    if o in ('-c', '--config'):
      config_file_path = a
    if o in ('-h', '--help'):
      usage()

  config = configparser.RawConfigParser()
  config.read(config_file_path)
  test = [config.get('Test', 'Test_output')]"""

  init_infrastructure()
  
  sys.exit()

if __name__ == '__main__':
  main()
