
from dataclasses import dataclass
from typing import Set

import jsondiff
from prediction.predictor import TestPredictor
from reader.method_signature import MethodSignature
from reader.program import Program
from syntactic_analysis.bytecode.call_graph import build_call_graph
import logging as l


@dataclass
class CallGraphPredictor(TestPredictor):
    # Used to remove offsets from bytecode, as these seem to alternate between decompilations
    def _remove_offsets(self, bytecode):
        if isinstance(bytecode, dict):
            return {k: self._remove_offsets(v) for k, v in bytecode.items() if k != 'offset'}
        elif isinstance(bytecode, list):
            return [self._remove_offsets(item) for item in bytecode]
        return bytecode

    def predict(self, old_program: Program, new_program: Program) -> Set[MethodSignature]:
        call_graph = build_call_graph(old_program)
        
        # draw_graph(call_graph)

        test_predictions: Set[MethodSignature] = set()
        
        new_methods: Set[MethodSignature] = set()
        changed_methods: Set[MethodSignature] = set()

        def walk_callgraph(start_node: MethodSignature, old_signature: MethodSignature) -> bool:

            if not new_program.contains_method(old_signature):
                l.debug(f"Method {old_signature} has been removed")
                test_predictions.add(start_node)
                new_methods.add(old_signature)
                return False
            
            new_method = new_program.method(old_signature)
            old_method = old_program.method(old_signature)

            new_bytecode = self._remove_offsets(new_method.bytecode)
            old_bytecode = self._remove_offsets(old_method.bytecode)

            if new_bytecode == old_bytecode:
                return True

            diff = jsondiff.diff(old_bytecode, new_bytecode)
            
            if diff:
                l.debug(f"Method {old_signature} has changed:")
                test_predictions.add(start_node)
                changed_methods.add(old_signature)
                return False

            return True

        for file, method in new_program.all_test_methods():
            if not method.signature in call_graph:
                test_predictions.add(method.signature)
                continue
            
            call_graph.bfs_walk(method.signature, walk_callgraph)

        return test_predictions