# California Housing Data Cleaning Project

## Описание проекта
Проект по очистке и анализу данных о недвижимости Калифорнии. Включает полный цикл анализа данных от загрузки до визуализации.

## Структура проекта
\`\`\`
california-housing-analysis/
├── data/
│   ├── raw/           # Исходные данные
│   └── processed/     # Очищенные данные
├── notebooks/
│   └── 02_california_housing_cleaning.ipynb
├── src/
│   └── download_california_data.py
├── requirements.txt
└── README.md
\`\`\`

## Установка
pip install -r requirements.txt

## Использование
1. Создайте данные: \`python src/download_california_data.py\`
2. Запустите анализ: \`jupyter notebook\`
3. Откройте ноутбук в папке notebooks

## Особенности проекта
- Анализ пропущенных значений
- Обнаружение и обработка выбросов
- Визуализация распределений
- Работа с категориальными переменными

