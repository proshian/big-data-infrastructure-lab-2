from collections import Counter

import torch
import pandas as pd  # for type hints


class SonarDataset(torch.utils.data.Dataset):
    i2label = ['R', 'M']
    label2i = {label: i for i, label in enumerate(i2label)}

    def __init__(self, X: pd.DataFrame, labels: pd.DataFrame) -> None:
        y_list = [self.label2i[label] for label in labels]
        self.y = torch.tensor(y_list, dtype = torch.float32, requires_grad=False)
        self.X = torch.tensor(X.values, dtype = torch.float32, requires_grad=False)
        
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    
    def get_classes_distribution(self):
        return Counter(map(lambda i: self.i2label[int(i)], self.y.numpy().flatten()))
    

def get_train_test_datasets(path_to_csv: str, test_size: float = 0.2, random_state: int = 42):
    df = pd.read_csv(path_to_csv, index_col = False, header = None)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    train_dataset = SonarDataset(X_train, y_train)
    test_dataset = SonarDataset(X_test, y_test)
    return train_dataset, test_dataset