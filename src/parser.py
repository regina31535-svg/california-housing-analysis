
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from fake_useragent import UserAgent

class CianParser:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.base_url = "https://www.cian.ru/cat.php"
        
    def get_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def parse_page(self, page=1):
        """Парсит одну страницу объявлений ЦИАН"""
        
        params = {
            'deal_type': 'sale',
            'engine_version': 2,
            'offer_type': 'flat',
            'region': 1,
            'page': page,
        }
        
        try:
            print(f"Парсим страницу {page}...")
            response = self.session.get(
                self.base_url, 
                params=params, 
                headers=self.get_headers(),
                timeout=15
            )
            response.raise_for_status()
            
            return self.parse_html(response.text)
            
        except Exception as e:
            print(f"Ошибка при парсинге страницы {page}: {e}")
            return []
    
    def parse_html(self, html):
        """Парсит HTML и извлекает данные объявлений"""
        soup = BeautifulSoup(html, 'html.parser')
        offers = []
        
        # Поиск карточек объявлений
        offer_cards = soup.find_all('article', attrs={'data-name': 'CardComponent'})
        
        if not offer_cards:
            offer_cards = soup.find_all('div', class_=re.compile('--container--'))
            print(f"Используем альтернативные селекторы, найдено: {len(offer_cards)}")
        
        print(f"Найдено карточек: {len(offer_cards)}")
        
        for i, card in enumerate(offer_cards[:8]):
            try:
                print(f"Обрабатываем объявление {i+1}...")
                offer_data = self.extract_offer_data(card)
                if offer_data:
                    offers.append(offer_data)
            except Exception as e:
                print(f"Ошибка в карточке {i+1}: {e}")
                continue
                
        return offers
    
    def extract_offer_data(self, card):
        """Извлекает данные из одной карточки объявления"""
        offer = {}
        
        # Поиск цены
        price_selectors = [
            'span[data-mark="MainPrice"]',
            'div[data-testid="price-amount"]',
            '.price',
            'span[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_elem = card.select_one(selector)
            if price_elem:
                offer['price'] = self.clean_price(price_elem.get_text())
                break
        
        # Поиск заголовка
        title_selectors = [
            'span[data-mark="OfferTitle"]',
            'div[data-testid="title"]',
            'h1', 'h2', 'h3'
        ]
        
        for selector in title_selectors:
            title_elem = card.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                offer['title'] = title_text
                rooms_area = self.parse_rooms_area(title_text)
                offer.update(rooms_area)
                break
        
        # Поиск адреса
        address_selectors = [
            'div[data-name="Address"]',
            'div[class*="address"]'
        ]
        
        for selector in address_selectors:
            addr_elem = card.select_one(selector)
            if addr_elem:
                offer['address'] = addr_elem.get_text(strip=True)
                break
        
        # Поиск метро
        metro_selectors = [
            'div[data-name="Underground"]',
            'div[class*="underground"]'
        ]
        
        for selector in metro_selectors:
            metro_elem = card.select_one(selector)
            if metro_elem:
                offer['underground'] = metro_elem.get_text(strip=True)
                break
        
        # Ссылка на объявление
        link_elem = card.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            if 'cian.ru' in href:
                offer['url'] = href if href.startswith('http') else f'https://www.cian.ru{href}'
        
        if offer.get('price') and offer.get('title'):
            return offer
        else:
            return None
    
    def clean_price(self, price_text):
        """Очищает цену от лишних символов"""
        if not price_text:
            return None
        
        cleaned = re.sub(r'[^\d]', '', price_text)
        return int(cleaned) if cleaned else None
    
    def parse_rooms_area(self, title_text):
        """Парсит количество комнат и площадь из заголовка"""
        result = {}
        
        # Поиск комнат
        room_patterns = [
            r'(\d+)-комн',
            r'(\d+) комн',
            r'(\d+)к',
            r'студия',
            r'апартаменты'
        ]
        
        for pattern in room_patterns:
            match = re.search(pattern, title_text.lower())
            if match:
                if 'студия' in pattern or 'апартаменты' in pattern:
                    result['rooms'] = 0
                else:
                    result['rooms'] = int(match.group(1))
                break
        
        # Поиск площади
        area_match = re.search(r'(\d+[.,]?\d*)\s*м²', title_text.lower())
        if area_match:
            result['area'] = float(area_match.group(1).replace(',', '.'))
        
        return result
    
    def collect_data(self, pages=2):
        """Собирает данные с нескольких страниц"""
        all_offers = []
        
        for page in range(1, pages + 1):
            print(f"Страница {page}/{pages}")
            offers = self.parse_page(page=page)
            all_offers.extend(offers)
            
            print(f"Собрано с страницы: {len(offers)}")
            print(f"Всего собрано: {len(all_offers)}")
            
            if page < pages and offers:
                sleep_time = 3 + random.uniform(1, 2)
                print(f"Ожидание {sleep_time:.1f} секунд...")
                time.sleep(sleep_time)
            elif not offers:
                print("На странице нет данных, прекращаем...")
                break
        
        print(f"ИТОГО: {len(all_offers)} объявлений")
        return pd.DataFrame(all_offers)

if __name__ == "__main__":
    print("ПАРСЕР ЦИАН ДЛЯ МОСКВЫ")
    
    parser = CianParser()
    
    try:
        df = parser.collect_data(pages=2)
        
        if not df.empty:
            import os
            os.makedirs('data/raw', exist_ok=True)
            
            df.to_csv('data/raw/cian_moscow_raw.csv', index=False, encoding='utf-8')
            print("ДАННЫЕ СОХРАНЕНЫ")
            print(f"Файл: data/raw/cian_moscow_raw.csv")
            print(f"Записей: {len(df)}")
            print(f"Диапазон цен: {df['price'].min():,} - {df['price'].max():,} руб")
            
            print("Первые 3 объявления:")
            for i, row in df.head(3).iterrows():
                print(f"{i+1}. {row.get('title', 'N/A')} - {row.get('price', 'N/A'):,} руб")
                
        else:
            print("Не удалось собрать данные")
            
    except Exception as e:
        print(f"Критическая ошибка: {e}")
