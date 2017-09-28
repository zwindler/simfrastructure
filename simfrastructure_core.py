#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
from graphviz import Digraph

current_indent = 0
color_map = ['lightgrey', 'lightpink', 'orange', 'cyan', 'gold', 'lawngreen', 'sienna', 'yellow', 'red', 'hotpink']
verbose = 0

def print_simple_tree():
  indent= "| "
  last_indent= "\_"
  """prints a beautiful dependancy tree"""
  return max(current_indent-1,0)*indent+min(1,current_indent)*last_indent

class sim_datacenter:
  """A datacenter that can contain racks"""
  def __init__(self, name, tenant_id=0):
    self.name = name
    self.racks = []
    self.rack_max = None
    self.tenant_id= tenant_id

  """Set maximum number of racks in DC"""
  def set_rack_max(self, rack_max):
    self.rack_max = rack_max

  def add_rack(self, rack):
    if (not isinstance(rack, sim_rack)):
      print(rack.name+" is not a rack!")
    if ( self.rack_max == None or len(racks) < self.rack_max ):
      self.racks.append(rack)
    else:
      print(self.name+" is full, can't add rack!")

  def find_suitable_host(self, kind, guest_capacity):
    suitable_objects = []
    for rack in self.racks:
      for server in rack.servers:
        if server.get_host_capability(kind) and server.has_enough_ressources(guest_capacity):
          suitable_objects.append(server)
        if "vms" in server.guests:
          for vm in server.guests["vms"]:
            if vm.get_host_capability(kind) and vm.has_enough_ressources(guest_capacity):
              suitable_objects.append(vm)
    return random.choice(suitable_objects)

  def get_dc_free_capacity(self, kind):
    dc_free_capacity = {"vcpu": 0, "ram": 0}
    for rack in self.racks:
      rack_free_capacity = rack.get_rack_free_capacity(kind)
      dc_free_capacity["vcpu"] += rack_free_capacity["vcpu"]
      dc_free_capacity["ram"] += rack_free_capacity["ram"]
    return dc_free_capacity

  def generate_graph(self, graph):
    global color_map
    graph.attr('node', style='filled', color=color_map[self.tenant_id])
    graph.attr('node', shape='diamond', overlap='false')
    graph.node(self.name)
    for rack in self.racks:
      graph.attr('node', style='filled', color=color_map[rack.tenant_id])
      graph.attr('node', shape='box', overlap='false')
      graph.node(rack.name)
      graph.edge(self.name, rack.name) 
      graph = rack.generate_graph(graph)
    return graph

  def __str__(self):
    global current_indent
    output = "Datacenter "+self.name+"\n"
    current_indent += 1
    if verbose:
      output += print_simple_tree()+"Datacenter size: "+str(self.rack_max)+"\n"
      output += print_simple_tree()+"Racks in this datacenter: \n"
      current_indent += 1
    for rack in self.racks:
      output += str(rack)
    current_indent = 0
    return output
  
class sim_rack:
  """A rack that can contain servers"""  
  def __init__(self, name, tenant_id=0):
    self.name = name
    self.servers = []
    self.rack_size = 42
    self.tenant_id = tenant_id

  """Set maximum number of servers units in rack"""
  def set_rack_size(self, rack_size):
    self.rack_size = rack_size

  def get_rack_usage(self):
    rack_usage = 0
    for server in self.servers:
      rack_usage += server.server_size
    return rack_usage

  def get_rack_free_capacity(self, kind):
    rack_free_capacity = {"vcpu": 0, "ram": 0}
    for server in self.servers:
      server_free_capacity = server.get_host_free_capacity(kind)
      rack_free_capacity["vcpu"] += server_free_capacity["vcpu"]
      rack_free_capacity["ram"] += server_free_capacity["ram"]
    return rack_free_capacity

  def add_server(self, server):
    if (not isinstance(server, sim_server)):
      print(server.name+" is not a server!")
    rack_usage = self.get_rack_usage()
    if ( self.rack_size == None or rack_usage < self.rack_size):
      self.servers.append(server)
    else:
      print(self.name+" is full, can't add server!")

  def generate_graph(self, graph):
    for server in self.servers:
      global color_map
      graph.attr('node', style='filled', color=color_map[server.tenant_id])
      graph.attr('node', shape='ellipse')
      graph.node(server.name)
      graph.edge(self.name, server.name) 
      with graph.subgraph(name='cluster_'+server.name) as c:
        c.attr(color='blue')
        c = server.generate_graph(c)
    return graph

  def __str__(self):
    global current_indent
    output = print_simple_tree()+"Rack "+self.name+"\n"
    current_indent += 1
    if verbose:
      output += print_simple_tree()+"Rack usage: "+str(self.get_rack_usage())+"/"+str(self.rack_size)+"U\n"
      output += print_simple_tree()+"Servers in this rack: \n"
      current_indent += 1
    for server in self.servers:
      output += str(server)
    current_indent -= 1
    return output

