from prediction.predictor import TestPredictor


class AbstractPredictor(TestPredictor):

    def predict(self, old_program, new_program):
        raise NotImplementedError
    