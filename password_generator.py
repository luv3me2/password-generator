#!/usr/bin/env python3
"""
Password Generator - профессиональный генератор паролей
Author: Васильев Александр Александрович
GitHub: https://github.com/luv3me2/password-generator.git
"""

import random
import string
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

class PasswordGenerator:
    """Класс для генерации и управления паролями"""
    
    def __init__(self):
        self.history_file = Path("password_history.json")
        self._init_history()
    
    def _init_history(self):
        """Инициализация файла истории"""
        if not self.history_file.exists():
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def save_to_history(self, password, service="cli", length=0, strength=""):
        """Сохранение пароля в историю"""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            history.append({
                "password": password,
                "service": service,
                "length": length,
                "strength": strength,
                "created": datetime.now().isoformat()
            })
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def view_history(self):
        """Просмотр истории сгенерированных паролей"""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            if not history:
                print("\n📭 История пуста")
                return
            
            print("\n" + "="*60)
            print("📜 ИСТОРИЯ ПАРОЛЕЙ")
            print("="*60)
            
            for i, entry in enumerate(history[-10:], 1):  # последние 10
                print(f"\n{i}. Сервис: {entry.get('service', 'N/A')}")
                print(f"   Пароль: {entry['password']}")
                print(f"   Сложность: {entry.get('strength', 'N/A')}")
                print(f"   Длина: {entry.get('length', 'N/A')}")
                print(f"   Дата: {entry.get('created', 'N/A')[:19]}")
            
            print("\n" + "="*60)
        except Exception as e:
            print(f"Ошибка чтения истории: {e}")
    
    def check_strength(self, password):
        """Проверка сложности пароля"""
        score = 0
        
        # Длина
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        
        # Наличие разных типов символов
        if any(c.isdigit() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c in string.punctuation for c in password):
            score += 2
        
        # Оценка
        if score >= 6:
            return "🔒 ОЧЕНЬ СЛОЖНЫЙ"
        elif score >= 4:
            return "🔐 СЛОЖНЫЙ"
        elif score >= 2:
            return "⚠️ СРЕДНИЙ"
        else:
            return "❌ СЛАБЫЙ"
    
    def generate(self, length=12, use_digits=True, use_lower=True, 
                 use_upper=True, use_special=True, exclude_ambiguous=False):
        """
        Генерация пароля с заданными параметрами
        
        Args:
            length: длина пароля
            use_digits: использовать цифры
            use_lower: использовать строчные буквы
            use_upper: использовать заглавные буквы
            use_special: использовать спецсимволы
            exclude_ambiguous: исключать похожие символы (1,l,I,0,O)
        """
        
        # Базовые наборы символов
        char_sets = []
        if use_digits:
            char_sets.append(string.digits)
        if use_lower:
            char_sets.append(string.ascii_lowercase)
        if use_upper:
            char_sets.append(string.ascii_uppercase)
        if use_special:
            char_sets.append(string.punctuation)
        
        if not char_sets:
            raise ValueError("Должен быть выбран хотя бы один тип символов")
        
        # Исключаем неоднозначные символы
        ambiguous = '1lI0O' if exclude_ambiguous else ''
        
        # Объединяем наборы
        all_chars = ''.join(char_sets)
        all_chars = ''.join(c for c in all_chars if c not in ambiguous)
        
        # Генерация с гарантией всех типов
        password = []
        
        # Добавляем хотя бы один символ из каждого выбранного типа
        if use_digits:
            password.append(random.choice(string.digits))
        if use_lower:
            password.append(random.choice(string.ascii_lowercase))
        if use_upper:
            password.append(random.choice(string.ascii_uppercase))
        if use_special:
            password.append(random.choice(string.punctuation))
        
        # Заполняем остальное случайными символами
        for _ in range(length - len(password)):
            password.append(random.choice(all_chars))
        
        # Перемешиваем
        random.shuffle(password)
        
        return ''.join(password)
    
    def generate_multiple(self, count=5, **kwargs):
        """Генерация нескольких паролей"""
        passwords = []
        for _ in range(count):
            passwords.append(self.generate(**kwargs))
        return passwords

