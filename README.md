# ЛР 1. Классический жизненный цикл разработки моделей машинного обучения

## Данные

В качестве датасета был использован [Connectionist Bench (Sonar, Mines vs. Rocks)](https://archive.ics.uci.edu/dataset/151/connectionist+bench+sonar+mines+vs+rocks). Датасет содержит 208 объектов, каждый из которых описывается 60 признаками. Признаки - амплитуды частот звукового сигнала, отраженного от объекта. Каждый объект принадлежит к одному из двух классов: `R` - камень, `M` - мина (металлический цилиндр).

<!-- ## Модель и ее обучение -->

## DVC

На данный момент DVC используется для версионирования файла `data/sonar.all-data`.

В качестве remote хранилища была создана папка на google drive с id `1lh_wUfw88ceVCL04UtT0e0zQCoFpqLxY`. Всем в интернете был дан доступ на чтение google drive папки, чтобы у всех работали команды `dvc get . data/sonar.all-data` и `dvc pull`. Однако, обе команды требуют аутентификации (dvc автоматически генерирует ссылку на Google OAuth2)

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
 
## Docker
Сейчас с докер контейнером производится работа "руками"

Сначала я создаю docker image с помощью:

```bash
docker build -t proshian/bd1 .
```

Потом создаю и запускаю "самоудаляющися" контейнер в интерактивном режиме, запускаю в нем shell:

```bash
docker run --rm -it  proshian/bd1 sh
```

В котнейнере я произвожу следующие команды:
```bash
dvc remote modify myremote gdrive_use_service_account true
dvc pull
python src/prepare_data.py
python src/unit_tests/test_prepare_data.py
```

Нужно отметить, что dvc pull работает только благодаря тому, что у меня локально в репозитории есть config.local, в котором указан путь др ключа от service аккаунта и сам ключ тоже хранится в репозитории (размеется, ключ и конфиг входят в .gitignore). Из репоизитория данные файлы были скопированы в докер образ (которым я не поделюсь, пока не исключу данные файлы). Если бы это было не так, использование service аккаунта было бы невозможно, и требовалась бы аутентификация в аккаунт google drive.

Нужен способ не хранить в образе ключ от service аккаунта внутри docker образа.

Я думаю, что можно как-то хранить этот json с ключом на стороне Github Actions, чтобы на этапе CD в docker контейнере происходила запись этого файла.

После записи json'а с ключом должны производиться команды
```bash
dvc remote modify myremote gdrive_use_service_account true
dvc remote modify myremote --local \
              gdrive_service_account_json_file_path path/to/file.json
```

## TODO
1. Дополнить unittest для `prepare_data.py`
    * Проверить, что файлы созданы и соответствуют тому, что записалось в config
    * Проверить, что созданные датасеты парсятся pandas
2. Переписать predare_data.py
    * Добавить запись в конфиг пути до созданного датасета
3. Создать CI pipeline (Jenkins, Team City, Circle CI и др.) для сборки docker image и отправки его на DockerHub, сборка должна автоматически  стартовать по pull request в основную ветку репозитория модели;
4. Создать CD pipeline для запуска контейнера и проведения функционального тестирования по сценарию, запуск должен стартовать  по требованию или расписанию или как вызов с последнего этапа CI pipeline;