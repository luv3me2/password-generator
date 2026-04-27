
Password Generator - генератор безопасных паролей
Author: Васильев Александр Александрович
GitHub: [ТВОЙ_НИК]
"""

import random
import string
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


class PasswordGenerator:
    """
    Класс для генерации и управления паролями
    Поддерживает: выбор символов, проверку сложности, историю
    """
    
    def __init__(self):
        """Инициализация генератора"""
        self.history_file = Path("password_history.json")
        self._init_history()
    
    def _init_history(self):
        """Создание файла истории если его нет"""
        if not self.history_file.exists():
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def generate(self, length=12, use_digits=True, use_lower=True, 
                 use_upper=True, use_special=True, exclude_ambiguous=False):
        """
        Генерация пароля с заданными параметрами
        
        Args:
            length: длина пароля (4-100)
            use_digits: использовать цифры 0-9
            use_lower: использовать строчные буквы a-z
            use_upper: использовать заглавные буквы A-Z
            use_special: использовать спецсимволы !@#$%^&* и др.
            exclude_ambiguous: исключить похожие символы (1,l,I,0,O)
        
        Returns:
            str: сгенерированный пароль
        """
        # Проверка длины
        if length < 4:
            raise ValueError("Длина пароля должна быть минимум 4 символа")
        if length > 100:
            raise ValueError("Длина пароля не должна превышать 100 символов")
        
        # Собираем наборы символов
        char_sets = []
        char_names = []
        
        if use_digits:
            char_sets.append(string.digits)
            char_names.append("цифры")
        if use_lower:
            char_sets.append(string.ascii_lowercase)
            char_names.append("строчные")
        if use_upper:
            char_sets.append(string.ascii_uppercase)
            char_names.append("заглавные")
        if use_special:
            char_sets.append(string.punctuation)
            char_names.append("спецсимволы")
        
        # Проверка что выбран хотя бы один тип
        if not char_sets:
            raise ValueError("Выберите хотя бы один тип символов")
        
        # Объединяем все разрешённые символы
        all_chars = ''.join(char_sets)
        
        # Исключаем неоднозначные символы если нужно
        if exclude_ambiguous:
            ambiguous = '1lI0O'
            all_chars = ''.join(c for c in all_chars if c not in ambiguous)
        
        # Генерируем пароль с гарантией всех выбранных типов
        password_chars = []
        
        # Добавляем по одному символу из каждого выбранного типа
        for chars in char_sets:
            if chars:
                # Убираем неоднозначные символы из гарантийных символов
                available = chars
                if exclude_ambiguous:
                    available = ''.join(c for c in available if c not in '1lI0O')
                if available:  # Если после исключения остались символы
                    password_chars.append(random.choice(available))
        
        # Заполняем оставшиеся символы случайными из всех разрешённых
        remaining = length - len(password_chars)
        for _ in range(remaining):
            password_chars.append(random.choice(all_chars))
        
        # Перемешиваем символы для случайного порядка
        random.shuffle(password_chars)
        
        return ''.join(password_chars)
    
    def check_strength(self, password):
        """
        Проверка сложности пароля
        
        Args:
            password: пароль для проверки
        
        Returns:
            str: оценка сложности с эмодзи
        """
        score = 0
        length = len(password)
        
        # Оценка длины
        if length >= 16:
            score += 3
        elif length >= 12:
            score += 2
        elif length >= 8:
            score += 1
        
        # Оценка разнообразия символов
        has_digit = any(c.isdigit() for c in password)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_special = any(c in string.punctuation for c in password)
        
        if has_digit:
            score += 1
        if has_lower:
            score += 1
        if has_upper:
            score += 1
        if has_special:
            score += 2
        
        # Определяем уровень
        if score >= 8:
            return "🔒 ОЧЕНЬ СЛОЖНЫЙ"
        elif score >= 6:
            return "🔐 СЛОЖНЫЙ"
        elif score >= 4:
            return "⚠️ СРЕДНИЙ"
        else:
            return "❌ СЛАБЫЙ"
    
    def save_to_history(self, password, service="", length=0, strength=""):
        """
        Сохранение пароля в историю
        
        Args:
            password: пароль
            service: название сервиса
            length: длина пароля
            strength: оценка сложности
        """
        try:
            # Загружаем существующую историю
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Добавляем новую запись
            history.append({
                "password": password,
                "service": service if service else "не указан",
                "length": length,
                "strength": strength,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Ограничиваем историю 100 записями
            if len(history) > 100:
                history = history[-100:]
            
            # Сохраняем обратно
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Ошибка сохранения в историю: {e}")
            return False
    
    def view_history(self, limit=10):
        """
        Просмотр истории паролей
        
        Args:
            limit: количество последних записей для показа
        """
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not history:
                print("\n📭 История пуста. Сгенерируйте и сохраните пароль.")
                return
            
            print("\n" + "="*70)
            print("📜 ИСТОРИЯ ПАРолей (последние {})".format(min(limit, len(history))))
            print("="*70)
            
            # Показываем последние N записей (в обратном порядке)
            for i, entry in enumerate(reversed(history[-limit:]), 1):
                print(f"\n{i}. 📱 Сервис: {entry.get('service', 'N/A')}")
                print(f"   🔑 Пароль: {entry['password']}")
                print(f"   📊 Сложность: {entry.get('strength', 'N/A')}")
                print(f"   📏 Длина: {entry.get('length', 'N/A')}")
                print(f"   🕐 Дата: {entry.get('created', 'N/A')}")
            
            print("\n" + "="*70)
            print(f"💡 Всего сохранено паролей: {len(history)}")
        
        except Exception as e:
            print(f"Ошибка чтения истории: {e}")
    
    def clear_history(self, confirm=False):
        """
        Очистка истории паролей
        
        Args:
            confirm: подтверждение очистки
        """
        if not confirm:
            print("⚠️ Для очистки истории используйте флаг --clear-force")
            return
        
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            print("✅ История успешно очищена")
        except Exception as e:
            print(f"Ошибка очистки истории: {e}")
    
    def get_stats(self):
        """
        Получение статистики по паролям
        
        Returns:
            dict: статистика
        """
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not history:
                return {"total": 0, "avg_length": 0, "strength_stats": {}}
            
            total = len(history)
            avg_length = sum(h['length'] for h in history) / total
            
            # Подсчёт по уровням сложности
            strength_stats = {}
            for entry in history:
                strength = entry.get('strength', 'неизвестно')
                strength_stats[strength] = strength_stats.get(strength, 0) + 1
            
            return {
                "total": total,
                "avg_length": round(avg_length, 1),
                "strength_stats": strength_stats
            }
        
        except Exception:
            return {"total": 0, "avg_length": 0, "strength_stats": {}}


def main():
    """Главная функция с парсингом аргументов командной строки"""
    
    parser = argparse.ArgumentParser(
        description="🔐 Password Generator - генератор безопасных паролей",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
📌 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
  %(prog)s                              # Пароль 12 символов
  %(prog)s -l 16                        # Пароль 16 символов
  %(prog)s -l 20 --no-special           # Без спецсимволов
  %(prog)s --exclude-ambiguous          # Исключить 1,l,I,0,O
  %(prog)s -n 5 -l 14                   # 5 паролей по 14 символов
  %(prog)s --check "MyPass123"          # Проверить сложность
  %(prog)s --history                    # Показать историю
  %(prog)s -l 16 -s "gmail"             # Сохранить для сервиса

⭐ GitHub: [ТВОЙ_НИК]/password-generator
        """
    )
    
    # Основные параметры
    parser.add_argument('-l', '--length', type=int, default=12,
                       help='Длина пароля (по умолчанию: 12, мин: 4, макс: 100)')
    parser.add_argument('-n', '--count', type=int, default=1,
                       help='Количество паролей (по умолчанию: 1)')
    
    # Типы символов
    parser.add_argument('--no-digits', action='store_false', dest='digits',
                       help='Не использовать цифры')
    parser.add_argument('--no-lower', action='store_false', dest='lower',
                       help='Не использовать строчные буквы')
    parser.add_argument('--no-upper', action='store_false', dest='upper',
                       help='Не использовать заглавные буквы')
    parser.add_argument('--no-special', action='store_false', dest='special',
                       help='Не использовать спецсимволы')
    parser.add_argument('--exclude-ambiguous', action='store_true',
                       help='Исключить похожие символы (1, l, I, 0, O)')
    
    # Дополнительные функции
    parser.add_argument('-s', '--save', type=str, metavar='SERVICE',
                       help='Сохранить пароль в историю (указать сервис)')
    parser.add_argument('--history', action='store_true',
                       help='Показать историю сохранённых паролей')
    parser.add_argument('--history-all', action='store_true',
                       help='Показать всю историю (без ограничений)')
    parser.add_argument('--check', type=str, metavar='PASSWORD',
                       help='Проверить сложность пароля')
    parser.add_argument('--stats', action='store_true',
                       help='Показать статистику по паролям')
    parser.add_argument('--clear-force', action='store_true',
                       help='Очистить историю (требуется подтверждение)')
    parser.add_argument('--quiet', action='store_true',
                       help='Тихий режим (только пароль)')
    
    args = parser.parse_args()
    
    # Проверка длины
    if args.length < 4 or args.length > 100:
        print("❌ Ошибка: длина пароля должна быть от 4 до 100 символов")
        sys.exit(1)
    
    generator = PasswordGenerator()
    
    # Режим просмотра истории
    if args.history:
        limit = 10 if not args.history_all else 999
        generator.view_history(limit)
        return
    
    # Режим статистики
    if args.stats:
        stats = generator.get_stats()
        print("\n" + "="*50)
        print("📊 СТАТИСТИКА ПАРОЛЕЙ")
        print("="*50)
        print(f"📝 Всего паролей: {stats['total']}")
        print(f"📏 Средняя длина: {stats['avg_length']} символов")
        if stats['strength_stats']:
            print("\n📈 Распределение по сложности:")
            for strength, count in stats['strength_stats'].items():
                print(f"   {strength}: {count}")
        print("="*50)
        return
    
    # Режим очистки истории
    if args.clear_force:
        generator.clear_history(confirm=True)
        return
    
    # Режим проверки пароля
    if args.check:
        strength = generator.check_strength(args.check)
        print(f"\n🔍 Пароль: {args.check}")
        print(f"📊 Сложность: {strength}")
        print(f"📏 Длина: {len(args.check)} символов")
        
        # Дополнительные рекомендации
        if len(args.check) < 8:
            print("\n💡 Рекомендация: используйте пароль длиннее 8 символов")
        if not any(c.isupper() for c in args.check):
            print("💡 Рекомендация: добавьте заглавные буквы")
        if not any(c.isdigit() for c in args.check):
            print("💡 Рекомендация: добавьте цифры")
        if not any(c in string.punctuation for c in args.check):
            print("💡 Рекомендация: добавьте спецсимволы (!@#$%^&*)")
        return
    
    # Режим генерации
    try:
        if args.count == 1:
            # Генерация одного пароля
            password = generator.generate(
                length=args.length,
                use_digits=args.digits,
                use_lower=args.lower,
                use_upper=args.upper,
                use_special=args.special,
                exclude_ambiguous=args.exclude_ambiguous
            )
            
            strength = generator.check_strength(password)
            
            if args.quiet:
                print(password)
            else:
                print("\n" + "="*60)
                print("🔑 СГЕНЕРИРОВАННЫЙ ПАРОЛЬ")
                print("="*60)
                print(f"\n🔐 Пароль: {password}")
                print(f"📏 Длина: {len(password)} символов")
                print(f"📊 Сложность: {strength}")
                print("="*60)
            
            # Сохранение в историю
            if args.save:
                generator.save_to_history(
                    password=password,
                    service=args.save,
                    length=args.length,
                    strength=strength
                )
                if not args.quiet:
                    print(f"\n💾 Сохранено для сервиса: {args.save}")
        
        else:
            # Генерация нескольких паролей
            passwords = []
            for _ in range(args.count):
                pwd = generator.generate(
                    length=args.length,
                    use_digits=args.digits,
                    use_lower=args.lower,
                    use_upper=args.upper,
                    use_special=args.special,
                    exclude_ambiguous=args.exclude_ambiguous
                )
                passwords.append(pwd)
            
            if args.quiet:
                for pwd in passwords:
                    print(pwd)
            else:
                print("\n" + "="*60)
                print(f"🔑 {args.count} СГЕНЕРИРОВАННЫХ ПАРОЛЕЙ")
                print("="*60)
                
                for i, pwd in enumerate(passwords, 1):
                    strength = generator.check_strength(pwd)
                    print(f"\n{i}. {pwd}")
                    print(f"   📊 Сложность: {strength}")
                
                print("\n" + "="*60)
            
            # Сохранение всех в историю
            if args.save:
                for pwd in passwords:
                    generator.save_to_history(
                        password=pwd,
                        service=f"{args.save}_batch",
                        length=args.length,
                        strength=generator.check_strength(pwd)
                    )
                if not args.quiet:
                    print(f"\n💾 {args.count} паролей сохранено для сервиса: {args.save}")
    
    except ValueError as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
        sys.exit(0)
