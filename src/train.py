import configparser
import os
import sys
from typing import Tuple, Optional, Dict, List

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
# import matplotlib.pyplot as plt
from tqdm import tqdm

from dataset import SonarDataset
from logger import Logger
from model import MlpSonarModel


CONFIG_NAME = "config.ini"


class Trainer:
    """
    Trains model, saves information about training

    The aim of the class is to incapsulate all the training process.
    It should be able to:
    - train model for given number of epochs
    - save Trainer state
        - model parameters
        - optimizer state
        - metric and loss history
        - epoch number 
    - load Trainer states
    - resume training from saved state

    
    -other possible features:
        - early stopping
        - learning rate scheduler
        - logging
        - tensorboard support

        
    Arguments:
    ----------
    model: nn.Module
    optimizer: torch.optim.Optimizer
    criterion: nn.Module
    best_state_save_path: str
        Path to save Trainer state with the lowest validation loss.
    scheduled_state_save_path: str
        Path to save Trainer state once 'save_period' epoches.
    save_period: int
        Number of epochs between saving Trainer state
    log_period: int
        number of epochs between logging
    device: torch.device
        device to train on
    """
    def __init__(self, model: nn.Module, optimizer: torch.optim.Optimizer,
                 criterion: nn.Module, dataloaders: Dict[str, DataLoader],
                 best_state_save_path: Optional[str] = None,
                 scheduled_state_save_path: Optional[str] = None,
                 save_period: int = 0, log_period: int = 5,
                 device: Optional[torch.device] = None
                 ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scheduled_state_save_path = scheduled_state_save_path
        self.save_period = save_period
        if self.save_period != 0 and self.scheduled_state_save_path is not None:
            raise ValueError("`scheduled_state_save_path` should be a `str` " \
                             "if `save_period` is other than `0`")
        self.best_state_save_path = best_state_save_path
        self.log_period = log_period
        self.epoch = 0
        self.dataloaders = dataloaders
        self.model = self.model.to(self.device)

        self.phases = ['train', 'val']
        
        self.phase_history_keys = ['f1_score', 'accuracy', 'loss']
        self.history = {
            phase_name: {
                key: [] for key in self.phase_history_keys
            } for phase_name in self.phases
        }

        self.best_val_loss = float('inf')

        # logger_getter = Logger(show=False, filename='trainer.log')
        # self.logger = logger_getter.get_logger(__name__ + '.model_training')
        

    def train(self, n_epochs: int, plot_history: bool = False):
        epoch_pbar = tqdm(range(n_epochs), position=0, leave = True, desc='Epochs')
        for _ in epoch_pbar:
            epoch_pbar_str = f'epoch {self.epoch} '
            for phase in self.phases:
                running_loss = 0
                all_lables = []
                all_pred_logits = []

                if phase == 'train':
                    self.model.train()
                else:
                    self.model.eval()

                with torch.set_grad_enabled(phase == 'train'):
                    batch_pbar = tqdm(self.dataloaders[phase], position=1, 
                                      leave = False,
                                      desc=f"E{self.epoch} {phase.upper()} " \
                                      "Batches")
                    for X, y in batch_pbar:
                        X = X.to(self.device)
                        y = y.to(self.device)
                        out = self.model(X)

                        loss = self.criterion(out, y)
                        
                        if phase == 'train':
                            self.optimizer.zero_grad()
                            loss.backward()
                            self.optimizer.step()

                        running_loss += loss.item()
                        all_lables.extend(list(y.flatten().cpu().numpy()))
                        all_pred_logits.extend(list(out.detach().cpu().numpy()))
                        
                        batch_pbar.set_postfix_str(f'loss {loss.item():.3f}')
                
                avg_loss = running_loss / len(self.dataloaders[phase])

                metrics = self.get_metrics(all_lables, all_pred_logits)
                metrics['loss'] = avg_loss

                metric_str_list = [f'{m_name}: {m_value:.3f}'
                    for m_name, m_value in metrics.items()]
                metrics_str = f"{', '.join(metric_str_list)}"

                epoch_pbar_str += f' {phase}: {metrics_str}'

                epoch_pbar.set_postfix_str(epoch_pbar_str)

                for metric_name, metric_value in metrics.items():
                    self.history[phase][metric_name].append(metric_value)

                # ! I don't think I should log this.
                # I can just save whol trainer state or history dict.
                #
                # if self.epoch % self.log_period == 0:
                #     self.log(epoch_pbar_str)
                
                running_loss = 0

                if (self.best_state_save_path 
                        and phase == 'val' and avg_loss < self.best_val_loss):
                    self.best_val_loss = avg_loss
                    self.save(self.best_state_save_path)
            
            if self.save_period and self.epoch % self.save_period == 0:
                self.save(self.save_path)
            
            if plot_history:
                self.plot_history()

            self.epoch += 1

    def save(self, path: str) -> None:
        # We save whole model and optimizer instead of
        # state_dicts because this is a robust way
        # to save trainer state even if we update model
        # and optimizer.
        torch.save({
            'epoch': self.epoch,
            'model': self.model,
            'optimizer': self.optimizer,
            'history': self.history
        }, path)

    def load(self, path: str) -> None:
        checkpoint = torch.load(path)
        self.epoch = checkpoint['epoch']
        # self.model.load_state_dict(checkpoint['model_state_dict'])
        # self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.model = checkpoint['model']
        self.optimizer = checkpoint['optimizer']
        self.history = checkpoint['history']
        self.model.to(self.device)
    
    # def log(self, metrics_str: str):
    #     # writer.add_scalar('{phase} loss',
    #     #                     loss,
    #     #                     global_step = self.epoch)  # global_step=epoch * len(trainloader) + i)
    #     self.logger.info(
    #         f"Epoch {self.epoch}. {metrics_str}
    #     )

    def get_metrics(self,
                    all_lables: List[float],
                    all_preds_logits: List[np.ndarray[float]]
                    ) -> Dict[str, float]:
        preds = np.argmax(all_preds_logits, axis=1)
        return {
            'accuracy': accuracy_score(all_lables, preds),
            'f1_score': f1_score(all_lables, preds, average='macro')
        }
    
    def validate(self) -> float:
        """Returns loss on validation dataset"""
        running_loss = 0.0
        with torch.no_grad():
            for seqs, labels in self.dataloaders['val']:
                seqs = seqs.to(self.device)
                labels = labels.to(self.device)
                out = self.model(seqs)
                running_loss += self.criterion(out.permute(0, 2, 1), labels).item()
        
        return running_loss / len(self.dataloaders['val'])

    
    # def plot_history(self, figsize: Tuple[int, int] = (10, 5)):
    #     metric_names = self.phase_history_keys
    #     fig, axs = plt.subplots(
    #         len(self.phases), len(metric_names),
    #         sharex=True, figsize=figsize, dpi=80)
    #     for i, phase in enumerate(self.phases):
    #         for j, metric in enumerate(metric_names):
    #             axs[i, j].plot(self.history[phase][metric])
    #             axs[i, j].set_title(f'{phase} {metric}')
    #     plt.show()


def get_dataloaders(train_batch_size: Optional[int] = None,
                    test_batch_size: Optional[int] = None
                    ) -> Dict[str, DataLoader]:
    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)
       
    train_dataset = SonarDataset(
        config["SPLIT_DATA"]['X_train'],
        config["SPLIT_DATA"]['y_train'])
   
    test_dataset = SonarDataset(
        config["SPLIT_DATA"]['X_test'],
        config["SPLIT_DATA"]['y_test'])
    
    # Datasets are tiny currently. 166 lines at most.
    # Thus using full dataset as a batch.
    train_batch_size = train_batch_size or len(train_dataset)
    test_batch_size = test_batch_size or len(test_dataset)

    loaders = {
        'train': DataLoader(
            train_dataset, batch_size=train_batch_size, shuffle=True),
        'val': DataLoader(test_dataset, batch_size=test_batch_size)
    }

    return loaders


