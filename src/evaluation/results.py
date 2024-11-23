
from dataclasses import dataclass
from typing import List, Set

from reader.method_signature import MethodSignature


@dataclass
class TestStageResult:
    predicted: Set[MethodSignature]
    ground_truth: Set[MethodSignature]
    found_ground_truth: Set[MethodSignature]
    prediction_time: float = 0.0
    test_time: float = 0.0

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
    
    def print_stats(self):
        print(f"Time taken: {self.prediction_time}")
        print(f"True positives: {self.compute_true_positives_count()}")
        print(f"False positives: {self.compute_false_positives_count()}")
        print(f"False negatives: {self.compute_false_negatives_count()}")
        print(f"Accuracy: {self.compute_accuracy()}")
        print(f"Precision: {self.compute_precision()}")
        print(f"Recall: {self.compute_recall()}")
        print(f"F1 score: {self.compute_f1_score()}")


@dataclass
class TestScenarioResult:
    stage_results: List[TestStageResult]
    
    def compute_total_time_taken(self) -> float:
        total_time_taken = 0.0
        for stage_result in self.stage_results:
            total_time_taken += stage_result.prediction_time
        return total_time_taken
    
    def compute_average_time_taken(self) -> float:
        total_time_taken = self.compute_total_time_taken() 
        return total_time_taken / len(self.stage_results)
    
    def compute_total_test_time_taken(self) -> float:
        total_time_taken = 0.0
        for stage_result in self.stage_results:
            total_time_taken += stage_result.test_time
        return total_time_taken
    
    def compute_average_test_time_taken(self) -> float:
        total_time_taken = self.compute_total_test_time_taken() 
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


@dataclass
class TestSuiteResult:
    scenario_results: List[TestScenarioResult]
    
    def compute_total_time_taken(self) -> float:
        total_time_taken = 0.0
        for scenario_result in self.scenario_results:
            total_time_taken += scenario_result.compute_total_time_taken()
        return total_time_taken
    
    def compute_average_time_taken(self) -> float:
        total_time_taken = self.compute_total_time_taken() 
        return total_time_taken / len(self.scenario_results)
    
    def compute_total_true_positive_count(self) -> int:
        total_true_positive_count = 0
        for scenario_result in self.scenario_results:
            total_true_positive_count += scenario_result.compute_total_true_positive_count()
        return total_true_positive_count
    
    def compute_total_false_positive_count(self) -> int:
        total_false_positive_count = 0
        for scenario_result in self.scenario_results:
            total_false_positive_count += scenario_result.compute_total_false_positive_count()
        return total_false_positive_count
    
    def compute_total_false_negative_count(self) -> int:
        total_false_negative_count = 0
        for scenario_result in self.scenario_results:
            total_false_negative_count += scenario_result.compute_total_false_negative_count()
        return total_false_negative_count
    
    def compute_total_accuracy(self) -> float:
        total_true_positive_count = self.compute_total_true_positive_count()
        total_false_positive_count = self.compute_total_false_positive_count()
        total_false_negative_count = self.compute_total_false_negative_count()
        return total_true_positive_count / (total_true_positive_count + total_false_positive_count + total_false_negative_count)
    
    def compute_total_precision(self) -> float:
        total_true_positive_count = self.compute_total_true_positive_count()
        total_false_positive_count = self.compute_total_false_positive_count()
        
        denominator = total_true_positive_count + total_false_positive_count
        if denominator == 0:
            return 0.0
        
        return total_true_positive_count / denominator
    
    def compute_total_recall(self) -> float:
        total_true_positive_count = self.compute_total_true_positive_count()
        total_false_negative_count = self.compute_total_false_negative_count()
        
        denominator = total_true_positive_count + total_false_negative_count
        if denominator == 0:
            return 0.0
        
        return total_true_positive_count / denominator
    
    def compute_total_f1_score(self) -> float:
        total_precision = self.compute_total_precision()
        total_recall = self.compute_total_recall()
        
        denominator = total_precision + total_recall
        if denominator == 0:
            return 0.0
        
        return 2 * (total_precision * total_recall) / denominator
    
    def compute_average_time_taken_by_stage(self) -> float:
        total_time_taken = self.compute_total_time_taken() 
        stage_count = 0
        for scenario_result in self.scenario_results:
            stage_count += len(scenario_result.stage_results)

        return total_time_taken / stage_count
    
    def compute_average_test_time_taken_by_stage(self) -> float:
        total_time_taken = 0.0
        stage_count = 0
        for scenario_result in self.scenario_results:
            for stage_result in scenario_result.stage_results:
                # Skip stages that whose test time was not recorded
                if stage_result.test_time is None:
                    continue

                total_time_taken += stage_result.test_time
                stage_count += 1

        if stage_count == 0:
            return None

        return total_time_taken / stage_count

    def compute_average_time_taken_variance_by_stage(self) -> float:
        average_time_taken = self.compute_average_time_taken_by_stage()
        total_variance = 0.0
        stage_count = 0
        for scenario_result in self.scenario_results:
            for stage_result in scenario_result.stage_results:
                total_variance += (stage_result.prediction_time - average_time_taken) ** 2
                stage_count += 1

        return total_variance / stage_count

    def compute_average_test_time_taken_variance_by_stage(self) -> float:
        average_time_taken = self.compute_average_test_time_taken_by_stage()

        if average_time_taken is None:
            return None

        total_variance = 0.0
        stage_count = 0
        for scenario_result in self.scenario_results:
            for stage_result in scenario_result.stage_results:
                total_variance += (stage_result.test_time - average_time_taken) ** 2
                stage_count += 1

        return total_variance / stage_count

    def print_stats(self):
        print(f"Total time taken: {self.compute_total_time_taken()}")
        print(f"Average time taken by stage: {self.compute_average_time_taken_by_stage()}")
        print(f"Average time taken by stage variance: {self.compute_average_time_taken_variance_by_stage()}")
        print(f"Average test time taken by stage: {self.compute_average_test_time_taken_by_stage()}")
        print(f"Average test time taken by stage variance: {self.compute_average_test_time_taken_variance_by_stage()}")
        print(f"Total true positives: {self.compute_total_true_positive_count()}")
        print(f"Total false positives: {self.compute_total_false_positive_count()}")
        print(f"Total false negatives: {self.compute_total_false_negative_count()}")
        print(f"Total accuracy: {self.compute_total_accuracy()}")
        print(f"Total precision: {self.compute_total_precision()}")
        print(f"Total recall: {self.compute_total_recall()}")
        print(f"Total F1 score: {self.compute_total_f1_score()}")