def main():
    parser = argparse.ArgumentParser(
        description="Генератор паролей с расширенными функциями",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s -l 16                     # Пароль длиной 16 символов
  %(prog)s -l 20 --no-special        # Без спецсимволов
  %(prog)s -l 12 --exclude-ambiguous # Исключить 1,l,I,0,O
  %(prog)s -n 5 -l 14                # Сгенерировать 5 паролей
  %(prog)s --history                  # Показать историю
  %(prog)s --check "MyPass123"       # Проверить сложность
        """
    )
    
    # Основные параметры
    parser.add_argument('-l', '--length', type=int, default=12,
                       help='Длина пароля (по умолчанию: 12)')
    parser.add_argument('-n', '--count', type=int, default=1,
                       help='Количество паролей (по умолчанию: 1)')
    parser.add_argument('--no-digits', action='store_false', dest='digits',
                       help='Не использовать цифры')
    parser.add_argument('--no-lower', action='store_false', dest='lower',
                       help='Не использовать строчные буквы')
    parser.add_argument('--no-upper', action='store_false', dest='upper',
                       help='Не использовать заглавные буквы')
    parser.add_argument('--no-special', action='store_false', dest='special',
                       help='Не использовать спецсимволы')
    parser.add_argument('--exclude-ambiguous', action='store_true',
                       help='Исключить похожие символы (1,l,I,0,O)')
    
    # Дополнительные функции
    parser.add_argument('--save', type=str, metavar='SERVICE',
                       help='Сохранить пароль в историю (указать имя сервиса)')
    parser.add_argument('--history', action='store_true',
                       help='Показать историю паролей')
    parser.add_argument('--check', type=str, metavar='PASSWORD',
                       help='Проверить сложность пароля')
    
    args = parser.parse_args()
    
    generator = PasswordGenerator()
    
    # Режим просмотра истории
    if args.history:
        generator.view_history()
        return
    
    # Режим проверки пароля
    if args.check:
        strength = generator.check_strength(args.check)
        print(f"\nПароль: {args.check}")
        print(f"Сложность: {strength}")
        print(f"Длина: {len(args.check)} символов")
        return
    
    # Режим генерации
    try:
        if args.count == 1:
            # Генерируем один пароль
            password = generator.generate(
                length=args.length,
                use_digits=args.digits,
                use_lower=args.lower,
                use_upper=args.upper,
                use_special=args.special,
                exclude_ambiguous=args.exclude_ambiguous
            )
            
            # Проверяем сложность
            strength = generator.check_strength(password)
            
            # Выводим результат
            print("\n" + "="*50)
            print("🔑 СГЕНЕРИРОВАННЫЙ ПАРОЛЬ")
            print("="*50)
            print(f"\nПароль: {password}")
            print(f"Длина: {len(password)} символов")
            print(f"Сложность: {strength}")
            print("="*50)
            
            # Сохраняем если нужно
            if args.save:
                generator.save_to_history(
                    password=password,
                    service=args.save,
                    length=args.length,
                    strength=strength
                )
                print(f"\n✅ Сохранено для сервиса: {args.save}")
        
        else:
            # Генерируем несколько паролей
            passwords = generator.generate_multiple(
                count=args.count,
                length=args.length,
                use_digits=args.digits,
                use_lower=args.lower,
                use_upper=args.upper,
                use_special=args.special,
                exclude_ambiguous=args.exclude_ambiguous
            )
            
            print("\n" + "="*50)
            print(f"🔑 {args.count} СГЕНЕРИРОВАННЫХ ПАРОЛЕЙ")
            print("="*50)
            
            for i, pwd in enumerate(passwords, 1):
                strength = generator.check_strength(pwd)
                print(f"\n{i}. {pwd}")
                print(f"   Сложность: {strength}")
            
            print("\n" + "="*50)
            
            # Сохраняем все если нужно
            if args.save:
                for pwd in passwords:
                    generator.save_to_history(
                        password=pwd,
                        service=args.save,
                        length=args.length,
                        strength=generator.check_strength(pwd)
                    )
                print(f"\n✅ {args.count} паролей сохранено для сервиса: {args.save}")
    
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
