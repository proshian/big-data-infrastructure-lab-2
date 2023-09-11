import sys; import os; sys.path.insert(1, os.path.join(os.getcwd(), "src"))

import unittest
import configparser

import torch

from dataset import SonarDataset


CONFIG_PATH = "config.ini"


class TestDataset(unittest.TestCase):

    def setUp(self) -> None:        
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)
        self.train_dataset = SonarDataset(
            self.config["SPLIT_DATA"]['X_train'],
            self.config["SPLIT_DATA"]['y_train'],
        )

        self.test_dataset = SonarDataset(
            self.config["SPLIT_DATA"]['X_test'],
            self.config["SPLIT_DATA"]['y_test'],
        )

    def test_dtype(self):
        """
        Checks that data types of dataset instances are correct
        in test and train datasets.
        """
        for dataset in [self.train_dataset, self.test_dataset]:
            for X, y in dataset:
                self.assertEqual(X.dtype, torch.float32)
                self.assertEqual(y.dtype, torch.long)

    def test_same_shape(self):
        shapes = set()

        for dataset in [self.train_dataset, self.test_dataset]:
            for X, y in dataset:
                shapes.add((X.shape, y.shape))
        
        self.assertEqual(len(shapes), 1)
        
        

if __name__ == "__main__":
    unittest.main()
