#!/bin/bash

set -e

if ! command -v poetry &> /dev/null
then
    echo "Poetry не найден. Установите poetry перед запуском этого скрипта:"
    echo "> pip install poetry"
    exit 1
fi

echo "Установка зависимостей..."
poetry install

echo "Запуск симуляции"

cd "$(dirname "$0")/.."

export PYTHONPATH=src
poetry run python src/trade_simulator/main.py