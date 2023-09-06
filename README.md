# ЛР 1. Классический жизненный цикл разработки моделей машинного обучения

## Данные

В качестве датасета был использован [Connectionist Bench (Sonar, Mines vs. Rocks)](https://archive.ics.uci.edu/dataset/151/connectionist+bench+sonar+mines+vs+rocks). Датасет содержит 208 объектов, каждый из которых описывается 60 признаками. Признаки - амплитуды частот звукового сигнала, отраженного от объекта. Каждый объект принадлежит к одному из двух классов: `R` - камень, `M` - мина (металлический цилиндр).

<!-- ## Модель и ее обучение -->

## DVC

На данный момент DVC используется для версионирования файла `data/sonar.all-data`.

В качестве remote хранилища была создана папка на google drive с id `1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY`. Всем в интернете был дан доступ на чтение google drive папки, благодаря чему любой авторизованный в google drive пользователь может производить команды `dvc get . data/sonar.all-data` и `dvc pull`. DVC автоматически генерирует ссылку на Google OAuth2 при первом выполнении одной из данных команд. 

DVC команды, которые были использованы для добавления удаленного хранилища и сохранения на нем первой версии `data/sonar.all-data`:

```bash
dvc init
dvc remote add -d myremote gdrive://1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY
dvc remote modify myremote gdrive_acknowledge_abuse true
dvc add data/sonar.all-data
dvc push

git add data/sonar.all-data.dvc data/.gitignore
```

Для CI/CD был создан Google Cloud проект, в котором был создан service account. Service account'у были даны права на редактирование папки, являющейся remote хранилищем. Ключ от service accaunt'а был (будет) записан в github secrets. Более подробно с произведенной настройкой можно ознакомиться в [официальной документации](https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive) (разделы `Using a custom Google Cloud project (recommended)` и `Using service accounts`)

JSON с ключом от service account'а был закодирован в base64 и сохранен в github secrets.
 
## Docker

На этапе CI производится сборка docker образа и его отправка в docker hub. В docker образ не включен файл `data/sonar.all-data`, он находится в удаленном хранилище. 

На этапе CD на runner'е создается файл с ключом от google service аккаунта, производится dvc pull, который скачивает файл `data/sonar.all-data`, выполнются `docker-compose pull` и `docker-compose up`, в результате чего запускаются скрипты и тесты.


Локально можно собрать docker образ командой:

```bash
docker build -t proshian/bd1 .
```

Далее произвести dvс pull:
```bash
dvc pull
```

Произвести аутентификаицю в google drive, если она не была произведена ранее.

Далее выполнить docker-compose up:
```bash
docker-compose up
```

## TODO

1. Сделать CI, который просто создает образ и пушит его в docker hub
2. Сделать CD, который запускает контейнер, в котором происходит запись json'а с ключом от service аккаунта, и потом запускает тесты и скрипт prepare_data.py
    * планирую воспользоваться [кодированием base64 для хранения json'а в github secrets](https://medium.com/@verazabeida/using-json-in-your-github-actions-when-authenticating-with-gcp-856089db28cf)

1. Дополнить unittest для `prepare_data.py`
    * Проверить, что файлы созданы и соответствуют тому, что записалось в config
    * Проверить, что созданные датасеты парсятся pandas
2. Переписать predare_data.py
    * Добавить запись в конфиг пути до созданного датасета
3. Создать CI pipeline (Jenkins, Team City, Circle CI и др.) для сборки docker image и отправки его на DockerHub, сборка должна автоматически  стартовать по pull request в основную ветку репозитория модели;
4. Создать CD pipeline для запуска контейнера и проведения функционального тестирования по сценарию, запуск должен стартовать  по требованию или расписанию или как вызов с последнего этапа CI pipeline;