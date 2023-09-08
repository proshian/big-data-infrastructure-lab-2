from collections import Counter

import torch
import numpy as np  # For type hints.


class SonarDataset(torch.utils.data.Dataset):
    i2label = ['R', 'M']
    label2i = {label: i for i, label in enumerate(i2label)}

    def __init__(self, X_csv_path: str, y_csv_path: str) -> None:
        X = np.loadtxt(X_csv_path, delimiter=",", dtype=float)
        y_strs = np.loadtxt(y_csv_path, delimiter=",", dtype=str)
        y_list  = list(map(self.label2i.get, y_strs))
        
        self.y = torch.tensor(y_list, dtype = torch.long, requires_grad=False)
        self.X = torch.tensor(X, dtype = torch.float32, requires_grad=False)
        
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    
    def get_classes_distribution(self):
        return Counter(map(lambda i: self.i2label[int(i)], self.y.numpy().flatten()))