from dataclasses import Field, dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple
import networkx as nx
import matplotlib.pyplot as plt

from reader.method_signature import MethodSignature
from reader.program import Program

@dataclass
class CallGraph:
    nodes: Set[MethodSignature] = field(default_factory=set)
    graph: Dict[MethodSignature, Set[MethodSignature]] = field(default_factory=dict)

    def add_nodes_from(self, nodes: Set[MethodSignature]) -> None:
        for node in nodes:
            self.add_node(node)

    def add_node(self, method_id: MethodSignature) -> None:
        if method_id in self.nodes:
            return
        self.nodes.add(method_id)
        self.graph[method_id] = set()

    def add_edge(self, callsite: MethodSignature, callee: MethodSignature) -> None:
        if not callsite in self.nodes:
            self.add_node(callsite)

        if not callee in self.nodes:
            self.add_node(callee)

        self.graph[callsite].add(callee)


def extract_methods_and_calls(program: Program) -> Tuple[Set[MethodSignature], Dict[MethodSignature, List[MethodSignature]]]:
    method_signatures: Set[MethodSignature] = set()
    calls: Dict[MethodSignature, List[MethodSignature]] = {}

    for file, method in program.all_methods():
        method_signature = method.signature
        method_signatures.add(method_signature)
        bytecode = method.bytecode

        calls[method_signature] = []

        if not bytecode:
            continue
        
        for instruction in bytecode:
            if instruction["opr"] == "invoke":
                if instruction["access"] != "static":
                    continue

                callee = MethodSignature.from_bytecode(instruction["method"])
                calls[method_signature].append(callee)

    return method_signatures, calls


def build_call_graph(program: Program) -> CallGraph:
    methods, calls = extract_methods_and_calls(program)
    call_graph = CallGraph()

    # call_graph.add_nodes_from(methods)

    for callsite, callees in calls.items():
        for callee in callees:

            # Skip callees that are not in the program
            if not callee in methods:
                continue

            call_graph.add_edge(callsite, callee)

    return call_graph


def draw_graph(call_graph: CallGraph) -> None:
    G = nx.DiGraph()
    G.add_nodes_from([node for node in call_graph.nodes])

    for caller, callees in call_graph.graph.items():
        for callee in callees:
            G.add_edge(caller, callee)
    
    nx.draw(G, with_labels=True)
    plt.show()