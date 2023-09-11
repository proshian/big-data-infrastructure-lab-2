import sys; import os; sys.path.insert(1, os.path.join(os.getcwd(), "src"))

import unittest
import configparser

import torch

from model import MlpSonarModel


CONFIG_PATH = "config.ini"


class TestModel(unittest.TestCase):

    def setUp(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)
        self.model = MlpSonarModel(input_size=60,
                                   hidden_size=40,
                                   output_size=2)

    def test_dtype(self):
        """
        Checks that data types of model parameters are correct.
        """
        for param in self.model.parameters():
            self.assertEqual(param.dtype, torch.float32)
    
    def test_determinism(self):
        """
        Checks that model output is same after 1st and 2nd runs.
        """
        self.model.eval()
        n_samples = 5
        X = torch.randn(n_samples, 60)
        model_output_first = self.model(X)
        model_output_second = self.model(X)
        
        self.assertTrue(torch.equal(model_output_first, model_output_second))
        

if __name__ == "__main__":
    unittest.main()
