import os
import argparse
import sys
import traceback
import configparser
from typing import Dict, Tuple, Optional, Any
import logging  # To set logging level

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from logger import Logger


CONFIG_NAME = "config.ini"
SCRIPT_PARAMS_NAME = "PREPARE_DATA_PARAMETERS"


class ArgsParser:
    """
    Encapsulates and groups together parse_args method and helper methods.
    """
    def __init__(self, logger):
        self.logger = logger

    def get_default_args(self) -> Dict[str, str]:
        """
        Gets DataPreparer args from config file.

        Args from previous run are stored in config file. If an arg was not
        specified as a command line argument it is taken from config file.
        """
        config = configparser.ConfigParser()
        config.read(CONFIG_NAME)
        default_args = config[SCRIPT_PARAMS_NAME]
        
        default_args_dict: Dict[str, str] = {
            d_arg: default_args[d_arg] for d_arg in default_args}

        default_args_dict["random_state"] = int(default_args_dict["random_state"])
        default_args_dict["test_size"] = float(default_args_dict["test_size"])

        return default_args_dict

    def _update_configfile(self, args) -> None:
        """
        Saves DataPreparer args to config file.
        """
        config = configparser.ConfigParser()
        config.read(CONFIG_NAME)

        if SCRIPT_PARAMS_NAME not in config:
            self.logger.info(f"{SCRIPT_PARAMS_NAME} not in {CONFIG_NAME}")
            config[SCRIPT_PARAMS_NAME] = {}
            
        for arg in vars(args):
            config[SCRIPT_PARAMS_NAME][arg] = str(getattr(args, arg))
        
        with open(CONFIG_NAME, 'w') as configfile:
            config.write(configfile)

    def _check_all_args_non_null(self, args):
        """
        Checks that all args values are not None after parsing
        """
        for arg in vars(args):
            if getattr(args, arg) is None:
                self.logger.error(f"Argument {arg} is missing")
                return False
        self.logger.info("All arguments obtained")
        return True

    def parse_args(self) -> argparse.Namespace:
        """
        Parses arguments
        
        All arguments are optional and default to config values.
        If an argument is not provided and it cannot be found in
        `config.ini`, an error is logged and program exits with code 1.

        After the arguments are parsed `config.ini` is updated.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--orig_data_filename", "-d", type=str)
        parser.add_argument("--test_size", "-t", type=float)
        parser.add_argument("--random_state", "-r", type=int)
        parser.add_argument("--save_path", "-s", type=str)
        parser.add_argument(
            "--log_level",
            "-l",
            type=str,
            default="DEBUG",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

        if os.path.exists(CONFIG_NAME):
            defaults = self.get_default_args()
            parser.set_defaults(**defaults)
        
        args = parser.parse_args()

        if not self._check_all_args_non_null(args):
            sys.exit(1)
        
        for arg in vars(args):
            logger.debug(f"type(args.{arg}) = {type(getattr(args, arg))}")
        
        self._update_configfile(args)

        return args


# That's a class because there might be a more
# sophisticated data obtain pipeline.
class DataPreparer:
    def __init__(self, orig_data_filename, save_path, logger) -> None:
        
        self.logger = logger

        self.orig_data_filename = orig_data_filename
        self.save_path = save_path
        
        self.logger.info(f"Initialized DataPreparer with " \
                         f"orig_data_filename={orig_data_filename}, " \
                         f"save_path={save_path}")


    def split_data(self,
                   df: Optional[pd.DataFrame] = None,
                   test_size: float = 0.2,
                   random_state: int = 42) -> Tuple[np.ndarray, ...]:
        """
        Splits dataset into train and test sets.

        The initial dataset is obtained from either df or filename. Only one of them
        should be not None.

        Arguments:
        ----------
        df: pd.DataFrame
            Dataset to split. It's assumed that the last column
            is the target column.
        filename: str
            Path to the dataset to split. It's assumed that the last column
            is the target column.
        test_size: float
            Fraction of the dataset to be used as test set
        random_state: int
            Random state for reproducibility
        save_path: str
            Path to save splitted data as files:
                Path/X_train.csv,
                Path/X_test.csv,
                Path/y_train.csv,
                Path/y_test.csv
            If None, data is not saved.
        
        Returns:
        --------
        tuple: (X_train, X_test, y_train, y_test)
        X_train: np.ndarray
        X_test: np.ndarray
        y_train: np.ndarray
        y_test: np.ndarray
        """
        config = configparser.ConfigParser()
        config.read(CONFIG_NAME)
        if "SPLIT_DATA" not in config:
            self.logger.info(f"{'SPLIT_DATA'} not in {CONFIG_NAME}")
            config["SPLIT_DATA"] = {}

        try:
            df = pd.read_csv(self.orig_data_filename, header=None)
        except FileNotFoundError:
            # ! Возможно, лучше использовать аргумент exc_info=True
            self.logger.error(f"File {self.orig_data_filename} not found")
            self.logger.error(traceback.format_exc())
            sys.exit(1)

        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values.reshape(-1, 1)

        self.logger.debug(f"X type: {type(X)}")
        self.logger.debug(f"X shape: {X.shape}")
        self.logger.debug(f"X dtype: {X.dtype}")
        self.logger.debug(f"y type: {type(y)}")
        self.logger.debug(f"y shape: {y.shape}")
        self.logger.debug(f"y dtype: {y.dtype}")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y)
        
        for data, data_kind in zip([X_train, X_test, y_train, y_test], 
                            ['X_train', 'X_test', 'y_train', 'y_test']):
            try:
                file_path = os.path.join(self.save_path, f'{data_kind}.csv')
                fmt = '%f'
                if data.dtype == 'object':
                    fmt = '%s'
                np.savetxt(file_path, data, delimiter=',', fmt=fmt)
                self.logger.info(f"Saved {data_kind} to {file_path}")
                # add data_kind: file_path to config 
                config["SPLIT_DATA"][data_kind] = file_path

            except Exception:
                self.logger.error(f"Failed to save {data_kind} to {file_path}")
                self.logger.error(traceback.format_exc())
                sys.exit(1)
        
        with open(CONFIG_NAME, 'w') as configfile:
            config.write(configfile)

        self.logger.info("Train and test data are ready")                

        return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    logger_getter = Logger(show=True)
    logger = logger_getter.get_logger(__name__)

    args_parser = ArgsParser(logger)
    args = args_parser.parse_args()

    numeric_level = getattr(logging, args.log_level.upper(), None)
    logger.setLevel(numeric_level)

    data_preparer = DataPreparer(args.orig_data_filename, args.save_path, logger)
    data_preparer.split_data(test_size=args.test_size, random_state=args.random_state)