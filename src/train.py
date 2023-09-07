import pandas as pd

from dataset import SonarDataset
from logger import Logger


if __name__ == "__main__":
    train_dataset = SonarDataset(
        pd.read_csv("data/X_train.csv", index_col=0),
        pd.read_csv("data/y_train.csv", index_col=0))
    test_dataset = SonarDataset(
        pd.read_csv("data/X_test.csv", index_col=0),
        pd.read_csv("data/y_test.csv", index_col=0))
    