class sim_host:
  def has_enough_ressources(self, guest_capacity):
    usage = self.get_host_usage()
    suitable = True
    for k in usage.keys():
      if usage[k] + guest_capacity[k] > self.capacity[k]:
        return None
    return self

  def get_host_usage(self):
    host_usage = {"vcpu" : 0, "ram" : 0}
    for k, v in self.guests.items():
      for logical_object in v:
        host_usage["vcpu"] += logical_object.capacity["vcpu"]
        host_usage["ram"] += logical_object.capacity["ram"]
    return host_usage

  def get_host_free_capacity(self, kind):
    host_free_capacity = {"vcpu": 0, "ram": 0}
    if self.get_host_capability(kind):
      usage = self.get_host_usage()
      for k in usage.keys():
        host_free_capacity[k] = self.capacity[k] - usage[k] 
    return host_free_capacity

  """Set the ability to run VMs or containers or both"""
  def set_host_capability(self, capabilities):
    for capability in capabilities:
      self.guests[capability] = []

  def get_host_capability(self, kind):
    if kind in self.guests.keys() :
      return True
    return False

  def register_logical_object_to_host(self, guest):
    self.guests[guest.kind].append(guest)
  
  def generate_graph(self, graph):
    for guest_types in self.guests:
      for guest in self.guests[guest_types]:
        global color_map
        graph.attr('node', style='filled', color=color_map[guest.tenant_id])
        if guest_types == "containers":
          graph.attr('node', shape='box3d', style="")
        elif guest_types == "vms":
          graph.attr('node', shape='hexagon', style="")
        graph.node(guest.name)
        graph.edge(self.name, guest.name) 
        with graph.subgraph(name='cluster_'+guest.name) as c:
          c.attr(color='blue')
          c = guest.generate_graph(c)
    return graph

class sim_server(sim_host):
  """A 2U server that may run containers or virtual machines or both"""
  def __init__(self, name, vcpu_max_capacity, ram_max_capacity, tenant_id=0):
    self.name = name
    self.server_size = 2
    self.capacity = {"vcpu": vcpu_max_capacity, "ram": ram_max_capacity}
    self.guests = {}
    self.tenant_id = tenant_id

  def __str__(self):
    global current_indent
    output = print_simple_tree()+"Server "+self.name+" (Usage: "+str(self.get_host_usage()["vcpu"])+"/"+str(self.capacity["vcpu"])+" vCPU; "+str(self.get_host_usage()["ram"])+"/"+str(self.capacity["ram"])+" GB RAM)\n"
    current_indent += 1
    if verbose:
      output += print_simple_tree()+"Server size : "+str(self.server_size)+"U\n"
    if "vms" in self.guests.keys():
      if verbose:
        output += print_simple_tree()+"Can run VMs\n"
      for vm in self.guests["vms"]:
        output += str(vm)
    if "containers" in self.guests.keys():
      current_indent += 1
      if verbose:
        output += print_simple_tree()+"Can run containers\n"
      for container in self.guests["containers"]:
        output += str(container)
      current_indent -= 1
    current_indent -= 1
    return output

class sim_logical_object(sim_host):
  """Allocate vm or container in a specified DC"""
  def add_logical_object_in_dc(self, dc):
    host = dc.find_suitable_host(self.kind, self.capacity)
    host.register_logical_object_to_host(self)
    
  """Force VM or container allocation on a specified server"""
  """def add_logical_object_on_server(self, server):
    print(guest)"""

  def __init__(self, name, vcpu_alloc, ram_alloc, tenant_id=0):
    self.name = name
    self.capacity = {"vcpu": vcpu_alloc, "ram": ram_alloc}
    self.guests = {}
    self.tenant_id = tenant_id
    
  def __str__(self):
    output = print_simple_tree()+self.label+" "+self.name+" ("+str(self.capacity["vcpu"])+"vCPU/"+str(self.capacity["ram"])+"GB RAM)\n"
    return output
    
class sim_vm(sim_logical_object):
  """A VM on a server that can execute VMs"""
  kind = "vms"
  label = "VM"

  def __str__(self):
    global current_indent
    output = super(sim_vm, self).__str__()
    if "containers" in self.guests.keys():
      current_indent += 1
      if verbose:
        output += print_simple_tree()+"Can run containers\n"
      for container in self.guests["containers"]:
        output += str(container)
      current_indent -= 1
    return output

class sim_container(sim_logical_object):
  """A container on a server that can execute containers"""
  kind = "containers"
  label = "Container"

  """Force container allocation on a specified VM"""
  """def add_container_on_vm(self, vm):
    print("TODO")"""
