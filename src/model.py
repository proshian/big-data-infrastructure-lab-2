import sys

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


def load_model(config, model_name, logger) -> torch.nn.Module:
    mol_path = config[model_name]["model_optimizer_loss_dict_path"]
    try:
        mol = torch.load(mol_path)
    except KeyError:
        logger.exception("Error during loading the model. " 
                         f"Is {model_name} in {model_name}?")
        sys.exit(1)
    except FileNotFoundError:
        logger.exception(f'File {mol_path} is missing')
        sys.exit(1)
    model = mol['model']
    model.eval()
    return model