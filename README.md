# hw05_final
____
###### Блог Yatube, в котором реализованы следующие возможности:
+ _создание постов, с выбором подходящей группы и их последующее редактирование (CRUD) автором поста_
+ _добавление и редактирование комментариев к постам_
+ _возможность подписки/отписки на(от) автора_

### Как запустить проект:
____

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/FataLklg/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
### Авторы:
___
- ##### __Антон Тарасов__


[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
