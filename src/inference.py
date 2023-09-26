"""
Reads data from greenplum database, uses a trained model to make predictions,
and writes the predictions back to the database.
"""

import argparse

import greenplumpython as gp


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
    args = parse_args()
    db = gp.Database(host=args.db_host,
                     port=args.db_port,
                     dbname=args.db_name,
                     user=args.db_user,
                     password=args.db_password)

    X = gp.DataFrame.from_table(args.db_table, db=db)

    print(X.head())