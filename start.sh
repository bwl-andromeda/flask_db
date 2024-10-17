#!/usr/bin/env bash

set -e

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Python не установлен... Пожалуйста, установите Python и запустите скрипт снова..."
    exit 1
fi

if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "Python не установлен... Пожалуйста установите Python и запустите скрипт снова..."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Создание виртуального окружения..."
    $PYTHON -m venv .venv
fi

source .venv/bin/activate

if ! command -v pip &> /dev/null; then
    echo "Pip не найден... Установка pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $PYTHON get-pip.py
    rm get-pip.py
fi

if [ -f "requirements.txt" ]; then
    echo "Проверка и установка необходимых зависимостей..."
    pip freeze > current_requirements.txt
    pip install -r <(comm -23 <(sort requirements.txt) <(sort current_requirements.txt))
    rm current_requirements.txt
else
    echo "requirements.txt не найден... Пропуск установки зависимостей..."
fi

if ! command -v docker &> /dev/null; then
    echo "Docker не установлен... Пожалуйста установите Docker и запустите скрипт снова..."
    exit 1
fi

if ! docker ps -a --format '{{.Names}}' | grep -Eq "^financial-tracker-db\$"; then
    echo "Docker контейнер 'financial-tracker-db' не найден. Создание и старт контейнера..."
    docker run --name financial-tracker-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=financial_tracker -p 5432:5432 -d postgres
else
    if ! docker ps --format '{{.Names}}' | grep -Eq "^financial-tracker-db\$"; then
        echo "Старт существующего контейнера 'financial-tracker-db'..."
        docker start financial-tracker-db
    else
        echo "Контейнер 'financial-tracker-db' уже запущен."
    fi
fi

echo "Запуск flask приложения..."
flask run

