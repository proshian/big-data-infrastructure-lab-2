import sys; import os; sys.path.insert(1, os.path.join(os.getcwd(), "src"))

import unittest

import numpy as np

from logger import Logger
from prepare_data import DataPreparer, ArgsParser


class TestDataPreparer(unittest.TestCase):

    def setUp(self) -> None:
        logger_getter = Logger(show=True)
        self.logger = logger_getter.get_logger(__name__)
        args_parser = ArgsParser(self.logger)
        self.args = args_parser.get_default_args()
        self.data_preparer = DataPreparer(
            self.args["orig_data_filename"],
            self.args["save_path"],
            self.logger)

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
        
        # Можно еще проверить типы данных в массивах.
        # Но я еще не определился, метки будут строками или int'ами.

    # ! To be implemented
    # def test_split_data__determinism(self):
    #     """
    #     Checks that split_data output files are same after 1st and 2nd runs.
    #     """
        
        

if __name__ == "__main__":
    unittest.main()