if __name__ == "__main__":
    torch.manual_seed(0)

    expirements_dir = os.path.join('.', 'experiments')

    if not os.path.exists(expirements_dir):
        os.mkdir(expirements_dir)
   

    logger_getter = Logger(show=True)
    logger = logger_getter.get_logger(__name__)

    model_name = 'mlp'
    
    dataloaders = get_dataloaders()

    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)


    model_params = {
        'input_size': 60,
        'hidden_size': 40,
        'output_size': 2,
    }
    model = MlpSonarModel(**model_params)

    lr = 0.01
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    criterion = torch.nn.CrossEntropyLoss()

    try:
        trainer = Trainer(
            model, optimizer, criterion, dataloaders, log_period = 5)
        logger.info("Trainer created")
    except:
        logger.exception("Exception during trainer cretion")
        sys.exit(1)
    
    n_epoches = 80
    
    try:
        trainer.train(n_epoches)
        logger.info(f"Training {model_name} complete")
    except:
        logger.exception("Exception during training {model_name}")

    config_model_data = model_params.copy()
    config_model_data['lr'] = lr


    model_optimizer_criterion_dict_name = 'mlp_adam_ce'
    save_path = os.path.join(
        expirements_dir, model_optimizer_criterion_dict_name + '.pkl')
    model_optimizer_criterion_dict = {
        'model': model,
        'criterion': criterion,
        'optimier': optimizer
    }
    torch.save(model_optimizer_criterion_dict, save_path)

    config_model_data['model_optimizer_loss_dict_path'] = save_path

    config[model_name] = config_model_data

    with open(CONFIG_NAME, 'w') as configfile:
            config.write(configfile)
    
    logger.info(f"Saved trained model and other artifacts to {save_path}")

    # trainer.plot_history()
