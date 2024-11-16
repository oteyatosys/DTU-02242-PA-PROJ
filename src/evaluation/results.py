
from dataclasses import dataclass
from typing import List, Set

from reader.method_signature import MethodSignature


@dataclass
class TestStageResult:
    predicted: Set[MethodSignature]
    ground_truth: Set[MethodSignature]
    time_taken: float = 0.0

    def compute_true_positives(self) -> Set[MethodSignature]:
        return self.predicted & self.ground_truth
    
    def compute_false_positives(self) -> Set[MethodSignature]:
        return self.predicted - self.ground_truth
    
    def compute_false_negatives(self) -> Set[MethodSignature]:
        return self.ground_truth - self.predicted
    
    def compute_true_positives_count(self) -> int:
        return len(self.compute_true_positives())
    
    def compute_false_positives_count(self) -> int:
        return len(self.compute_false_positives())
    
    def compute_false_negatives_count(self) -> int:
        return len(self.compute_false_negatives())

    def compute_accuracy(self) -> float:
        tp = self.compute_true_positives_count()
        fp = self.compute_false_positives_count()
        fn = self.compute_false_negatives_count()
        return tp / (tp + fp + fn)
    
    def compute_precision(self) -> float:
        tp = self.compute_true_positives_count()
        fp = self.compute_false_positives_count()
        return tp / (tp + fp)
    
    def compute_recall(self) -> float:
        tp = self.compute_true_positives_count()
        fn = self.compute_false_negatives_count()
        return tp / (tp + fn)
    
    def compute_f1_score(self) -> float:
        precision = self.compute_precision()
        recall = self.compute_recall()
        return 2 * (precision * recall) / (precision + recall)


@dataclass
class TestScenarioResult:
    stage_results: List[TestStageResult]
    
    def compute_total_time_taken(self) -> float:
        total_time_taken = 0.0
        for stage_result in self.stage_results:
            total_time_taken += stage_result.time_taken
        return total_time_taken
    
    def compute_average_time_taken(self) -> float:
        total_time_taken = self.compute_total_time_taken() 
        return total_time_taken / len(self.stage_results)
    
    def compute_total_true_positive_count(self) -> int:
        total_true_positive_count = 0
        for stage_result in self.stage_results:
            total_true_positive_count += stage_result.compute_true_positives_count()
        return total_true_positive_count
    
    def compute_total_false_positive_count(self) -> int:
        total_false_positive_count = 0
        for stage_result in self.stage_results:
            total_false_positive_count += stage_result.compute_false_positives_count()
        return total_false_positive_count
    
    def compute_total_false_negative_count(self) -> int:
        total_false_negative_count = 0
        for stage_result in self.stage_results:
            total_false_negative_count += stage_result.compute_false_negatives_count()
        return total_false_negative_count
    
    def compute_total_accuracy(self) -> float:
        total_true_positive_count = self.compute_total_true_positive_count()
        total_false_positive_count = self.compute_total_false_positive_count()
        total_false_negative_count = self.compute_total_false_negative_count()
        return total_true_positive_count / (total_true_positive_count + total_false_positive_count + total_false_negative_count)
    
    def compute_total_precision(self) -> float:
        total_true_positive_count = self.compute_total_true_positive_count()
        total_false_positive_count = self.compute_total_false_positive_count()
        return total_true_positive_count / (total_true_positive_count + total_false_positive_count)
    
    def compute_total_recall(self) -> float:
        total_true_positive_count = self.compute_total_true_positive_count()
        total_false_negative_count = self.compute_total_false_negative_count()
        return total_true_positive_count / (total_true_positive_count + total_false_negative_count)
    
    def compute_total_f1_score(self) -> float:
        total_precision = self.compute_total_precision()
        total_recall = self.compute_total_recall()
        return 2 * (total_precision * total_recall) / (total_precision + total_recall)
    
    def print_stats(self):
        print(f"Total time taken: {self.compute_total_time_taken()}")
        print(f"Average time taken: {self.compute_average_time_taken()}")
        print(f"Total true positives: {self.compute_total_true_positive_count()}")
        print(f"Total false positives: {self.compute_total_false_positive_count()}")
        print(f"Total false negatives: {self.compute_total_false_negative_count()}")
        print(f"Total accuracy: {self.compute_total_accuracy()}")
        print(f"Total precision: {self.compute_total_precision()}")
        print(f"Total recall: {self.compute_total_recall()}")
        print(f"Total F1 score: {self.compute_total_f1_score()}")