
from dataclasses import dataclass
from typing import List, Set

from reader.method_signature import MethodSignature


@dataclass
class TestStageResult:
    predicted: Set[MethodSignature]
    ground_truth_positive: Set[MethodSignature]
    ground_truth_negative: Set[MethodSignature]
    found_ground_truth: Set[MethodSignature]
    prediction_time: float = 0.0
    test_time: float = 0.0

    def compute_true_positives(self) -> Set[MethodSignature]:
        return self.predicted & self.ground_truth_positive
    
    def compute_false_positives(self) -> Set[MethodSignature]:
        return self.predicted - self.ground_truth_positive
    
    def compute_false_negatives(self) -> Set[MethodSignature]:
        return self.ground_truth_positive - self.predicted
    
    def compute_true_negatives(self) -> Set[MethodSignature]:
        return self.ground_truth_negative - self.predicted
    
    def compute_true_positives_count(self) -> int:
        return len(self.compute_true_positives())
    
    def compute_false_positives_count(self) -> int:
        return len(self.compute_false_positives())
    
    def compute_false_negatives_count(self) -> int:
        return len(self.compute_false_negatives())
    
    def compute_true_negatives_count(self) -> int:
        return len(self.compute_true_negatives())

@dataclass
class TestScenarioResult:
    stage_results: List[TestStageResult]
    
    def compute_total_prediction_time(self) -> float:
        total_time_taken = 0.0
        for stage_result in self.stage_results:
            total_time_taken += stage_result.prediction_time
        return total_time_taken
    
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
    
    def compute_total_true_negative_count(self) -> int:
        total_true_negative_count = 0
        for stage_result in self.stage_results:
            total_true_negative_count += stage_result.compute_true_negatives_count()
        return total_true_negative_count


@dataclass
class TestSuiteResult:
    scenario_results: List[TestScenarioResult]
    evaluation_time: float
    
    def compute_total_prediction_time(self) -> float:
        total_time_taken = 0.0
        for scenario_result in self.scenario_results:
            total_time_taken += scenario_result.compute_total_prediction_time()
        return total_time_taken
    
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
    
    def compute_total_true_negative_count(self) -> int:
        total_true_negative_count = 0
        for scenario_result in self.scenario_results:
            total_true_negative_count += scenario_result.compute_total_true_negative_count()
        return total_true_negative_count
    
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
    
    def compute_mean_prediction_time(self) -> float:
        total_time_taken = self.compute_total_prediction_time() 
        stage_count = 0
        for scenario_result in self.scenario_results:
            stage_count += len(scenario_result.stage_results)

        return total_time_taken / stage_count
    
    def compute_mean_test_time(self) -> float:
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

    def compute_prediction_time_variance(self) -> float:
        average_time_taken = self.compute_mean_prediction_time()
        total_variance = 0.0
        stage_count = 0
        for scenario_result in self.scenario_results:
            for stage_result in scenario_result.stage_results:
                total_variance += (stage_result.prediction_time - average_time_taken) ** 2
                stage_count += 1

        return total_variance / stage_count

    def compute_test_time_variance(self) -> float:
        average_time_taken = self.compute_mean_test_time()

        if average_time_taken is None:
            return None

        total_variance = 0.0
        stage_count = 0
        for scenario_result in self.scenario_results:
            for stage_result in scenario_result.stage_results:
                total_variance += (stage_result.test_time - average_time_taken) ** 2
                stage_count += 1

        return total_variance / stage_count
    
    def compute_test_time_std_deviation(self) -> float:
        variance = self.compute_test_time_variance()
        if variance is None:
            return None
        
        return variance ** 0.5
    
    def compute_prediction_time_std_deviation(self) -> float:
        return self.compute_prediction_time_variance() ** 0.5

    def compute_total_stage_count(self) -> int:
        stage_count = 0
        for scenario_result in self.scenario_results:
            stage_count += len(scenario_result.stage_results)
        return stage_count

    def print_stats(self):
        print(f"===== Evaluation Results =====")
        print(f"-- Time --")
        print(f" Total stage count: {self.compute_total_stage_count()}")
        print(f" Total evaluation time (s): {self.evaluation_time}")
        print(f" Total prediction time (s): {self.compute_total_prediction_time()}")
        print(f" Mean prediction time (s): {self.compute_mean_prediction_time()}")
        print(f" Prediction time variance: {self.compute_prediction_time_variance()}")
        print(f" Prediction time std deviation: {self.compute_prediction_time_std_deviation()}")
        print(f" Mean test time (s): {self.compute_mean_test_time()}")
        print(f" Test time variance: {self.compute_test_time_variance()}")
        print(f" Test time std deviation: {self.compute_test_time_std_deviation()}")
        print(f"-- Confusion Matrix Metrics --")
        print(f" Total true positives: {self.compute_total_true_positive_count()}")
        print(f" Total false positives: {self.compute_total_false_positive_count()}")
        print(f" Total false negatives: {self.compute_total_false_negative_count()}")
        print(f" Total true negatives: {self.compute_total_true_negative_count()}")
        print(f" In total {self.compute_total_true_positive_count() + self.compute_total_false_positive_count() + self.compute_total_false_negative_count() + self.compute_total_true_negative_count()} tests")
        print(f"-- Evaluation Metrics --")
        print(f" Total accuracy: {self.compute_total_accuracy()}")
        print(f" Total precision: {self.compute_total_precision()}")
        print(f" Total recall: {self.compute_total_recall()}")
        print(f" Total F1 score: {self.compute_total_f1_score()}")
        print(f"=============================")