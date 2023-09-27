"""
Reads data from greenplum database, uses a trained model to make predictions,
and writes the predictions back to the database.
"""

import argparse
import configparser
import io

import greenplumpython as gp
import pandas as pd
import torch
import numpy as np

from model import load_model
from db_utils import write_to_table
from dataset import SonarDataset
from logger import Logger


SHOW_LOG = True
CONFIG_NAME = 'config.ini'
MODEL_NAME = 'mlp'
DATA_TABLE = 'frequencies'
PREDICTIONS_TABLE = 'predictions'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-host", type=str, required=True)
    parser.add_argument("--db-port", type=int, required=True)
    parser.add_argument("--db-user", type=str, required=True)
    parser.add_argument("--db-password", type=str, required=True)
    parser.add_argument("--db-name", type=str, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    logger_getter = Logger(SHOW_LOG)
    logger = logger_getter.get_logger(__name__)

    config = configparser.ConfigParser()
    config.read(CONFIG_NAME)

    args = parse_args()

    logger.debug(f"Creating Database object")

    params = dict(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_password
    )

    db = gp.Database(params=params)
    logger.debug(f"Created Database object")


    with db._conn.cursor() as curs:
        curs.execute(
            "select column_name, data_type " \
            "from INFORMATION_SCHEMA.COLUMNS " \
            "where table_name = 'predictions';")
        prediction_table_columns = curs.fetchall()
        logger.debug(f"prediction_table_columns: {prediction_table_columns}")
    
    
    X = gp.DataFrame.from_table(DATA_TABLE, db=db)

    # print(X.where(lambda df: df["frequencies_id"] == 1))
    

    X = pd.DataFrame(X)

    X = X.rename(columns={"id": "frequencies_id"})

    logger.debug(f"X.columns = {X.columns}")

    preds_gp = gp.DataFrame.from_table(PREDICTIONS_TABLE, db=db)

    preds_df = pd.DataFrame(preds_gp)
    
    if len(preds_df) == 0:
        logger.debug("preds_df is empty")
        preds_df = pd.DataFrame(columns = ['prediction_id', 'frequencies_id', 'prediction', 'm_probability'])


    merged_df = X.join(
        preds_df, how = 'left', on = "frequencies_id", rsuffix="_pred_table")
    merged_df= merged_df.drop('frequencies_id_pred_table', axis = 1)

    logger.debug(f"merged_df.columns = {merged_df.columns}")

    n_freqs = 60
    data_np = merged_df[[f'freq_{i}' for i in range(n_freqs)]].values

    freq_ids_np = merged_df[['frequencies_id']].values

    data_torch = torch.tensor(data_np, dtype = torch.float32, requires_grad=False)

    model = load_model(config, MODEL_NAME, logger)

    outs = model(data_torch)
    outs_np = outs.numpy(force = True)

    m_index = SonarDataset.label2i['M']
    m_probs = outs_np[:, m_index]

    preds = outs_np.argmax(axis = 1)

    logger.debug(f"preds.shape = {preds.shape}")
    logger.debug(f"m_probs.shape = {m_probs.shape}")
    logger.debug(f"freq_ids_np.shape = {freq_ids_np.shape}")

    preds = [SonarDataset.i2label[pred] for pred in preds]

    abscent_pred_table_data = pd.DataFrame(
        {
            'frequencies_id': freq_ids_np.reshape(-1),
            'prediction': preds,
            'm_probability': m_probs.reshape(-1)
        }
    )
    
    logger.debug(f"preparing to wite data:\n{abscent_pred_table_data.head()}\netc.")

    write_to_table(db, abscent_pred_table_data, PREDICTIONS_TABLE)

    preds_gp = gp.DataFrame.from_table(PREDICTIONS_TABLE, db=db)

    preds_gp_df = pd.DataFrame(preds_gp)

    logger.debug(f"reading data from table:\n{preds_gp_df.head()}\netc.")