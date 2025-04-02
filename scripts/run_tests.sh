#!/bin/bash

# Перейти в корень проекта
cd "$(dirname "$0")/.."

export PYTHONPATH=src
poetry run pytest --cov=trade_simulator --cov-report=term-missing --cov-report=xml
