# Virtual-Library
Books (Library)

Функциональный сайт для хранения книг с возможностью добавления, просмотра и оценки.

**Фокус:**
* Работа с шаблонами (Jinja2)
* Использование Bootstrap для верстки
* Минимизация дублирования кода


**Критерий выполнения**
* Добавлено текстовое поле "Отзыв" для книг с сохранением в БД и выводом в списке
* Реализована загрузка и отображение обложек книг (сохранение в /static/uploads/)
* Добавлена система оценки книг (1-5 звёзд) с возможностью выбора при добавлении и визуализацией ★
* Реализован функциональный поиск по названию/автору с фильтрацией через SQL LIKE
* Добавлена система жанров (выпадающий список при добавлении + фильтрация по жанру)
* Создана страница статистики с количеством книг, средним рейтингом и популярными жанрами
* Реализована система пользователей (регистрация+вход) с функцией "Избранное"
* Разработано API для книг с возвратом JSON и фильтрацией через параметры URL

Очевидно, что данный проект потребовал щалезть в интернет, взять оттуда разные структуры, осознать из и вставить из в код. Ниже я написала список источников, которые я испольщовала (Даже включая реддит и другие сообщества)
* https://flask.palletsprojects.com/en/stable/
* https://flask-sqlalchemy.palletsprojects.com/en/stable/
* https://flask-login.readthedocs.io/en/latest/
* https://werkzeug.palletsprojects.com/en/stable/
* https://jinja.palletsprojects.com/en/stable/
* https://realpython.com/using-flask-login-for-user-management-with-flask/
* https://www.geeksforgeeks.org/connect-flask-to-a-database-with-flask-sqlalchemy/ _(ОЧЕНЬ ПОЛЕЗНО!!!)_
* https://pythonbasics.org/flask-login/ _(Очень помогло разобраться с логином, этот ресурс мне посоветовал папа)_
* https://pythonbasics.org/flask-upload-file/
* https://www.reddit.com/r/flask/
* https://github.com/pallets
* https://stackoverflow.com/questions/tagged/flask _(Мне даже пришлось здесь зарегистрироваться)_
