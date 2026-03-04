# Лабораторная работа №2. Работа с Docker

**Выполнил:** Килбас Эдуард Сергеевич  
**Вариант:** 11 (.NET + MS SQL Server)  
**Тема:** Работа с Docker  
**Цель:** Познакомиться с возможностями и получить практические навыки работы с Docker

---

## Этап 1. Установка Docker и базовые команды

### Проверка версии Docker и запуск hello-world

Проверка установленной версии Docker и запуск первого контейнера `hello-world`, который подтверждает корректность установки.

```bash
docker --version
docker run hello-world
```

![docker --version и hello-world](img/img01.png)

---

### Запуск контейнера docker/getting-started

Запуск обучающего контейнера `docker/getting-started` в фоновом режиме с проброской порта 8080.

```bash
docker run -d -p 8080:80 docker/getting-started
```

![docker run getting-started](img/img02.png)

---

### Команды docker ps, images, stop, start

Демонстрация основных команд жизненного цикла контейнера: просмотр запущенных контейнеров, список образов, остановка и повторный запуск.

```bash
docker ps
docker images
docker stop 987f2b2371dd
docker ps -a
docker start 987f2b2371dd
docker ps
```

![docker ps images stop start](img/img03.png)

---

### Команда docker logs (часть 1)

Просмотр логов контейнера `docker/getting-started` — видны логи nginx и процессов внутри контейнера.

```bash
docker logs 987f2b2371dd
```

![docker logs часть 1](img/img04.png)

---

### Команда docker logs (часть 2)

Продолжение вывода логов — перезапуск nginx после команды `docker start`.

![docker logs часть 2](img/img05.png)

---

### Команда docker inspect

Получение IP-адреса контейнера с помощью `docker inspect`.

```bash
docker inspect 987f2b2371dd | grep -i ipaddress
```

![docker inspect](img/img06.png)

---

### Tutorial в браузере

Открытие обучающего tutorial из контейнера `docker/getting-started` по адресу `http://localhost:8080/tutorial`.

![Getting Started tutorial в браузере](img/img07.png)

---

## Этап 2. Скрипт с использованием geometric_lib

### Клонирование репозитория geometric_lib

Создание рабочей директории и клонирование репозитория с геометрической библиотекой.

```bash
mkdir docker_geometric
cd docker_geometric
git clone https://github.com/smartiqaorg/geometric_lib
ls
cd geometric_lib && ls
```

![git clone geometric_lib](img/img08.png)

---

### Скрипт app.py

Python-скрипт `app.py`, использующий функции из `geometric_lib`. Данные передаются через переменные окружения `FIGURE` и `PARAM1`.

```bash
cat app.py
```

![cat app.py](img/img09.png)

---

### Структура директории

Проверка структуры проекта: файлы `app.py` и папка `geometric_lib`.

```bash
ls
```

![ls структура](img/img10.png)

---

### Dockerfile для geometric-app

Содержимое Dockerfile для сборки образа с Python-скриптом. Используется образ `python:3.9-slim`, копируется библиотека и скрипт.

```bash
cat Dockerfile
```

![cat Dockerfile geometric](img/img11.png)

---

### Сборка образа docker build (часть 1)

Запуск сборки Docker-образа `geometric-app`. Загрузка базового образа `python:3.9-slim`.

```bash
docker build -t geometric-app .
```

![docker build часть 1](img/img12.png)

---

### Сборка образа docker build (часть 2)

Успешное завершение сборки — все 6 шагов выполнены, образ `geometric-app:latest` создан.

![docker build часть 2 успех](img/img13.png)

---

### Запуск контейнера с передачей параметров через env

Тестирование контейнера с передачей данных через переменные окружения. Вычисляются площадь и периметр круга и квадрата.

```bash
docker run --rm -e FIGURE=circle -e PARAM1=5 geometric-app
docker run --rm -e FIGURE=square -e PARAM1=4 geometric-app
```

![docker run с переменными окружения](img/img14.png)

---

## Этап 3. Основной проект .NET + MS SQL Server

### Клонирование проекта с GitHub

Клонирование проекта `WebApiEntityFrameworkDockerSqlServer` — ASP.NET Core Web API с Entity Framework и SQL Server.

```bash
mkdir docker_dotnet_project
cd docker_dotnet_project
git clone https://github.com/bryanjhogan/WebApiEntityFrameworkDockerSqlServer.git
```

![git clone dotnet проект](img/img15.png)

---

### Структура .NET проекта

Просмотр файла `.csproj` — видны зависимости: `EntityFrameworkCore.SqlServer` и `AutoFixture`.

```bash
cd WebApiEntityFrameworkDockerSqlServer
cat WebApiEntityFrameworkDockerSqlServer.csproj
```

![cat .csproj](img/img16.png)

---

### Dockerfile для .NET приложения

Многоэтапный Dockerfile: сначала сборка с `dotnet/sdk:6.0`, затем финальный образ на основе `dotnet/aspnet:6.0`.

```bash
cat Dockerfile
ls
```

