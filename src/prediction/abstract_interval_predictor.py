from dataclasses import dataclass, field
from typing import Any, Set

import jsondiff
from prediction.predictor import TestPredictor
from reader.method import Method
from reader.method_signature import MethodSignature
from static_analysis.interpreter.abstract_sign_interpreter import PC
from static_analysis.interpreter.abstractions.abstract_state import AbstractState
from static_analysis.interpreter.abstract_interval_interpreter import AbstractIntervalInterpreter
from syntactic_analysis.bytecode.call_graph import CallGraph, build_call_graph
import logging as l

from syntactic_analysis.scanner import get_int_literals

@dataclass
class AbstractIntervalPredictor(TestPredictor):
    def _remove_offsets(self, bytecode):
        if isinstance(bytecode, dict):
            return {k: self._remove_offsets(v) for k, v in bytecode.items() if k != 'offset'}
        elif isinstance(bytecode, list):
            return [self._remove_offsets(item) for item in bytecode]
        return bytecode


    def _add_offsets(self, changed_bc: dict[MethodSignature, Set[int]], signature: MethodSignature, changed: Set[int]):
        if signature not in changed_bc:
            changed_bc[signature] = set()
        changed_bc[signature].update(changed)

    
    def predict(self, old_program, new_program):
        # Find prediction candidates and changed bytecode

        call_graph: CallGraph = build_call_graph(old_program)

        changed_bc: dict[MethodSignature, Set[int]] = {}

        tests_to_analyse: Set[MethodSignature] = set()

        def walk_callgraph(start_node: MethodSignature, new_signature: MethodSignature) -> bool:
            new_method: Method = new_program.method(new_signature)

            if not old_program.contains_method(new_signature):
                tests_to_analyse.add(start_node)
                self._add_offsets(changed_bc, start_node, set(range(len(new_method.bytecode))))
                return True

            old_method: Method = old_program.method(new_signature)

            new_bytecode = self._remove_offsets(new_method.bytecode)
            old_bytecode = self._remove_offsets(old_method.bytecode)

            if new_bytecode == old_bytecode:
                return True

            diff: dict[int, Any] = jsondiff.diff(old_bytecode, new_bytecode)
            
            if diff:
                l.debug(f"Method {new_signature} has changed:")
                tests_to_analyse.add(start_node)

                changed = set(diff.keys()) - {jsondiff.insert, jsondiff.delete}

                inserts = diff.get(jsondiff.insert, [])
                deletions = diff.get(jsondiff.delete, [])

                inserted_indexes = [
                    insert[0]
                    for insert in inserts
                ]
                
                deleted_indexes = [
                    deletion[0]
                    for deletion in deletions
                ]

                changed.update(inserted_indexes)
                changed.update(deleted_indexes)

                self._add_offsets(
                    changed_bc, 
                    new_signature,
                    changed
                )

                return True

            return True

        for _, method in new_program.all_test_methods():         
            call_graph.bfs_walk(method.signature, walk_callgraph)

        # Analyse prediction candidates

        test_predictions: Set[MethodSignature] = set()

        for test_signature in tests_to_analyse:
            interpreter = AbstractIntervalInterpreter(new_program)

            pc = PC(test_signature, 0)
            initial_state = AbstractState([], {})

            touched = interpreter.analyse(pc, initial_state)

            if len(interpreter.errors) <= 0:
                continue

            for signature, offsets in touched.items():
                if not signature in changed_bc:
                    continue

                intersection = offsets.intersection(changed_bc[signature])

                if intersection:
                    test_predictions.add(test_signature)
                    break

        return test_predictions

            