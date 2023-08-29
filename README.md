# ЛР 1. Классический жизненный цикл разработки моделей машинного обучения

## Данные

В качестве датасета был использован [Connectionist Bench (Sonar, Mines vs. Rocks)](https://archive.ics.uci.edu/dataset/151/connectionist+bench+sonar+mines+vs+rocks). Датасет содержит 208 объектов, каждый из которых описывается 60 признаками. Признаки - амплитуды частот звукового сигнала, отраженного от объекта. Каждый объект принадлежит к одному из двух классов: `R` - камень, `M` - мина (металлический цилиндр).

<!-- ## Модель и ее обучение -->

# DVC

На данный момент DVC используется для версионирования файла `data/sonar.all-data`.

В качестве remote хранилища была создана папка на google drive с id `1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY`. Всем в интернете был дан доступ на чтение google drive папки, чтобы у всех работали команды `dvc get . data/sonar.all-data` и `dvc pull`.

DVC команды, которые были использованы для добавления удаленного хранилища и сохранения на нем первой версии `data/sonar.all-data`:

```bash
dvc init
dvc remote add -d myremote gdrive://1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY
dvc remote modify myremote gdrive_acknowledge_abuse true
dvc add data/sonar.all-data
dvc push

git add data/sonar.all-data.dvc data/.gitignore
```

# DVC TODO
! Напоминалка для меня из будущего: Когда будет настраиваться CI/CD для `prepare_data.py`, нужно будет произвести шаги `Using a custom Google Cloud project (recommended)` и `Using service accounts` из [официальной документации по испоьзованию google drive в качестве удаленного хранилища dvc](https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive#using-a-custom-google-cloud-project-recommended)

 
# TODO
1. Сделать unittest для `prepare_data.py`
    * Проверить, что выходом является `tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]`
    * Проверить, что файлы созданы и соответствуют тому, что записалось в config
    * Проверить, что созданные датасеты парсятся pandas
2. Переписать predare_data.py
    * Aргументы `__init__` и `split_data` должны браться из config'а
    * Убрать argparse
    * Добавить запись в конфиг путей до созданного датасета
3. Создать CI pipeline (Jenkins, Team City, Circle CI и др.) для сборки docker image и отправки его на DockerHub, сборка должна автоматически  стартовать по pull request в основную ветку репозитория модели;
4. Создать CD pipeline для запуска контейнера и проведения функционального тестирования по сценарию, запуск должен стартовать  по требованию или расписанию или как вызов с последнего этапа CI pipeline;