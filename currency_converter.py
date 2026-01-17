import json
from colorama import init, Fore, Style
from typing import Dict, Optional

# Инициализация colorama для Windows
init(autoreset=True)


def load_currency_data() -> Optional[Dict]:
    """
    Загружает данные о курсах валют из файла.
    
    Returns:
        dict: Данные о курсах валют или None в случае ошибки
    """
    try:
        with open("currency_rate.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"{Fore.RED}Ошибка: Файл currency_rate.json не найден!")
        print(f"{Fore.YELLOW}Сначала запустите currency.py для обновления данных.")
        return None
    except json.JSONDecodeError:
        print(f"{Fore.RED}Ошибка: Неверный формат JSON файла!")
        return None
    except Exception as e:
        print(f"{Fore.RED}Ошибка при загрузке данных: {e}")
        return None


def get_available_currencies(data: Dict) -> list:
    """
    Получает список всех доступных валют из данных.
    
    Args:
        data: Словарь с данными о курсах валют
        
    Returns:
        list: Список кодов валют
    """
    currencies = set()
    
    # Проходим по всем базовым валютам и собираем все доступные валюты
    for base_currency, currency_data in data.items():
        if isinstance(currency_data, dict) and "rates" in currency_data:
            currencies.update(currency_data["rates"].keys())
    
    return sorted(list(currencies))


def find_base_currency(data: Dict, currency: str) -> Optional[str]:
    """
    Находит базовую валюту, относительно которой есть курс для указанной валюты.
    
    Args:
        data: Словарь с данными о курсах валют
        currency: Код валюты
        
    Returns:
        str: Код базовой валюты или None
    """
    # Сначала проверяем, есть ли эта валюта как базовая
    if currency in data:
        return currency
    
    # Ищем валюту в rates других базовых валют
    for base_currency, currency_data in data.items():
        if isinstance(currency_data, dict) and "rates" in currency_data:
            if currency in currency_data["rates"]:
                return base_currency
    
    return None


def get_exchange_rate(data: Dict, from_currency: str, to_currency: str) -> Optional[float]:
    """
    Получает курс обмена между двумя валютами.
    
    Args:
        data: Словарь с данными о курсах валют
        from_currency: Исходная валюта
        to_currency: Целевая валюта
        
    Returns:
        float: Курс обмена или None в случае ошибки
    """
    # Если валюты одинаковые
    if from_currency == to_currency:
        return 1.0
    
    # Находим базовую валюту для исходной валюты
    base_currency = find_base_currency(data, from_currency)
    if not base_currency:
        return None
    
    base_data = data[base_currency]
    if not isinstance(base_data, dict) or "rates" not in base_data:
        return None
    
    rates = base_data["rates"]
    
    # Если обе валюты есть в rates относительно одной базовой
    if from_currency in rates and to_currency in rates:
        # Курс = (курс целевой валюты) / (курс исходной валюты)
        from_rate = rates[from_currency]
        to_rate = rates[to_currency]
        
        if from_rate == 0:
            return None
        
        return to_rate / from_rate
    
    return None


def convert_currency(data: Dict, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
    """
    Конвертирует сумму из одной валюты в другую.
    
    Args:
        data: Словарь с данными о курсах валют
        amount: Сумма для конвертации
        from_currency: Исходная валюта
        to_currency: Целевая валюта
        
    Returns:
        float: Конвертированная сумма или None в случае ошибки
    """
    rate = get_exchange_rate(data, from_currency, to_currency)
    if rate is None:
        return None
    
    return amount * rate


def display_currencies(currencies: list, per_line: int = 5):
    """
    Выводит список валют в красивом формате.
    
    Args:
        currencies: Список кодов валют
        per_line: Количество валют в строке
    """
    for i in range(0, len(currencies), per_line):
        line_currencies = currencies[i:i + per_line]
        formatted = "  ".join([f"{Fore.GREEN}{curr}{Fore.RESET}" for curr in line_currencies])
        print(f"  {formatted}")


def print_header(text: str):
    """Выводит заголовок в красивом формате."""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{text:^80}")
    print(f"{Fore.CYAN}{'='*80}{Fore.RESET}\n")


def main():
    """
    Главная функция с интерфейсом конвертера валют.
    """
    print_header("КОНВЕРТЕР ВАЛЮТ")
    
    # Загружаем данные
    print(f"{Fore.YELLOW}Загрузка данных о курсах валют...")
    data = load_currency_data()
    
    if not data:
        return
    
    # Получаем список доступных валют
    available_currencies = get_available_currencies(data)
    
    if not available_currencies:
        print(f"{Fore.RED}Ошибка: Не найдено доступных валют!")
        return
    
    print(f"{Fore.GREEN}✓ Данные успешно загружены!")
    print(f"{Fore.WHITE}Доступно валют: {Fore.GREEN}{len(available_currencies)}{Fore.RESET}\n")
    
    while True:
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'МЕНЮ':^80}")
        print(f"{Fore.CYAN}{'='*80}{Fore.RESET}\n")
        
        print(f"{Fore.WHITE}1. {Fore.GREEN}Конвертировать валюту")
        print(f"{Fore.WHITE}2. {Fore.GREEN}Показать курс обмена")
        print(f"{Fore.WHITE}3. {Fore.GREEN}Список доступных валют")
        print(f"{Fore.WHITE}0. {Fore.RED}Выход\n")
        
        choice = input(f"{Fore.YELLOW}Выберите действие: {Fore.RESET}").strip()
        
        if choice == "0":
            print(f"\n{Fore.YELLOW}До свидания!{Fore.RESET}\n")
            break
        
        elif choice == "1":
            # Конвертация валюты
            print(f"\n{Fore.CYAN}{'─'*80}{Fore.RESET}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}КОНВЕРТАЦИЯ ВАЛЮТЫ{Fore.RESET}\n")
            
            # Выбор исходной валюты
            print(f"{Fore.WHITE}Доступные валюты:")
            display_currencies(available_currencies)
            print()
            
            from_currency = input(f"{Fore.YELLOW}Введите код исходной валюты: {Fore.RESET}").strip().upper()
            
            if from_currency not in available_currencies:
                print(f"{Fore.RED}Ошибка: Валюта '{from_currency}' не найдена!\n")
                continue
            
            # Выбор целевой валюты
            to_currency = input(f"{Fore.YELLOW}Введите код целевой валюты: {Fore.RESET}").strip().upper()
            
            if to_currency not in available_currencies:
                print(f"{Fore.RED}Ошибка: Валюта '{to_currency}' не найдена!\n")
                continue
            
            # Ввод суммы
            try:
                amount = float(input(f"{Fore.YELLOW}Введите сумму для конвертации: {Fore.RESET}").strip())
                if amount < 0:
                    print(f"{Fore.RED}Ошибка: Сумма не может быть отрицательной!\n")
                    continue
            except ValueError:
                print(f"{Fore.RED}Ошибка: Введите корректное число!\n")
                continue
            
            # Выполняем конвертацию
            result = convert_currency(data, amount, from_currency, to_currency)
            
            if result is None:
                print(f"{Fore.RED}Ошибка: Не удалось получить курс обмена между {from_currency} и {to_currency}!\n")
            else:
                print(f"\n{Fore.GREEN}{'='*80}")
                print(f"{Fore.GREEN}{Style.BRIGHT}РЕЗУЛЬТАТ КОНВЕРТАЦИИ{Fore.RESET}")
                print(f"{Fore.GREEN}{'='*80}{Fore.RESET}\n")
                print(f"{Fore.WHITE}  {amount:,.2f} {Fore.YELLOW}{from_currency}{Fore.RESET} = {Fore.GREEN}{result:,.2f} {Fore.YELLOW}{to_currency}{Fore.RESET}\n")
        
        elif choice == "2":
            # Показать курс обмена
            print(f"\n{Fore.CYAN}{'─'*80}{Fore.RESET}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}КУРС ОБМЕНА{Fore.RESET}\n")
            
            print(f"{Fore.WHITE}Доступные валюты:")
            display_currencies(available_currencies)
            print()
            
            from_currency = input(f"{Fore.YELLOW}Введите код исходной валюты: {Fore.RESET}").strip().upper()
            
            if from_currency not in available_currencies:
                print(f"{Fore.RED}Ошибка: Валюта '{from_currency}' не найдена!\n")
                continue
            
            to_currency = input(f"{Fore.YELLOW}Введите код целевой валюты: {Fore.RESET}").strip().upper()
            
            if to_currency not in available_currencies:
                print(f"{Fore.RED}Ошибка: Валюта '{to_currency}' не найдена!\n")
                continue
            
            # Получаем курс
            rate = get_exchange_rate(data, from_currency, to_currency)
            
            if rate is None:
                print(f"{Fore.RED}Ошибка: Не удалось получить курс обмена между {from_currency} и {to_currency}!\n")
            else:
                print(f"\n{Fore.GREEN}{'='*80}")
                print(f"{Fore.GREEN}{Style.BRIGHT}КУРС ОБМЕНА{Fore.RESET}")
                print(f"{Fore.GREEN}{'='*80}{Fore.RESET}\n")
                print(f"{Fore.WHITE}  1 {Fore.YELLOW}{from_currency}{Fore.RESET} = {Fore.GREEN}{rate:.6f} {Fore.YELLOW}{to_currency}{Fore.RESET}\n")
        
        elif choice == "3":
            # Список доступных валют
            print(f"\n{Fore.CYAN}{'─'*80}{Fore.RESET}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}ДОСТУПНЫЕ ВАЛЮТЫ{Fore.RESET}\n")
            print(f"{Fore.WHITE}Всего валют: {Fore.GREEN}{len(available_currencies)}{Fore.RESET}\n")
            display_currencies(available_currencies)
            print()
        
        else:
            print(f"{Fore.RED}Неверный выбор! Попробуйте снова.\n")


if __name__ == "__main__":
    main()