![cat Dockerfile dotnet](img/img17.png)

---

### docker-compose.yml

Файл `docker-compose.yml` с двумя сервисами (`db` — MS SQL Server, `web` — .NET API), общей сетью `app_network` и томом `mssql_data`.

```bash
cat docker-compose.yml
```

![cat docker-compose.yml](img/img18.png)

---

### Запуск docker compose up (сборка)

Запуск `docker compose up -d` — скачивание образа MS SQL Server и многоэтапная сборка .NET приложения.

```bash
docker compose up -d
```

![docker compose up сборка](img/img19.png)

---

### Завершение сборки и запуск контейнеров

Успешное завершение сборки всех слоёв. Сеть, том и оба контейнера созданы и запущены.

![docker compose up завершение](img/img20.png)

---

### Повторный запуск (из кэша)

Повторный `docker compose up -d` — контейнеры уже собраны, запуск происходит быстро из кэша.

![docker compose up повторный](img/img21.png)

---

### docker compose ps

Проверка статуса запущенных контейнеров: `sql_server_db` (порт 1433) и `web_api_app` (порт 8080).

```bash
docker compose ps
```

![docker compose ps](img/img22.png)

---

### docker compose logs

Просмотр логов веб-приложения. Видно, что Entity Framework выполнил миграции и приложение прослушивает порт 80.

```bash
docker compose logs web --tail=30
```

![docker compose logs](img/img23.png)

---

### API работает в браузере

Проверка работы API в браузере по адресу `http://localhost:8080/products` — возвращается JSON с данными из MS SQL Server.

![API в браузере](img/img24.png)

---

### docker images и docker ps

Список всех Docker-образов и запущенных контейнеров после разворачивания проекта.

```bash
docker images
docker ps
```

![docker images и docker ps](img/img25.png)

---

## Этап 4. Команды жизненного цикла контейнера

### docker stop, start, restart

Демонстрация команд остановки, запуска и перезапуска контейнера с проверкой статуса через `docker ps`.

```bash
docker stop web_api_app
docker ps
docker start web_api_app
docker ps
docker restart web_api_app
docker ps
```

![stop start restart](img/img26.png)

---

### docker pause, unpause

Приостановка контейнера (статус `Paused`) и возобновление работы.

```bash
docker pause web_api_app
docker ps
docker unpause web_api_app
docker ps
```

![pause unpause](img/img27.png)

---

### docker logs и docker inspect

Просмотр последних логов контейнера и получение его IP-адреса через `docker inspect`.

```bash
docker logs web_api_app --tail 20
docker inspect web_api_app | grep -i ipaddress
```

![logs и inspect](img/img28.png)

---

### docker tag

Создание тега для образа перед публикацией на DockerHub.

```bash
docker tag webapientityframeworkdockersqlserver-web uterst/myapp:latest
docker images
```

![docker tag](img/img29.png)

---

## Этап 5. Сетевое взаимодействие (docker network)

### docker network ls и inspect bridge

Просмотр всех сетей на хосте и детальная информация о стандартной сети `bridge`.

```bash
docker network ls
docker network inspect bridge
```

![network ls и inspect bridge](img/img30.png)

---

### Продолжение inspect bridge

Полная информация о сети `bridge`: подсеть `172.17.0.0/16`, шлюз `172.17.0.1`, настройки драйвера.

![inspect bridge продолжение](img/img31.png)

---

### docker network inspect host

Информация о сети `host` — используется сетевой стек хостовой машины напрямую.

```bash
docker network inspect host
```

![inspect host](img/img32.png)

---

### docker network inspect none

Информация о сети `none` — контейнеры в этой сети полностью изолированы от сети.

```bash
docker network inspect none
```

![inspect none](img/img33.png)

---

### Inspect сети проекта (app_network) — часть 1

Детальная информация о сети `app_network`, созданной docker-compose. Видны подключённые контейнеры и их IP-адреса.

```bash
docker network inspect webapientityframeworkdockersqlserver_app_network
```

![inspect app_network часть 1](img/img34.png)

---

### Inspect сети проекта (app_network) — часть 2

Продолжение вывода: MAC-адреса и IPv4-адреса контейнеров `web_api_app` (172.18.0.2) и `sql_server_db` (172.18.0.3).

![inspect app_network часть 2](img/img35.png)

---

### Создание bridge-сети my_bridge и запуск контейнера

Создание собственной bridge-сети `my_bridge`, запуск контейнера `alpine1` в этой сети.

```bash
docker network create my_bridge
docker network ls
docker run -dit --name alpine1 --network my_bridge alpine sh
```

![network create my_bridge](img/img36.png)

---

### Inspect my_bridge с контейнером

Информация о сети `my_bridge` — видно подключение контейнера `alpine1` с IP `172.19.0.2`.

```bash
docker network inspect my_bridge
```

![inspect my_bridge с alpine1](img/img37.png)

---

### Отключение контейнера от сети

Отключение `alpine1` от сети `my_bridge` и проверка — раздел `Containers` теперь пустой.

