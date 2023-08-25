import os
import argparse
import sys
import traceback
from typing import Optional, Tuple

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from logger import Logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orig_data_filename", "-d", type=str, default=r"./data/sonar.all-data")
    parser.add_argument("--test_size", "-t", type=float, default=0.2)
    parser.add_argument("--random_state", "-r", type=int, default=42)
    parser.add_argument("--save_path", "-s", type=str, default=r"./data")
    return parser.parse_args()


class DataPreparer:
    def __init__(self, orig_data_filename, save_path) -> None:
        logger_getter = Logger(show=True)
        self.logger = logger_getter.get_logger(__name__)

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
    args = parse_args()
    data_preparer = DataPreparer(args.orig_data_filename, args.save_path)
    data_preparer.split_data(test_size=args.test_size, random_state=args.random_state)