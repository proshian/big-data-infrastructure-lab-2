import numpy as np

FILE_PATH = r"./data/sonar.all-data"

CREATE_PRED_TABLE_STATEMENT = \
"""
CREATE TABLE predictions
(
    id          SERIAL NOT NULL PRIMARY KEY,
    frequencies_id INT NOT NULL,
    prediction  TEXT  NOT NULL,
    probability FLOAT NOT NULL,
    FOREIGN KEY (frequencies_id) REFERENCES frequencies (id)
);
"""


def get_create_frequencies_statement(col_names) -> str:
    statement = """CREATE TABLE frequencies (
    id          SERIAL NOT NULL PRIMARY KEY,"""
    
    for col_name in col_names:
        statement += f"\n    {col_name}      FLOAT  NOT NULL,"
    
    statement = statement[:-1]

    statement += "\n);"

    return statement


def get_fill_freq_table_statements(X, col_names) -> str:
    statement = "INSERT INTO frequencies " + \
        f"({', '.join(col_names)}) " + \
        "VALUES"
    for i, row in enumerate(X):
        statement += '\n' + "    (" + ", ".join(row) + ")"
        if i != len(X) - 1:
            statement += ","
        else:
            statement += ";"
    
    return statement
    


if __name__ == "__main__":
    data = np.loadtxt(FILE_PATH, delimiter=",", dtype = str)

    X = data[:, :-1]

    rows, cols = X.shape

    col_names = [f"freq_{i}" for i in range(cols)]

    create_freq_table_statement = get_create_frequencies_statement(col_names)

    fill_freq_statement = get_fill_freq_table_statements(X, col_names)

    with open("init.sql", 'w') as f:
        f.write(f"{create_freq_table_statement}\n{CREATE_PRED_TABLE_STATEMENT}\n{fill_freq_statement}")
