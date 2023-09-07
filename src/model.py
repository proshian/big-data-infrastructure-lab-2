import torch

class MlpSonarModel(torch.nn.Module):
    def __init__(self,  
                 input_size: int = 60,
                 hidden_size: int = 40,
                 output_size: int = 2) -> None:
        super().__init__()
        
        self.model = torch.nn.Sequential(
            torch.nn.Linear(input_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_size, output_size),
            torch.nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)