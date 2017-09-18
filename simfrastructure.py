# -*- coding: utf-8 -*-
import sys
import random
"""import getopt
import configparser"""

class sim_datacenter:
  """A datacenter that can contain racks"""
  def __init__(self, name):
    self.name = name
    self.racks = []
    self.rack_max = None

  """Set maximum number of racks in DC"""
  def set_rack_max(self, rack_max):
    self.rack_max = rack_max

  def add_rack(self, rack):
    if (not isinstance(rack, sim_rack)):
      return rack.name+" is not a rack!"
    if ( self.rack_max == None or len(racks) < self.rack_max ):
      self.racks.append(rack)
    else:
      return self.name+" is full, can't add rack!"

  def find_suitable_host(self, kind, vcpu, ram):
    suitable_objects = []
    for rack in self.racks:
      for server in rack.servers:
        print(server.guests.keys())
        if kind in server.guests.keys():
          usage = server.get_server_usage()
          if usage["vcpu"] + vcpu <= server.vcpu_max_capacity and usage["ram"] + ram <= server.ram_max_capacity:
            suitable_objects.append(server)
        if server.guests["vms"]:
          for vm in server.guests["vms"]:
            if kind in vm.capability:
              print("TODO")
    return random.choice(suitable_objects)

  def __str__(self):
    output = "-Datacenter "+self.name+"\n"
    output += "  Datacenter size: "+str(self.rack_max)+"\n"
    output += "  Racks in this datacenter: \n"
    for rack in self.racks:
      output += str(rack)
    return output
  
class sim_rack:
  """A rack that can contain servers"""  
  def __init__(self, name):
    self.name = name
    self.servers = []
    self.rack_size = 42

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
      self.servers.append(server)
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
  def __init__(self, name):
    self.name = name
    self.capability = []
    self.server_size = 2
    self.vcpu_max_capacity = None
    self.ram_max_capacity = None
    self.guests = {}

  """Set the ability to run VMs or containers"""
  def set_server_capability(self, capabilities):
    for capability in capabilities:
      self.guests[capability] = []

  """Set the vCPU limit on server"""
  def set_vcpu_max_capacity(self, vcpu_max_capacity):
    self.vcpu_max_capacity = vcpu_max_capacity

  """Set the RAM limit on server"""
  def set_ram_max_capacity(self, ram_max_capacity):
    self.ram_max_capacity = ram_max_capacity

  def get_server_usage(self):
    server_usage = {"vcpu" : 0, "ram" : 0}
    for k, v in self.guests.items():
      for logical_object in v:
        server_usage["vcpu"] += logical_object.vcpu_alloc
        server_usage["ram"] += logical_object.gigabytes_ram_alloc
    return server_usage

  def check_server_capability(self, kind, vcpu, ram):
    if kind in self.guests.keys() :
      return True

  def register_logical_object_to_host(self, guest):
    print("TODO")

  def __str__(self):
    output ="        *"+self.name+"\n"
    output += "          Server size : "+str(self.server_size)+"U\n"
    if self.vcpu_max_capacity:
      output += "          Server vCPU usage: "+str(self.get_server_usage()["vcpu"])+"/"+str(self.vcpu_max_capacity)+" vCPU\n"
    if self.ram_max_capacity:
      output += "          Server RAM usage: "+str(self.get_server_usage()["ram"])+"/"+str(self.ram_max_capacity)+" GB RAM\n"
    if "vms" in self.guests.keys():
      output += "          Can run VMs\n"
      for vm in self.guests["vms"]:
        output += str(vm)+"\n"
    if "containers" in self.guests.keys():
      output += "          Can run containers\n"
      for container in self.guests["containers"]:
        output += str(container)+"\n"
    return output

class sim_logical_object:
  """Allocate vm or container in a specified DC"""
  def add_logical_object_in_dc(self, dc):
    host = dc.find_suitable_host(self.kind, self.vcpu_alloc, self.gigabytes_ram_alloc)
    host.register_logical_object_to_host(self)

  def register_logical_object_to_host(self, guest):
    print("TODO")
    
  """Force VM or container allocation on a specified server"""
  def add_logical_object_on_server(self, server):
    print(guest)

  def print_name_cpu_ram(self):
    output ="          %"+self.name+"\n"
    output +="           "+str(self.vcpu_alloc)+"\n"
    output +="           "+str(self.gigabytes_ram_alloc)+"\n"    

  def __init__(self, name, vcpu_alloc, gigabytes_ram_alloc):
    self.name = name
    self.vcpu_alloc = vcpu_alloc
    self.gigabytes_ram_alloc = gigabytes_ram_alloc
    
class sim_vm(sim_logical_object):
  """A VM on a server that can execute VMs"""
  kind = "vms"
  
  """Set the ability to run VMs or containers"""
  def set_vm_capability(self, capability):
    self.capability = capability
     
  def __str__(self):
    output = ""
    self.print_name_cpu_ram()
    if (self.containers):
      for container in self.containers:
        output += str(container)+"\n"
    return output

  def __init__(self, name, vcpu_alloc, gigabytes_ram_alloc):
    self.name = name
    self.vcpu_alloc = vcpu_alloc
    self.gigabytes_ram_alloc = gigabytes_ram_alloc
    self.containers = []
    
class sim_container(sim_logical_object):
  """A container on a server that can execute containers"""
  kind = "containers"

  """Force container allocation on a specified VM"""
  def add_container_on_vm(self, vm):
    print("TODO")

  def __str__(self):
    self.print_name_cpu_ram()
    return output

def init_infrastructure():
  dc1 = sim_datacenter("dc1")
  dc2 = sim_datacenter("dc2")

  rack1 = sim_rack("dc1_rack1")
  dc1.add_rack(rack1)
  rack2 = sim_rack("dc2_rack2")
  dc2.add_rack(rack2)

  srv1 = sim_server("dc1_rack1_srv1")
  srv1.set_server_capability(["vms","containers"])
  """Server with 2 sockets, 14 cores each socket, 4 vCPU each core"""
  srv1.set_vcpu_max_capacity(2*14*4)
  """Server with 12 sticks of 16GB of RAM"""
  srv1.set_ram_max_capacity(12*16)
  rack1.add_server(srv1)
  
  srv2 = sim_server("dc2_rack2_srv2")
  srv2.set_server_capability(["vms"])
  rack2.add_server(srv2)

  srv3 = sim_server("dc1_rack1_srv3")
  srv3.set_server_capability(["vms"])
  """Server with 1 sockets, 1 cores each socket, 4 vCPU each core"""
  srv3.set_vcpu_max_capacity(1*1*4)
  """Server with 1 stick of 16GB of RAM"""
  srv3.set_ram_max_capacity(16)
  rack1.add_server(srv3)

  vm1 = sim_vm("dc1_vm1", 8, 16)
  vm1.add_logical_object_in_dc(dc1)
  vm1.set_vm_capability(["containers"])
  
  """cont1 = sim_container("dc1_cont1", 1, 1)
  cont1.add_logical_object_in_dc(dc1)"""
  
  print(dc1)
  print(dc2)
  
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
