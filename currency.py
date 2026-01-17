import requests
import json
import os
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Инициализация colorama для Windows
init(autoreset=True)

FAVORITE_CURRENCIES = ["USD", "EUR", "GBP", "RUB"]
FILE_NAME = "currency_rate.json"

def get_currency_rate(currency_code: str) -> float:
    URL = f"https://open.er-api.com/v6/latest/{currency_code}"

    response = requests.get(URL)
    if response.status_code != 200: 
        print(f"Ошибка: {response.status_code}")
        return None
    
    data = response.json()
    return data
    
def save_to_file(data: dict):
    """
    Сохраняет данные о курсах валют в файл.
    
    Args:
        data: Словарь с данными о курсах валют
    """
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

def update_currency_rates():
    all_data = {}
    for currency in FAVORITE_CURRENCIES:
        rate = get_currency_rate(currency)
        all_data[currency] = rate
    save_to_file(all_data)
    print(f"Данные обновлены в currency_rate.json")

def read_from_file():
    """
    Читает данные о курсах валют из файла.
    
    Returns:
        dict: Данные о курсах валют или None в случае ошибки
    """
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {FILE_NAME} не найден.")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка: Неверный формат JSON в файле {FILE_NAME}.")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


def is_file_older_than_24_hours(file_path: str) -> bool:
    """
    Проверяет, старше ли файл 24 часов.
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        bool: True если файл старше 24 часов или не существует, False если моложе
    """
    if not os.path.exists(file_path):
        return True  # Файл не существует, нужно обновить
    
    try:
        # Получаем время последней модификации файла
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        # Текущее время
        current_time = datetime.now()
        # Разница во времени
        time_diff = current_time - file_time
        
        # Проверяем, прошло ли 24 часа
        return time_diff > timedelta(hours=24)
    except Exception as e:
        print(f"Ошибка при проверке возраста файла: {e}")
        return True  # В случае ошибки обновляем файл


def load_or_update_currency_rates():
    """
    Загружает данные из файла, если он существует и моложе 24 часов,
    иначе обновляет данные из API.
    
    Returns:
        dict: Данные о курсах валют
    """
    # Проверяем, нужно ли обновлять файл
    if is_file_older_than_24_hours(FILE_NAME):
        print(f"Файл {FILE_NAME} не найден или старше 24 часов. Обновление данных...")
        update_currency_rates()
    else:
        print(f"Используются данные из файла {FILE_NAME} (файл моложе 24 часов).")
    
    # Читаем данные из файла (обновленного или существующего)
    data = read_from_file()
    return data

def get_available_base_currencies(data: dict) -> list:
    """
    Получает список доступных базовых валют из данных.
    
    Args:
        data: Словарь с данными о курсах валют
        
    Returns:
        list: Список кодов базовых валют
    """
    return list(data.keys())


def find_base_currency_for_currency(data: dict, currency: str) -> str:
    """
    Находит базовую валюту, в rates которой есть указанная валюта.
    
    Args:
        data: Словарь с данными о курсах валют
        currency: Код валюты
        
    Returns:
        str: Код базовой валюты или None
    """
    # Сначала проверяем, является ли валюта базовой
    if currency in data:
        return currency
    
    # Ищем валюту в rates других базовых валют
    for base_currency, currency_data in data.items():
        if isinstance(currency_data, dict) and "rates" in currency_data:
            if currency in currency_data["rates"]:
                return base_currency
    
    return None


def get_rates_for_base_currency(data: dict, base_currency: str) -> dict:
    """
    Получает курсы всех валют относительно указанной базовой валюты.
    
    Args:
        data: Словарь с данными о курсах валют
        base_currency: Код базовой валюты
        
    Returns:
        dict: Словарь с курсами валют или None
    """
    # Если валюта является базовой в файле
    if base_currency in data:
        currency_data = data[base_currency]
        if isinstance(currency_data, dict) and "rates" in currency_data:
            return currency_data["rates"]
    
    # Если валюта не является базовой, ищем её в rates других базовых валют
    source_base = find_base_currency_for_currency(data, base_currency)
    if not source_base:
        return None
    
    source_data = data[source_base]
    if not isinstance(source_data, dict) or "rates" not in source_data:
        return None
    
    source_rates = source_data["rates"]
    
    # Если запрашиваемая валюта не найдена в rates
    if base_currency not in source_rates:
        return None
    
    # Получаем курс запрашиваемой валюты относительно исходной базовой
    base_rate = source_rates[base_currency]
    if base_rate == 0:
        return None
    
    # Вычисляем курсы всех валют относительно новой базовой
    new_rates = {}
    for currency, rate in source_rates.items():
        if currency == base_currency:
            new_rates[currency] = 1.0
        else:
            new_rates[currency] = rate / base_rate
    
    return new_rates


