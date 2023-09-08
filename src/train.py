import configparser
from typing import Tuple, Optional

import pandas as pd
from torch.utils.data import DataLoader 

from dataset import SonarDataset
from logger import Logger


CONFIG_NAME = "config.ini"


def get_dataloaders(train_batch_size: Optional[int] = None,
                    test_batch_size: Optional[int] = None
                    ) -> Tuple[DataLoader, DataLoader]:
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
       
    train_dataset = SonarDataset(
        pd.read_csv(config["SPLIT_DATA"]['X_train'], index_col=0),
        pd.read_csv(config["SPLIT_DATA"]['y_train'], index_col=0))
   
    test_dataset = SonarDataset(
        pd.read_csv(config["SPLIT_DATA"]['X_test'], index_col=0),
        pd.read_csv(config["SPLIT_DATA"]['y_test'], index_col=0))
    
    # Datasets are tiny currently. 166 lines at most.
    # Thus using full dataset as a batch.
    train_batch_size = train_batch_size or len(train_dataset)
    test_batch_size = test_batch_size or len(test_dataset)

    train_loader = DataLoader(
        train_dataset, batch_size=train_batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=test_batch_size)

    return train_loader, test_loader


if __name__ == "__main__":
    logger_getter = Logger(show=True)
    logger = logger_getter.get_logger(__name__)
    
    train_loader, test_loader = get_dataloaders()