"""
Reads data from greenplum database, uses a trained model to make predictions,
and writes the predictions back to the database.
"""

import argparse
import configparser

import greenplumpython as gp

from model import load_model
from logger import Logger


SHOW_LOG = True
CONFIG_NAME = 'config.ini'
MODEL_NAME = 'mlp'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-host", type=str, required=True)
    parser.add_argument("--db-port", type=int, required=True)
    parser.add_argument("--db-user", type=str, required=True)
    parser.add_argument("--db-password", type=str, required=True)
    parser.add_argument("--db-name", type=str, required=True)
    parser.add_argument("--db-table", type=str, required=True)
    # parser.add_argument("--model-path", type=str, required=True)
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
    
    X = gp.DataFrame.from_table(args.db_table, db=db)

    model = load_model(config, MODEL_NAME, logger)
    

    print(X.head())