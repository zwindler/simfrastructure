# -*- coding: utf-8 -*-
import sys
from simfrastructure_core import *

def init_infrastructure():
  dc1 = sim_datacenter("dc1")
  dc2 = sim_datacenter("dc2")

  rack1 = sim_rack("dc1_rack1")
  dc1.add_rack(rack1)
  rack2 = sim_rack("dc2_rack2")
  dc2.add_rack(rack2)

  """Server with 2 sockets, 14 cores each socket, 4 vCPU each core"""
  """Server with 12 sticks of 16GB of RAM"""
  srv1 = sim_server("dc1_rack1_srv1", 2*14*4, 12*16)
  srv1.set_server_capability(["vms"])
  rack1.add_server(srv1)
  
  srv2 = sim_server("dc2_rack2_srv2", 2*14*4, 12*16)
  srv2.set_server_capability(["vms"])
  rack2.add_server(srv2)

  """Server with 1 sockets, 1 cores each socket, 4 vCPU each core"""
  """Server with 1 stick of 16GB of RAM"""
  srv3 = sim_server("dc1_rack1_srv3", 1*1*4, 16)
  srv3.set_server_capability(["vms"])
  rack1.add_server(srv3)

  vm1 = sim_vm("dc1_vm1", 8, 16)
  vm1.add_logical_object_in_dc(dc1)
  vm1.set_vm_capability(["containers"])

  vm2 = sim_vm("dc1_vm2", 1, 1)
  vm2.add_logical_object_in_dc(dc1)
  
  cont1 = sim_container("dc1_cont1", 1, 1)
  cont1.add_logical_object_in_dc(dc1)
  
  print(dc1)
  print(dc2)
  
def usage():
  return ''

def main():
  init_infrastructure()
  sys.exit()

if __name__ == '__main__':
  main()