def display_currency_rates(base_currency: str, rates: dict):
    """
    Отображает курсы валют относительно базовой валюты в красивом формате.
    
    Args:
        base_currency: Код базовой валюты
        rates: Словарь с курсами валют
    """
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{f'КУРСЫ ВАЛЮТ ОТНОСИТЕЛЬНО {base_currency}':^80}")
    print(f"{Fore.CYAN}{'='*80}{Fore.RESET}\n")
    
    # Сортируем валюты по коду
    sorted_currencies = sorted(rates.items(), key=lambda x: x[0])
    
    # Выводим курсы в колонках
    currencies_per_line = 4
    for i in range(0, len(sorted_currencies), currencies_per_line):
        line_currencies = sorted_currencies[i:i + currencies_per_line]
        line_parts = []
        for currency, rate in line_currencies:
            # Форматируем курс в зависимости от величины
            if rate >= 1:
                rate_str = f"{rate:,.4f}".rstrip('0').rstrip('.')
            else:
                rate_str = f"{rate:.6f}".rstrip('0').rstrip('.')
            
            line_parts.append(f"{Fore.GREEN}{currency}{Fore.RESET}: {Fore.YELLOW}{rate_str}{Fore.RESET}")
        
        print(f"  {'  |  '.join(line_parts)}")
    
    print(f"\n{Fore.CYAN}{'='*80}{Fore.RESET}\n")
    print(f"{Fore.WHITE}Всего валют: {Fore.GREEN}{len(rates)}{Fore.RESET}\n")


def show_currency_rates_interface(data: dict):
    """
    Интерфейс для ввода базовой валюты и отображения курсов.
    
    Args:
        data: Словарь с данными о курсах валют
    """
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'ОТОБРАЖЕНИЕ КУРСОВ ВАЛЮТ':^80}")
    print(f"{Fore.CYAN}{'='*80}{Fore.RESET}\n")
    
    # Получаем список доступных базовых валют
    available_bases = get_available_base_currencies(data)
    
    # Получаем все доступные валюты из rates
    all_currencies = set()
    for base, base_data in data.items():
        if isinstance(base_data, dict) and "rates" in base_data:
            all_currencies.update(base_data["rates"].keys())
    
    all_currencies = sorted(list(all_currencies))
    
    print(f"{Fore.WHITE}Доступные базовые валюты в файле: {Fore.GREEN}{', '.join(available_bases)}{Fore.RESET}")
    print(f"{Fore.WHITE}Всего доступных валют: {Fore.GREEN}{len(all_currencies)}{Fore.RESET}\n")
    
    while True:
        base_currency = input(f"{Fore.YELLOW}Введите код базовой валюты (или 'exit' для выхода): {Fore.RESET}").strip().upper()
        
        if base_currency.lower() in ['exit', 'выход', 'quit', 'q']:
            print(f"\n{Fore.YELLOW}Выход из режима просмотра курсов.{Fore.RESET}\n")
            break
        
        if not base_currency:
            print(f"{Fore.RED}Ошибка: Введите код валюты!\n")
            continue
        
        # Получаем курсы для выбранной базовой валюты
        rates = get_rates_for_base_currency(data, base_currency)
        
        if rates is None:
            print(f"{Fore.RED}Ошибка: Валюта '{base_currency}' не найдена в данных!\n")
            continue
        
        # Отображаем курсы
        display_currency_rates(base_currency, rates)


if __name__ == "__main__":
    # Загружаем или обновляем данные в зависимости от возраста файла
    data = load_or_update_currency_rates()
    
    if data:
        print(f"\n{Fore.GREEN}✓ Данные успешно загружены!{Fore.RESET}")
        print(f"{Fore.WHITE}Доступно базовых валют: {Fore.GREEN}{len(data)}{Fore.RESET}")
        print(f"{Fore.WHITE}Базовые валюты: {Fore.GREEN}{', '.join(data.keys())}{Fore.RESET}\n")
        
        # Запускаем интерфейс для просмотра курсов
        show_currency_rates_interface(data)
    else:
        print(f"{Fore.RED}Не удалось загрузить данные о курсах валют.{Fore.RESET}")