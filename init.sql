CREATE TABLE frequencies 
(
    id          SERIAL NOT NULL PRIMARY KEY,
    freq_1      FLOAT  NOT NULL,
    freq_2      FLOAT  NOT NULL,
    freq_3      FLOAT  NOT NULL,
    freq_4      FLOAT  NOT NULL,
    freq_5      FLOAT  NOT NULL,
    freq_6      FLOAT  NOT NULL,
    freq_7      FLOAT  NOT NULL,
    freq_8      FLOAT  NOT NULL,
    freq_9      FLOAT  NOT NULL,
    freq_10     FLOAT  NOT NULL,
    freq_11     FLOAT  NOT NULL,
    freq_12     FLOAT  NOT NULL,
    freq_13     FLOAT  NOT NULL,
    freq_14     FLOAT  NOT NULL,
    freq_15     FLOAT  NOT NULL,
    freq_16     FLOAT  NOT NULL,
    freq_17     FLOAT  NOT NULL,
    freq_18     FLOAT  NOT NULL,
    freq_19     FLOAT  NOT NULL,
    freq_20     FLOAT  NOT NULL
);


CREATE TABLE predictions
(
    id          SERIAL NOT NULL PRIMARY KEY,
    frequencies_id INT NOT NULL,
    prediction  TEXT  NOT NULL,
    probability FLOAT NOT NULL,
    FOREIGN KEY (frequencies_id) REFERENCES frequencies (id)
);

-- мб добавить колонку с папкой эксперимента / гиперпараметрами