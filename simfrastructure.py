#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from math import ceil
from simfrastructure_core import *

verbose=1
current_server_index=1

def gererate_png(sim_object, type, graph_attributes):
  if type == "twopi":
    graph = Digraph(name=sim_object.name, format='png', engine='twopi', graph_attr=graph_attributes)
  else:
    graph = Digraph(name=sim_object.name, format='png', graph_attr=graph_attributes)
  graph = sim_object.generate_graph(graph)
  print(graph)
  graph.render()

def create_servers_to_host_vms(dc, server_capacity, vms_to_host):
  global current_server_index
  """Get vms total footprint"""
  vms_total_vcpu = 0.0
  vms_total_ram = 0.0
  for vm in vms_to_host:
    vms_total_vcpu += vm.capacity["vcpu"]
    vms_total_ram += vm.capacity["ram"]
  if verbose:
    print("Total VMs footprint (applicative and runtime VMs): "+str(vms_total_vcpu)+" vCPU/"+str(vms_total_ram)+" GB RAM")

  server_capacity = { "vcpu": 2*14*4, "ram" : 24*16 }
  """Remember that we might have server not full in dc to reuse"""
  dc_free_capacity = dc.get_dc_free_capacity('vms')
  if verbose:
    print("Remaining capacity: "+str(dc.get_dc_free_capacity("vms")["vcpu"])+" vCPU/"+str(dc.get_dc_free_capacity("vms")["ram"])+"GB RAM")

  server_vcpu_contraint = max(0,int(ceil((vms_total_vcpu - dc_free_capacity["vcpu"])/server_capacity["vcpu"])))
  server_ram_contraint = max(0,int(ceil((vms_total_ram - dc_free_capacity["ram"])/server_capacity["ram"])))
  number_of_servers = max(server_vcpu_contraint,server_ram_contraint)
  if verbose:
    print("Number of needed servers: "+str(number_of_servers))

  """Create servers"""
  for i in range(1, number_of_servers+1):
    srv = sim_server("server"+str(current_server_index), server_capacity["vcpu"], server_capacity["ram"])
    srv.set_host_capability(["vms"])
    dc.racks[0].add_server(srv)
    current_server_index += 1

def create_tenant_in_dc(tenant_id, tiers, modules, dc):
  """Client with X microservice applications"""
  tenant_name = "client"+str(tenant_id)
  containers_to_host= []
  vms_to_host = []

  """Create containers and VMs"""
  for module in modules:
    for k, v in tiers.items():
      if v[1] == "one_per_module":
        if v[0] == "containers":
          cont = sim_container(tenant_name+"_"+module+"_"+k, v[2], v[3], tenant_id)
          containers_to_host.append(cont)
        elif v[0] == "vms": 
          vm = sim_vm(tenant_name+"_"+module+"_"+k, v[2], v[3], tenant_id)
          vms_to_host.append(vm)
  for k, v in tiers.items():
    if v[1] == "unique":
      if v[0] == "vms":
        vm = sim_vm(tenant_name+"_"+k, v[2], v[3], tenant_id)
        vms_to_host.append(vm)
      elif v[1] == "containers":
        cont = sim_container(tenant_name+"_"+k, v[2], v[3], tenant_id)
        containers_to_host.append(cont)     

  """Get containers and vms total footprint"""
  containers_total_vcpu = 0
  containers_total_ram = 0
  for container in containers_to_host:
    containers_total_vcpu += container.capacity["vcpu"]
    containers_total_ram += container.capacity["ram"]
  if verbose:
    print("Container footprint: "+str(containers_total_vcpu)+" vCPU/"+str(containers_total_ram)+" GB RAM")

  """How much VMs do we need to host containers?"""
  vm_container_runtime_capacity = { "vcpu": 6, "ram" : 12}
  vm_container_runtime_vcpu_contraint = int(ceil((containers_total_vcpu)/vm_container_runtime_capacity["vcpu"]))
  vm_container_runtime_ram_contraint = int(ceil((containers_total_ram)/vm_container_runtime_capacity["ram"]))
  number_of_container_runtime_vm = max(vm_container_runtime_vcpu_contraint,vm_container_runtime_ram_contraint)
  if verbose:
    print("Number of container runtime VMs needed: "+str(number_of_container_runtime_vm))
  
  """Create enough VMs 6vCPU/12GB RAM to host containers. BUG : need 1 more in case placement is not ideal"""
  for i in range(1, number_of_container_runtime_vm+2):
      vm = sim_vm(tenant_name+"_docker_"+str(i), vm_container_runtime_capacity["vcpu"], vm_container_runtime_capacity["ram"], tenant_id)
      vm.set_host_capability(["containers"])
      vms_to_host.append(vm)

  """How much servers do we need to host vms?"""
  """Server with 2 sockets, 14 cores each socket, 4 vCPU each core"""
  """Server with 24 sticks of 16GB of RAM"""
  server_capacity = { "vcpu": 2*14*4, "ram" : 24*16 }
  create_servers_to_host_vms(dc, server_capacity, vms_to_host)

  """Host VMs and containers"""
  for vm in vms_to_host:
    vm.add_logical_object_in_dc(dc)
  for container in containers_to_host:
    print(container)
    container.add_logical_object_in_dc(dc)
  
def example_infrastructure():
  dc1 = sim_datacenter("dc1")

  rack1 = sim_rack("dc1_rack1")
  dc1.add_rack(rack1)

  """Create 8 clients with the same multitiered microservice application"""
  """Do not share VMs between tenants"""
  tiers = {"front" : ["containers", "one_per_module", 0.5, 1], "back" : ["containers","one_per_module", 1, 2], "db" : ["vms","unique", 8, 16]}

  modules = []
  for i in range(1,11):
    modules.append("microsvc"+str(i))

  for i in range(1,4):
    create_tenant_in_dc(i, tiers, modules, dc1)
  
  #print(dc1)
  graph_attr={"ranksep": "8", "ratio": "auto"}
  gererate_png(dc1, "twopi", graph_attr)

def main():
  example_infrastructure()
  sys.exit()

if __name__ == '__main__':
  main()
