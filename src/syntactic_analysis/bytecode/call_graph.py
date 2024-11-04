from dataclasses import Field, dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple
from static_analysis.program import Program, MethodId
import networkx as nx
import matplotlib.pyplot as plt

@dataclass
class CallGraph:
    nodes: Set[MethodId] = field(default_factory=set)
    graph: Dict[MethodId, Set[MethodId]] = field(default_factory=dict)

    def add_nodes_from(self, nodes: Set[MethodId]) -> None:
        for node in nodes:
            self.add_node(node)

    def add_node(self, method_id: MethodId) -> None:
        if method_id in self.nodes:
            return
        self.nodes.add(method_id)
        self.graph[method_id] = set()

    def add_edge(self, callsite: MethodId, callee: MethodId) -> None:
        if not callsite in self.nodes:
            self.add_node(callsite)

        if not callee in self.nodes:
            self.add_node(callee)

        self.graph[callsite].add(callee)

def extract_methods_and_calls(program: Program) -> Tuple[Set[MethodId], Dict[MethodId, List[MethodId]]]:
    methods: Set[MethodId] = set(program._program.keys())
    calls: Dict[MethodId, List[MethodId]] = {}

    for method_id, bytecode in program._program.items():
        calls[method_id] = []

        if not bytecode:
            continue
        
        for instruction in bytecode:
            if instruction["opr"] == "invoke":
                if instruction["access"] != "static":
                    continue

                callee = MethodId.from_bytecode_invocation(instruction)
                calls[method_id].append(callee)

    return methods, calls

def build_call_graph(program: Program) -> CallGraph:
    methods, calls = extract_methods_and_calls(program)
    call_graph = CallGraph()

    call_graph.add_nodes_from(methods)

    for callsite, callees in calls.items():
        for callee in callees:

            # Skip callees that are not in the program
            if not callee in methods:
                continue

            call_graph.add_edge(callsite, callee)

    return call_graph

def draw_graph(call_graph: CallGraph) -> None:
    G = nx.DiGraph()
    G.add_nodes_from([node.fully_qualified_signature() for node in call_graph.nodes])

    for caller, callees in call_graph.graph.items():
        for callee in callees:
            G.add_edge(caller.fully_qualified_signature(), callee.fully_qualified_signature())
    
    nx.draw(G, with_labels=True)
    plt.show()

if __name__ == "__main__":
    p = Path("data", "bytecode")

    program: Program = Program.parse_program(p)
    graph = build_call_graph(program)
    draw_graph(graph)