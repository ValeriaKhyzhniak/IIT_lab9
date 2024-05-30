import telebot
from decimal import Decimal
import logging
from fluent import sender
from fluent import event

# Налаштування Fluentd
logger = sender.FluentSender('telegram_bot', host='localhost', port=24224)

# Налаштування стандартного логування
logging.basicConfig(level=logging.INFO)
fluent_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fluent_handler.setFormatter(formatter)
logging.getLogger().addHandler(fluent_handler)

bot = telebot.TeleBot("7080557202:AAHUXlYCck-y5g12Nx7ZTIyCNISFmB7ZxZw")

@bot.message_handler(commands=['show'])
def send_welcome(message):
    show_message = """
    Розробкою займались:
    Хижняк Валерія Валеріївна
    Костенко Павло Сергійович
    Сидорук Аліна Констянтинівна
    """
    bot.reply_to(message, show_message)
    logger.emit('bot_command', {'command': 'show', 'user': message.from_user.username})

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = """
    Привіт, """ + message.from_user.first_name + """! Я бот, здатний виконувати прості математичні операції (ТОБТО МНОЖЕННЯ, ДІЛЕННЯ, ДОДАВАННЯ ТА ВІДНІМАННЯ) з двома числами.
    Просто введіть два числа та операцію між ними (наприклад, 2 + 3), 
    і я вам надішлю результат. Не забудьте розділити числа та операцію пробілом.
    Для допомоги напишіть /help
    """
    bot.reply_to(message, welcome_message)
    logger.emit('bot_command', {'command': 'start', 'user': message.from_user.username})

@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = """
    Як використовувати цього бота:

    /start - початок роботи з ботом
    /help - показати цей довідник
    /show - отримати інформацію про розробників
    Для виконання операцій просто напишіть повідомлення з операцією (наприклад, 2 + 3)
    """
    bot.reply_to(message, help_message)
    logger.emit('bot_command', {'command': 'help', 'user': message.from_user.username})

@bot.message_handler(func=lambda message: True)
def calculate(message):
    try:
        text = message.text.split()
        num1 = Decimal(text[0])
        num2 = Decimal(text[2])
        operation = text[1]
        if operation == '/' and num2 == 0:
            bot.reply_to(message, 'Ділення на нуль неможливе. ' + message.from_user.first_name + ', хіба Вас в школі не вчили, що на нуль ділити не можна?)')
            logger.emit('calculation_error', {'error': 'division by zero', 'user': message.from_user.username, 'input': message.text})
            return
        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            result = num1 / num2
        else:
            bot.reply_to(message, 'Будь ласка, введіть коректну операцію.')
            logger.emit('calculation_error', {'error': 'invalid operation', 'user': message.from_user.username, 'input': message.text})
            return
        bot.reply_to(message, f'Результат: {result}')
        logger.emit('calculation', {'operation': operation, 'num1': str(num1), 'num2': str(num2), 'result': str(result), 'user': message.from_user.username})
    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так. Схоже такої команди немає, або команду було введено не корректно. Спробуйте ще раз пізніше.')
        logger.emit('calculation_error', {'error': str(e), 'user': message.from_user.username, 'input': message.text})

bot.polling()
