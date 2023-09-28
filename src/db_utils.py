import greenplumpython as gp
import pandas as pd
import time

def get_row_str(row):
    strs_of_row = [str(el) if type(el) != str else f"'{el}'" for el in row]
    return f'({", ".join(strs_of_row)})'

def write_to_table(db: gp.Database, data_df: pd.DataFrame, table_name:str):
    columns = data_df.columns
    columns_str = ", ".join(columns)
    values = data_df.values
    values_str = ",\n".join(map(get_row_str, values))
    values_str += ";"


    sql_insert = "INSERT INTO " \
        f"{table_name} ({columns_str}) VALUES \n{values_str}"
    
    
    # print("my_statement")

    # print(sql_insert)

    # time.sleep(60)

    with db._conn.cursor() as curs:
        curs.execute(sql_insert)
        # curs.commit()