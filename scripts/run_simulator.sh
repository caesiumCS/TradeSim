#!/bin/bash

# Перейти в корень проекта
cd "$(dirname "$0")/.."

poetry run python src/trade_simulator/main.py