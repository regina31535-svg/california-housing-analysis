
import pandas as pd
import numpy as np
import os

def download_california_data():
    """Создает California Housing dataset """
    print("СОЗДАНИЕ CALIFORNIA HOUSING DATASET")
    
    # Создаем синтетические данные похожие на California Housing
    np.random.seed(42)
    n_samples = 1000
    
    # Генерируем реалистичные данные
    data = {
        'longitude': np.random.uniform(-124.3, -114.3, n_samples),
        'latitude': np.random.uniform(32.5, 42.0, n_samples),
        'housing_median_age': np.random.randint(1, 52, n_samples),
        'total_rooms': np.random.randint(2, 40000, n_samples),
        'total_bedrooms': np.random.randint(1, 6500, n_samples),
        'population': np.random.randint(3, 15000, n_samples),
        'households': np.random.randint(1, 5000, n_samples),
        'median_income': np.random.uniform(0.5, 15.0, n_samples),
        'median_house_value': np.random.randint(15000, 500000, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Добавляем ocean_proximity на основе координат
    def get_ocean_proximity(lat, lon):
        if lat > 37.5 and lon < -122:
            return 'NEAR BAY'
        elif lat < 34.5:
            return 'INLAND'
        elif lon > -117:
            return 'INLAND'
        elif lon < -119:
            return 'NEAR OCEAN'
        else:
            return '<1H OCEAN'
    
    df['ocean_proximity'] = df.apply(lambda x: get_ocean_proximity(x['latitude'], x['longitude']), axis=1)
    
    print("ДОБАВЛЕНИЕ ПРОБЛЕМ В ДАННЫЕ ДЛЯ ОЧИСТКИ")
    
    # 1. Пропущенные значения (5% данных)
    missing_indices = df.sample(frac=0.05).index
    df.loc[missing_indices, 'total_bedrooms'] = np.nan
    
    missing_indices = df.sample(frac=0.03).index
    df.loc[missing_indices, 'housing_median_age'] = np.nan
    
    # 2. Выбросы
    outlier_indices = df.sample(frac=0.02).index
    df.loc[outlier_indices, 'median_income'] = df.loc[outlier_indices, 'median_income'] * 10
    
    outlier_indices = df.sample(frac=0.01).index
    df.loc[outlier_indices, 'total_rooms'] = 100000  # Нереальное значение
    
    # 3. Нестандартные форматы в категориальной переменной
    ocean_indices = df.sample(frac=0.1).index
    df.loc[ocean_indices, 'ocean_proximity'] = df.loc[ocean_indices, 'ocean_proximity'].str.lower()
    
    # 4. Проблемы с типами данных
    type_indices = df.sample(frac=0.05).index
    df.loc[type_indices, 'median_house_value'] = df.loc[type_indices, 'median_house_value'].astype(object)
    df.loc[type_indices, 'median_house_value'] = df.loc[type_indices, 'median_house_value'].apply(lambda x: f"{x} USD")
    
    # Сохраняем данные
    os.makedirs('data/raw', exist_ok=True)
    df.to_csv('data/raw/california_housing_dirty.csv', index=False)
    
    print(f"ДАННЫЕ СОХРАНЕНЫ: data/raw/california_housing_dirty.csv")
    print(f"Размер данных: {df.shape}")
    print(f"Колонки: {list(df.columns)}")
    
    # Показываем проблемы в данных
    print("\nПРОБЛЕМЫ В ДАННЫХ ДЛЯ ОЧИСТКИ:")
    print(f"Пропуски в total_bedrooms: {df['total_bedrooms'].isnull().sum()}")
    print(f"Пропуски в housing_median_age: {df['housing_median_age'].isnull().sum()}")
    print(f"Выбросы в median_income: {(df['median_income'] > 10).sum()}")
    print(f"Выбросы в total_rooms: {(df['total_rooms'] > 50000).sum()}")
    print(f"Проблемы с форматом цены: {df['median_house_value'].apply(lambda x: isinstance(x, str)).sum()}")
    
    return df

if __name__ == "__main__":
    df = download_california_data()
    print("\nПЕРВЫЕ 5 ЗАПИСЕЙ:")
    print(df.head())
