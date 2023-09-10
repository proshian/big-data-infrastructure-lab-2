import configparser
import sys
import os
import json
from datetime import datetime
import shutil
import yaml

import torch
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

from logger import Logger
from dataset import SonarDataset


SHOW_LOG = True
CONFIG_NAME = 'config.ini'
MODEL_NAME = 'mlp'


def load_model(config, logger) -> torch.nn.Module:
    mol_path = config[MODEL_NAME]["model_optimizer_loss_dict_path"]
    try:
        mol = torch.load(mol_path)
    except KeyError:
        logger.exception("Error during loading the model. " 
                         f"Is {MODEL_NAME} in {CONFIG_NAME}?")
        sys.exit(1)
    except FileNotFoundError:
        logger.exception(f'File {mol_path} is missing')
        sys.exit(1)
    model = mol['model']
    model.eval()
    return model


def functional_test(model, config, logger):
    tests_path = os.path.join('.', "tests")
    exp_path = os.path.join('.', "experiments")
    
    for test in os.listdir(tests_path):
        with open(os.path.join(tests_path, test)) as f:
            try:
                data = json.load(f)
            except FileNotFoundError:
                logger.exception()
                sys.exit(1)

            X = torch.tensor(data['X'], dtype = torch.float32, requires_grad=False)
            y_list = [SonarDataset.label2i[label] for label in data['y']]
            with torch.no_grad():
                probs = model(X)
                probs = probs.numpy()
            preds = np.argmax(probs, axis=1)
            accuracy = accuracy_score(preds, y_list)
            print(f"{MODEL_NAME} passed test {test}")
            
            logger.info(
                f"{MODEL_NAME} passed test {test}")
            
            exp_data = {
                "model": MODEL_NAME,
                "model params": dict(config.items(MODEL_NAME)),
                "accuracy": str(accuracy)
            }

            str_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            exp_dir = os.path.join(exp_path,
                                   f'exp_{test[:-5]}_{str_date}')
            os.mkdir(exp_dir)
            with open(os.path.join(exp_dir,"exp_config.yaml"), 'w') as exp_f:
                yaml.safe_dump(exp_data, exp_f, sort_keys=False)
            shutil.copy(os.path.join(os.getcwd(), "logfile.log"), os.path.join(exp_dir,"exp_logfile.log"))


if __name__ == "__main__":
    logger_getter = Logger(SHOW_LOG)
    logger = logger_getter.get_logger(__name__)

    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)


    model = load_model(config, logger)
    
    functional_test(model)