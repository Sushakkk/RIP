# Используйте конкретную версию Python для повышения стабильности
FROM python:3.9

# Установите рабочую директорию
WORKDIR /usr/src/app

# Копируйте файл с зависимостями
COPY req.txt ./

# Установите системные зависимости, если необходимо (например, для Pillow)
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
&& apt-get clean

# Обновите pip и setuptools
RUN pip install --upgrade pip setuptools

# Установите зависимости из файла
RUN pip install -r req.txt

