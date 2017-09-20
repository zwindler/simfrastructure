# -*- coding: utf-8 -*-
import sys
from math import ceil
from simfrastructure_core import *

def create_tenant_in_dc(tenant_name, x, dc):
  """Client with X microservice applications"""
  modules = []
  tiers = {"frontend" : ["containers", "one_per_module", 1, 1], "backend" : ["containers","one_per_module", 2, 4], "database" : ["vms","unique", 4, 8]}

  """Get containers and vms total footprint"""
  containers_total_vcpu = 0
  containers_total_ram = 0
  vms_subtotal_vcpu = 0
  vms_subtotal_ram = 0
  for k, v in tiers.items():
    if v[0] == "containers":
      if v[1] == "one_per_module":
        containers_total_vcpu += v[2]*x
        containers_total_ram += v[3]*x
      else:
        containers_total_vcpu += v[2]
        containers_total_ram += v[3]
    if v[0] == "vms":
      if v[1] == "one_per_module":
        vms_subtotal_vcpu += v[2]*x
        vms_subtotal_ram += v[3]*x
      else:
        vms_subtotal_vcpu += v[2]
        vms_subtotal_ram += v[3]

  print("Container footprint: "+str(containers_total_vcpu)+" vCPU/"+str(containers_total_ram)+" GB RAM")
  print("Applicative VMs footprint: "+str(vms_subtotal_vcpu)+" vCPU/"+str(vms_subtotal_ram)+" GB RAM")

  """Get vms total footprint"""
  vm_container_runtime_capacity = { "vcpu": 8, "ram" : 16}
  vm_container_runtime_vcpu_contraint=ceil((containers_total_vcpu)/vm_container_runtime_capacity["vcpu"])
  vm_container_runtime_ram_contraint=ceil((containers_total_ram)/vm_container_runtime_capacity["ram"])
  number_of_container_runtime_vm = max(vm_container_runtime_vcpu_contraint,vm_container_runtime_ram_contraint)
  print("Number of runtime VMs needed: "+str(number_of_container_runtime_vm))
  vms_total_vcpu = vms_subtotal_vcpu + vm_container_runtime_capacity["vcpu"] * number_of_container_runtime_vm
  vms_total_ram = vms_subtotal_ram + vm_container_runtime_capacity["ram"] * number_of_container_runtime_vm

  print("Total VMs footprint (applicative and runtime VMs): "+str(vms_total_vcpu)+" vCPU/"+str(vms_total_ram)+" GB RAM")

  """Create enough servers to hosts vms"""
  """Server with 2 sockets, 14 cores each socket, 4 vCPU each core"""
  """Server with 12 sticks of 16GB of RAM"""
  server_capacity = { "vcpu": 2*14*4, "ram" : 12*16 }
  server_vcpu_contraint=ceil((vms_total_vcpu)/server_capacity["vcpu"])
  server_ram_contraint=ceil((vms_total_ram)/server_capacity["ram"])
  number_of_servers = max(server_vcpu_contraint,server_ram_contraint)
  print("Number of needed servers: "+str(number_of_servers))

  for i in range(1, number_of_servers+1):
    srv = sim_server("server"+str(i), 2*14*4, 12*16)
    srv.set_server_capability(["vms"])
    dc.racks[0].add_server(srv)
  
  """Create enough VMs 8vCPU/16GB RAM to host containers"""
  for i in range(1, number_of_container_runtime_vm+1):
      vm = sim_vm(tenant_name+"_container_runtime_"+str(i), vm_container_runtime_capacity["vcpu"], vm_container_runtime_capacity["ram"])
      vm.set_vm_capability(["containers"])
      vm.add_logical_object_in_dc(dc)

  """Create containers and VMs"""
  for i in range(1, x+1):
    module_name = "module"+str(i)
    modules.append(module_name)
    for k, v in tiers.items():
      if v[1] == "one_per_module":
        if v[0] == "containers":
          cont = sim_container(tenant_name+"_"+module_name+"_"+k, v[2], v[3])
          cont.add_logical_object_in_dc(dc)
        else: 
          vm = sim_vm(tenant_name+"_"+module_name+"_"+k, v[2], v[3])
          vm.add_logical_object_in_dc(dc)
  for k, v in tiers.items():
    if v[1] == "unique":
      vm = sim_vm(tenant_name+"_"+k, v[2], v[3])
      vm.add_logical_object_in_dc(dc)    
  
def example_infrastructure():
  dc1 = sim_datacenter("dc1")

  rack1 = sim_rack("dc1_rack1")
  dc1.add_rack(rack1)

  rack2 = sim_rack("dc1_rack2")
  dc1.add_rack(rack2)
  
  create_tenant_in_dc("tenant1", 20, dc1)
  
  print(dc1)

def main():
  example_infrastructure()
  sys.exit()

if __name__ == '__main__':
  main()
