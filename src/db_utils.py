import greenplumpython as gp

def write_data_from_csv_to_db(db: gp.Database,
                              csv_path: str,
                              table_name: str,
                              has_header: bool):
    with db._conn.cursor() as curs:
        with open(csv_path, 'r') as f:
            if has_header:
                next(f)
            curs.copy_from(f, table_name, sep=',', null='')