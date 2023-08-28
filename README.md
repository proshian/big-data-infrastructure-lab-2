# ЛР 1. Классический жизненный цикл разработки моделей машинного обучения

## Данные

В качестве датасета был использован [Connectionist Bench (Sonar, Mines vs. Rocks)](https://archive.ics.uci.edu/dataset/151/connectionist+bench+sonar+mines+vs+rocks). Датасет содержит 208 объектов, каждый из которых описывается 60 признаками. Признаки - амплитуды частот звукового сигнала, отраженного от объекта. Каждый объект принадлежит к одному из двух классов: `R` - камень, `M` - мина (металлический цилиндр).

<!-- ## Модель и ее обучение -->

# DVC

На данный момент DVC используется для версионирования файла `data/sonar.all-data`.

В качестве remote хранилища была создана папка на google drive с id `1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY`. Чтобы у всех была возможность получить соответствующую версию данных с помощью команды `dvc get . data/sonar.all-data`, к google drive папке был дан доступ на чтение всем в интернете.

DVC команды, которые были использованы для добавления удаленного хранилища и сохранения на нем первой версии `data/sonar.all-data`

```bash
dvc init
dvc remote add -d myremote gdrive://1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY
dvc remote modify myremote gdrive_acknowledge_abuse true
dvc add data/sonar.all-data
dvc push

git add data/sonar.all-data.dvc data/.gitignore
```

