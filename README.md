![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white) ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)


# Проект Yatube 

[Yatube](https://aleksentcev.pythonanywhere.com/) - это социальная сеть для ведения микроблогов. Пользователи могут создавать и редактировать публикации, оставлять комментарии, подписываться на других пользователей, объединять публикации в группы. Реализован бекенд, фронтенд, настроена пагинация и кеширование. Проект покрыт тестами.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Aleksentcev/yatube-project.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```
```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Импортировать данные из csv файлов:

```
python3 manage.py import_csv
```

Запустить проект:

```
python3 manage.py runserver
```

Проект будет или не будет доступен по адресу: http://localhost/


### Панель администратора:

Создать суперпользователя:

```
python3 manage.py createsuperuser
```

Придумать и ввести имя пользователя:

```
Имя пользователя: <username>
```

Ввести адрес электронной почты:

```
Адрес эл.почты: <email>
```

Придумать и ввести пароль (поле ввода не будет отображать никакие символы):

```
Password: <password>
```

Повторно ввести пароль (поле ввода не будет отображать никакие символы):

```
Password (again): <password>
```

URL панели-администратора:

```
.../admin/
```

В панели администратора есть возможность просматривать и редактировать данные из базы данных.

Если ничего не заработало - идите пить чай :)

### Автор:

Михаил Алексенцев

[![Telegram](https://img.shields.io/badge/aleksentcev-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white&link=https://t.me/aleksentcev)](https://t.me/aleksentcev)
