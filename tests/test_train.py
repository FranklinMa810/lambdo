import unittest

import sklearn.preprocessing  # To get rid of ImportWarning
from sklearn import linear_model

from lambdo.Workflow import *

#
# Train functions for testing
#
def transform_func_1(value, model_param):  # It consumes model generated by the training function
    return value + model_param

def train_func_1(value):  # Retrun constant model (no data is needed to train it)
    trained_model = {"model_param": 1.0}
    return trained_model

def regression_predict(X, model):
    X_array = X.values
    y = model.predict(X_array.reshape(-1, 1))
    return pd.DataFrame(y)

def regression_fit(X, y):
    X_array = X.values
    y_array = y.values
    model = linear_model.LinearRegression()
    model.fit(X_array, y_array)
    return model


class TrainTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_custom(self):
        wf_json = {
            "id": "My workflow",
            "tables": [
                {
                    "id": "My table",
                    "columns": [
                        {
                            "id": "My column",
                            "function": "test_train:transform_func_1",
                            "scope": "one",
                            "inputs": ["A"],
                            "train": {
                                "function": "test_train:train_func_1",
                                "outputs": []
                            }
                        }
                    ]
                }
            ]
        }
        wf = Workflow(wf_json)

        # Provide data directly (without table population)
        data = {'A': [1, 2, 3]}
        df = pd.DataFrame(data)
        tb = wf.tables[0]
        tb.data = df

        wf.execute()

        self.assertAlmostEqual(wf.tables[0].data['My column'][0], 2.0)
        self.assertAlmostEqual(wf.tables[0].data['My column'][1], 3.0)
        self.assertAlmostEqual(wf.tables[0].data['My column'][2], 4.0)

    def test_regression(self):
        wf_json = {
            "id": "My workflow",
            "tables": [
                {
                    "id": "My table",
                    "columns": [
                        {
                            "id": "My column",
                            "function": "test_train:regression_predict",
                            "scope": "all",
                            "inputs": ["A"],
                            "outputs": ["B"],
                            "train": {
                                "function": "test_train:regression_fit"
                            }
                        }
                    ]
                }
            ]
        }
        wf = Workflow(wf_json)

        # Provide data directly (without table population)
        data = {'A': [1, 2, 3, 4], 'B': [1, 3, 3, 1]}
        df = pd.DataFrame(data)
        tb = wf.tables[0]
        tb.data = df

        wf.execute()

        self.assertAlmostEqual(tb.data['B'][0], 2.0)
        self.assertAlmostEqual(tb.data['B'][1], 2.0)
        self.assertAlmostEqual(tb.data['B'][2], 2.0)
        self.assertAlmostEqual(tb.data['B'][3], 2.0)

        pass

if __name__ == '__main__':
    unittest.main()
