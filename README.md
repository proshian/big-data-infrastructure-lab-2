# Классический жизненный цикл разработки моделей машинного обучения

![Здесь должен быть статус CI и CD](https://github.com/proshian/big-data-infrastructure-lab-1/actions/workflows/CI%20CD.yml/badge.svg)

Данный проект имеет цель на элементарной задаче потренироваться ставить воспроизводимые эксперименты с моделями машинного обучения. В проекте используется DVC для версионирования данных и моделей и хранения их в удаленном хранилище. Для CI/CD используется github actions. Эксперименты запускаются в docker контейнере, что позволяет легко переносить их на другие машины и воспроизводить эксперименты в одинаковых условиях.

## Данные

В качестве датасета был использован [Connectionist Bench (Sonar, Mines vs. Rocks)](https://archive.ics.uci.edu/dataset/151/connectionist+bench+sonar+mines+vs+rocks). Датасет содержит 208 объектов, каждый из которых описывается 60 признаками. Признаки - амплитуды частот звукового сигнала, отраженного от объекта. Каждый объект принадлежит к одному из двух классов: `R` - камень, `M` - мина (металлический цилиндр).

## Модель

В качестве модели был выбран многослойный [перцптрон с одним скрытым слоем](./src/model.py).

## Скрипты

В [notebooks/classification_rocks_vs_mines.ipynb](./notebooks/classification_rocks_vs_mines.ipynb) произведено обучение модели на представленном датасете. В данном блокноте код написан максимльно просто, его цель - "схематично" продемонстрировать пайплайн минимальными средставами. 

Этот блокнот был переписан в виде множества скриптов, которые находятся в папке [src](./src)

* [train.py](./src/train.py)
* [logger.py](./src/logger.py)
* [model.py](./src/model.py)
* [prepare_data.py](./src/prepare_data.py)
* [dataset.py](./src/dataset.py)
* [functional_test.py](./src/functional_test.py)

## DVC

DVC используется для версионирования исходных данных `data/sonar.all-data` и модели `experiments/mlp_adam_ce.pkl`.

В качестве remote хранилища была создана папка на google drive с id `1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY`. Всем в интернете был дан доступ на чтение google drive папки, благодаря чему любой авторизованный в google drive пользователь может производить команды `dvc get . data/sonar.all-data` и `dvc pull`. DVC автоматически генерирует ссылку на Google OAuth2 при первом выполнении одной из данных команд. 

DVC команды, которые были использованы для добавления удаленного хранилища и сохранения на нем первых версий отслеживаемых файлов:

```bash
dvc init
dvc remote add -d myremote gdrive://1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY
dvc remote modify myremote gdrive_acknowledge_abuse true
dvc add data/sonar.all-data
dvc add experiments/mlp_adam_ce.pkl
dvc push

git add data/sonar.all-data.dvc data/.gitignore experiments/mlp_adam_ce.pkl experiments/.gitignore
```

Для CI/CD был создан Google Cloud проект, в котором был создан service account. Service account'у были даны права на редактирование папки, являющейся remote хранилищем. Json ключ от service accaunt'а был закодирован base64 и записан в github secrets.

Более подробно с произведенной настройкой можно ознакомиться в [официальной документации](https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive) (разделы `Using a custom Google Cloud project (recommended)` и `Using service accounts`)
 
## Docker

На этапе CI производится сборка docker образа и его отправка в docker hub. В docker образ не включены файлы, отслеживаемые dvc.

На этапе CD на runner'е создается файл с ключом от google service аккаунта, производится dvc pull, который скачивает файл `data/sonar.all-data`, выполнются `docker-compose pull` и `docker-compose up`, в результате чего запускаются скрипты и тесты. Файл `data/sonar.all-data` оказывается доступен внутри контейнера благодаря volume монтированию.


Локально можно собрать docker образ командой:

```bash
docker build -t proshian/bd1 .
```

Далее произвести dvс pull:
```bash
dvc pull
```

Произвести аутентификаицю в google drive, если она не была произведена ранее (OAuth2 ссылка будет сгенерирована автоматически).

Далее выполнить docker-compose up:
```bash
docker-compose up
```
