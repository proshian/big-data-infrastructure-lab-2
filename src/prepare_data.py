import os
import argparse
import sys
import traceback
import configparser
from typing import Dict, Tuple, Optional, Any

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from logger import Logger


CONFIG_NAME = "config.ini"
SCRIPT_PARAMS_NAME = "PREPARE_DATA_PARAMETERS"


def get_default_args() -> Dict[str, str]:
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
    return config[SCRIPT_PARAMS_NAME]

def update_configfile(args, logger) -> None:
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)

    if SCRIPT_PARAMS_NAME not in config:
        logger.info(f"{SCRIPT_PARAMS_NAME} not in {CONFIG_NAME}")
        config[SCRIPT_PARAMS_NAME] = {}
        
    for arg in vars(args):
        config[SCRIPT_PARAMS_NAME][arg] = str(getattr(args, arg))
    
    with open(CONFIG_NAME, 'w') as configfile:
        config.write(configfile)

def check_all_args_non_null(args, logger):
    for arg in vars(args):
        if getattr(args, arg) is None:
            logger.error(f"Argument {arg} is not specified")
            return False
    logger.info("All arguments specified")
    return True


def parse_args(logger) -> argparse.Namespace:
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

    if os.path.exists(CONFIG_NAME):
        defaults = get_default_args()
        parser.set_defaults(**defaults)
    
    args = parser.parse_args()

    if not check_all_args_non_null(args, logger):
        sys.exit(1)
    
    for arg in vars(args):
        logger.debug(f"type(args.{arg}) = {type(getattr(args, arg))}")
    
    update_configfile(args, logger)

    return args


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
        try:
            df = pd.read_csv(self.orig_data_filename, header=None)
        except FileNotFoundError:
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
        
        for data, name in zip([X_train, X_test, y_train, y_test], 
                            ['X_train', 'X_test', 'y_train', 'y_test']):
            try:
                file_path = os.path.join(self.save_path, f'{name}.csv')
                fmt = '%f'
                if data.dtype == 'object':
                    fmt = '%s'
                np.savetxt(file_path, data, delimiter=',', fmt=fmt)
                self.logger.info(f"Saved {name} to {file_path}")
            except Exception:
                self.logger.error(f"Failed to save {name} to {file_path}")
                self.logger.error(traceback.format_exc())
                sys.exit(1)

        self.logger.info("Train and test data are ready")                

        return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    logger_getter = Logger(show=True)
    logger = logger_getter.get_logger(__name__)
    args = parse_args(logger)
    data_preparer = DataPreparer(args.orig_data_filename, args.save_path, logger)
    data_preparer.split_data(test_size=args.test_size, random_state=args.random_state)