```bash
docker network disconnect my_bridge alpine1
docker network inspect my_bridge
```

![network disconnect](img/img38.png)

---

### Создание второй bridge-сети и запуск трёх контейнеров

Создание `my_bridge2` и запуск трёх контейнеров (`alpine2`, `alpine3`, `alpine4`) в этой сети.

```bash
docker network create my_bridge2
docker run -dit --name alpine2 --network my_bridge2 alpine sh
docker run -dit --name alpine3 --network my_bridge2 alpine sh
docker run -dit --name alpine4 --network my_bridge2 alpine sh
```

![network create my_bridge2 и три контейнера](img/img39.png)

---

### Inspect my_bridge2 — IP-адреса контейнеров (часть 1)

Информация о сети `my_bridge2`: подсеть `172.20.0.0/16`, первый контейнер `alpine4` с IP `172.20.0.4`.

```bash
docker network inspect my_bridge2
```

![inspect my_bridge2 часть 1](img/img40.png)

---

### Inspect my_bridge2 — IP-адреса контейнеров (часть 2)

Продолжение вывода: все три контейнера в сети — `alpine4` (172.20.0.4), `alpine2` (172.20.0.2), `alpine3` (172.20.0.3).

![inspect my_bridge2 часть 2](img/img41.png)

---

### Пинг между контейнерами

Подключение к `alpine2` и пинг `alpine3` (172.20.0.3) и `alpine4` (172.20.0.4) — связь между контейнерами работает.

```bash
docker exec -it alpine2 sh
/ # ping -c 3 172.20.0.3
/ # ping -c 3 172.20.0.4
```

![ping между контейнерами](img/img42.png)

---

### Инициализация Swarm и создание overlay-сети my_overlay

Инициализация Docker Swarm, создание overlay-сети `my_overlay` и проверка списка сетей.

```bash
docker swarm init
docker network create --driver overlay my_overlay
docker network ls
```

![swarm init и overlay my_overlay](img/img43.png)

---

### Inspect overlay my_overlay

Информация о сети `my_overlay`: driver `overlay`, scope `swarm`, подсеть `10.0.1.0/24`.

```bash
docker network inspect my_overlay
```

![inspect my_overlay](img/img44.png)

---

### Создание второй overlay-сети my_overlay2

Создание `my_overlay2` и проверка списка сетей — обе overlay-сети появились.

```bash
docker network create --driver overlay my_overlay2
docker network ls
```

![network create my_overlay2](img/img45.png)

---

### Inspect overlay my_overlay2

Информация о сети `my_overlay2`: подсеть `10.0.2.0/24`.

```bash
docker network inspect my_overlay2
```

![inspect my_overlay2](img/img46.png)

---

### Удаление overlay-сети

Удаление `my_overlay2` и проверка — сеть исчезла из списка.

```bash
docker network rm my_overlay2
docker network ls
```

![network rm my_overlay2](img/img47.png)

---

### Попытка создать сеть host

Попытка создать дополнительную host-сеть — Docker возвращает ошибку, так как host-сеть может быть только одна.

```bash
docker network create --driver host my_host
```

> **Результат:** `Error response from daemon: only one instance of "host" network is allowed`

![попытка создать host сеть](img/img48.png)

---

## Этап 6. Тома (docker volume)

### docker volume ls и inspect

Просмотр созданных томов и детальная информация о томе `mssql_data`, который хранит данные MS SQL Server.

```bash
docker volume ls
docker volume inspect webapientityframeworkdockersqlserver_mssql_data
```

![volume ls и inspect](img/img49.png)

---

### Проверка персистентности данных

Остановка и повторный запуск контейнеров — данные в базе сохранились благодаря тому.

```bash
docker compose down
docker compose up -d
```

![docker compose down и up](img/img50.png)

---

### API после перезапуска

Проверка в браузере — данные в `http://localhost:8080/products` сохранились после перезапуска контейнеров.

![API после перезапуска](img/img51.png)

---

## Этап 7. Публикация на DockerHub

### docker login

Авторизация в DockerHub через браузер. Статус: `Login Succeeded`.

```bash
docker login
```

![docker login](img/img52.png)

---

### docker push на DockerHub

Публикация образа `uterst/myapp:latest` на DockerHub.

```bash
docker images
docker push uterst/myapp:latest
```

![docker push](img/img53.png)

---

### Образ на DockerHub

Подтверждение публикации — образ `uterst/myapp` появился в репозиториях на `hub.docker.com`.

![DockerHub профиль с образом](img/img54.png)

---

## Итог

В ходе лабораторной работы были выполнены:

- Установка Docker и запуск базовых контейнеров
- Создание Docker-образа для Python-скрипта с использованием `geometric_lib`
- Написание Dockerfile и docker-compose.yml для проекта .NET + MS SQL Server
- Демонстрация всех команд жизненного цикла контейнера
- Изучение сетей Docker: `bridge`, `host`, `none`, `overlay`
- Настройка томов для сохранения данных
- Публикация образа на DockerHub
