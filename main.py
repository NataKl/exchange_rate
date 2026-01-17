import requests
import json
from typing import Optional, Dict, Any


def get_request(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> None:
    """
    Выполняет GET запрос к указанному URL.
    
    Args:
        url: URL для запроса
        headers: Опциональные заголовки запроса
        params: Опциональные параметры запроса (query parameters)
    """
    try:
        print(f"\n{'='*60}")
        print(f"GET запрос к: {url}")
        if params:
            print(f"Параметры: {params}")
        if headers:
            print(f"Заголовки: {headers}")
        print(f"{'='*60}\n")
        
        response = requests.get(url, headers=headers, params=params)
        
        print(f"Статус код: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        print(f"\nТело ответа:")
        
        # Пытаемся распарсить JSON, если не получается - выводим как текст
        try:
            json_data = response.json()
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")


def make_get_country_request(country: str) -> None:
    """
    Выполняет GET запрос для получения информации о стране.
    
    Args:
        country: Название страны
    """
    url = f"https://restcountries.com/v3.1/name/{country}"
    get_request(url)


def get_random_dog() -> None:
    """
    Получает случайное изображение собаки из API Dog CEO.
    """
    url = "https://dog.ceo/api/breeds/image/random"
    
    try:
        print(f"\n{'='*60}")
        print("🐕 Случайная собака")
        print(f"{'='*60}\n")
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                image_url = data.get('message', '')
                print(f"✅ Статус: {data.get('status')}")
                print(f"\n🔗 Ссылка на изображение:")
                print(f"{image_url}\n")
            else:
                print(f"❌ Ошибка: {data.get('message', 'Неизвестная ошибка')}\n")
        else:
            print(f"❌ Ошибка: Не удалось получить изображение. Код ответа: {response.status_code}\n")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при выполнении запроса: {e}\n")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}\n")


def post_request(url: str, data: Optional[Dict[str, Any]] = None, 
                 json_data: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None) -> None:
    """
    Выполняет POST запрос к указанному URL.
    
    Args:
        url: URL для запроса
        data: Данные для отправки (form-data)
        json_data: JSON данные для отправки
        headers: Опциональные заголовки запроса
    """
    try:
        print(f"\n{'='*60}")
        print(f"POST запрос к: {url}")
        if json_data:
            print(f"JSON данные: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        if data:
            print(f"Form данные: {data}")
        if headers:
            print(f"Заголовки: {headers}")
        print(f"{'='*60}\n")
        
        # Если передан json_data, используем json параметр, иначе data
        if json_data:
            response = requests.post(url, json=json_data, headers=headers)
        else:
            response = requests.post(url, data=data, headers=headers)
        
        print(f"Статус код: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        print(f"\nТело ответа:")
        
        # Пытаемся распарсить JSON, если не получается - выводим как текст
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")


def main():
    """
    Главная функция для выбора типа запроса.
    """
    print("\n" + "="*60)
    print("ТЕСТОВЫЙ КЛИЕНТ ДЛЯ API")
    print("="*60)
    print("\nВыберите тип запроса:")
    print("1. GET запрос")
    print("2. POST запрос")
    print("3. GET запрос для получения информации о стране")
    print("4. Случайная собака")
    print("0. Выход")
    
    choice = input("\nВаш выбор: ").strip()
    
    if choice == "0":
        print("Выход из программы.")
        return
    
    if choice == "4":
        # Случайная собака - не требует URL
        get_random_dog()
        return
    
    url = input("Введите URL: ").strip()
    
    if not url:
        print("URL не может быть пустым!")
        return
    
    if choice == "1":
        # GET запрос
        headers_input = input("Заголовки (JSON формат, или Enter для пропуска): ").strip()
        params_input = input("Параметры запроса (JSON формат, или Enter для пропуска): ").strip()
        
        headers = None
        params = None
        
        if headers_input:
            try:
                headers = json.loads(headers_input)
            except json.JSONDecodeError:
                print("Ошибка парсинга заголовков. Используется формат по умолчанию.")
        
        if params_input:
            try:
                params = json.loads(params_input)
            except json.JSONDecodeError:
                print("Ошибка парсинга параметров. Используется формат по умолчанию.")
        
        get_request(url, headers=headers, params=params)
        
    elif choice == "2":
        # POST запрос
        data_type = input("Тип данных (1 - JSON, 2 - Form-data): ").strip()
        
        headers_input = input("Заголовки (JSON формат, или Enter для пропуска): ").strip()
        headers = None
        
        if headers_input:
            try:
                headers = json.loads(headers_input)
            except json.JSONDecodeError:
                print("Ошибка парсинга заголовков. Используется формат по умолчанию.")
        
        if data_type == "1":
            # JSON данные
            json_input = input("JSON данные: ").strip()
            json_data = None
            
            if json_input:
                try:
                    json_data = json.loads(json_input)
                except json.JSONDecodeError:
                    print("Ошибка парсинга JSON данных!")
                    return
            
            post_request(url, json_data=json_data, headers=headers)
            
        elif data_type == "2":
            # Form-data
            data_input = input("Form данные (JSON формат ключ-значение): ").strip()
            data = None
            
            if data_input:
                try:
                    data = json.loads(data_input)
                except json.JSONDecodeError:
                    print("Ошибка парсинга form данных!")
                    return
            
            post_request(url, data=data, headers=headers)
        else:
            print("Неверный выбор типа данных!")
    elif choice == "3":
        # GET запрос для получения информации о стране
        country = input("Введите название страны: ").strip()
        make_get_country_request(country)
    else:
        print("Неверный выбор!")


if __name__ == "__main__":
    main()
