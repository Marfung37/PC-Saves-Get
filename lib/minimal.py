# code based on https://github.com/eight04/sfinder-strict-minimal/blob/master/index.js

from dataclasses import dataclass
from typing import Iterable, TextIO
from shutil import get_terminal_size
from .utils import display_fumen, SQUARECHARWIDTH
from .constants import PCSIZE

import sys
sys.setrecursionlimit(5000)

class Node:
  def __init__(self, key: str, edges: set["Edge"], color: int, alter: list["Node"], redundant: bool = False):
    self.key = key
    self.edges = edges
    self.color = color
    self.alter = alter
    self.redundant = redundant

class Edge:
  def __init__(self, nodes: set[Node], color: int, redundant: bool | None = None):
    self.nodes = nodes
    self.color = color
    self.redundant = redundant

@dataclass
class Graph:
  edges: list[Edge]
  nodes: list[Node]

@dataclass
class MinimalSets:
  count: int
  sets: list[list[Node]]

class FumenStore:
  fumen_map: dict[str, Node] = {}

  def fumen_to_node(self, fumen: str) -> Node:
    if (fumen in self.fumen_map):
      return self.fumen_map[fumen]

    node = Node(fumen, set(), 0, [])
    self.fumen_map[fumen] = node
    return node;

  def get_nodes(self) -> list[Node]:
    return list(self.fumen_map.values())

def fumens_to_graph(fumens: list[list[str]]):
  fumen_store = FumenStore()
  edges: list[Edge] = list(
    map(
      lambda f: 
        Edge(
          set(map(fumen_store.fumen_to_node, f)),
          0
        ), 
      fumens
    )
  )

  for edge in edges:
    for node in edge.nodes:
      node.edges.add(edge)

  edges.sort(key=lambda a: len(a.nodes))

  for edge in edges:
    if edge.redundant: continue

    for sibling_edge in set_first(edge.nodes).edges:
      if sibling_edge is edge: continue

      sibling_edge.redundant = edge.nodes.issubset(sibling_edge.nodes)

  clean_edges = list(filter(lambda e: not e.redundant, edges))
  nodes = fumen_store.get_nodes()

  for node in nodes:
    node.edges = {edge for edge in node.edges if not edge.redundant}

  clean_nodes = list(filter(lambda n: len(n.edges), nodes))

  for node in clean_nodes:
    if node.redundant: continue

    for sibling_node in set_first(node.edges).nodes:
      if sibling_node is node: continue

      if sibling_node.edges == node.edges:
        sibling_node.redundant = True
        node.alter.append(sibling_node)

  for edge in clean_edges:
    edge.nodes = {node for node in edge.nodes if not node.redundant}

  return Graph(
    clean_edges,
    list(filter(lambda n: not n.redundant, clean_nodes))
  )

def find_minimal_nodes(edges: list[Edge]) -> MinimalSets:
  current_nodes: list[Node] = []
  result_count = float("inf")
  result_node_set: list[list[Node]] = []

  def digest(index: int = 0) -> None:
    nonlocal result_count, result_node_set
    if (len(current_nodes) > result_count): return;
    
    if (index >= len(edges)):
      if (len(current_nodes) < result_count):
        result_count = len(current_nodes);
        result_node_set = [];
      result_node_set.append(current_nodes.copy());
      return;
    
    edge = edges[index];
    
    if (edge.color):
      digest(index + 1);
      return;
    
    for node in edge.nodes:
      node.color += 1;
      if node.color > 1: continue # the node has been tried by other edges
      
      current_nodes.append(node);
      for siblingEdge in node.edges:
        siblingEdge.color += 1;
      digest(index + 1);
      current_nodes.pop();
      for siblingEdge in node.edges:
        siblingEdge.color -= 1
    for node in edge.nodes:
      node.color -= 1

  digest()
  return MinimalSets(int(result_count), result_node_set)

def set_first(s: set):
  return next(iter(s))

def pretty_print_fumens(fumens: Iterable[str]) -> str:
  delimitor = '    '
  delimitor_size = 4

  max_cols = get_terminal_size((80, 20)).columns // (PCSIZE * SQUARECHARWIDTH + delimitor_size) 

  fields = [field for sublist in map(display_fumen, fumens) for field in sublist]
  chunks = [fields[i:i+max_cols] for i in range(0, len(fields), max_cols)]

  return '\n\n'.join(['\n'.join([delimitor.join(col) for col in zip(*chunk)]) for chunk in chunks])

# prompting for getting set
def find_best_set(sets: list[list[Node]], log_file: TextIO | None = None) -> list[Node]:
  while len(sets) > 1:
    output = f"Try to find the best set. There are {len(sets)} sets\n"

    # find common nodes?
    set0 = set(sets[0])
    set1 = set(sets[1])
    diffA = set0 - set1
    diffB = set1 - set0
   
    output += "Option 1:\n"
    output += pretty_print_fumens(map(lambda n: n.key, diffA)) + '\n'
    output += "Option 2:\n"
    output += pretty_print_fumens(map(lambda n: n.key, diffB)) + '\n'

    print(output)

    result = input("Which is better? 1 or 2: ")

    if log_file is not None:
      output += "Which is better? 1 or 2: " + result + '\n'
      log_file.write(output)

    if result == '2':
      sets.pop(1)
    else:
      sets.pop(0)

  return sets[0]

