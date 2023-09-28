import sys; import os; sys.path.insert(1, os.path.join(os.getcwd(), "src"))

import unittest
import configparser

import numpy as np

from logger import Logger
from prepare_data import DataPreparer, ArgsParser


CONFIG_PATH = "config.ini"


class TestDataPreparer(unittest.TestCase):

    def setUp(self) -> None:
        logger_getter = Logger(show=False)
        self.dummy_logger = logger_getter.get_logger(__name__)
        args_parser = ArgsParser(self.dummy_logger)
        self.args = args_parser.get_default_args()
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)
        self.data_preparer = DataPreparer(
            self.args["orig_data_filename"],
            self.args["save_path"],
            self.dummy_logger)

    def test_split_data__type(self):
        """
        Checks that the result of split_data() is a tuple of 4 np.ndarrays
        """
        split_data_result = self.data_preparer.split_data(
            test_size=self.args["test_size"],
            random_state=self.args["random_state"])
        
        self.assertEqual(
            len(split_data_result), 4)
        
        for data in split_data_result:
            self.assertIsInstance(data, np.ndarray)
        
        # Можно еще проверить типы данных в массивах:
        # признаки - float32, метки - str.

    def test_split_data__determinism(self):
        """
        Checks that split_data output files are same after 1st and 2nd runs.
        """
        self.data_preparer.split_data(
            test_size=self.args["test_size"],
            random_state=self.args["random_state"])
        
        split_data_first = (
            self.config["SPLIT_DATA"]['X_train'],
            self.config["SPLIT_DATA"]['y_train'],
            self.config["SPLIT_DATA"]['X_test'],
            self.config["SPLIT_DATA"]['y_test'])

        self.data_preparer.split_data(
            test_size=self.args["test_size"],
            random_state=self.args["random_state"])

        split_data_second = (
            self.config["SPLIT_DATA"]['X_train'],
            self.config["SPLIT_DATA"]['y_train'],
            self.config["SPLIT_DATA"]['X_test'],
            self.config["SPLIT_DATA"]['y_test'])
        
        self.assertTrue(
            np.all(split_data_first == split_data_second)
        )
        

if __name__ == "__main__":
    unittest.main()
