import logging

from telebot import TeleBot
from telebot.types import Message

from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from goals.models import Goal, GoalCategory, BoardParticipant

# =============== Enable logging  ==============================
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("start bot")

user_states = {'state': {}}
cat_id = []

logger.info(user_states)
logger.info(cat_id)

bot = TeleBot(settings.BOT_TOKEN, threaded=False)

allowed_commands = ['/goals', '/create', '/cancel']


@bot.message_handler(commands=['start', 'help', 'cancel'])
def handle_user_without_verification(msg: Message):
    """ Проверочный код. Обрабатывать пользователя без проверки """
    tg_user, _ = TgUser.objects.get_or_create(user_ud=msg.from_user.id,
                                              defaults={"chat_id": msg.chat.id, "username": msg.from_user.username})

    if tg_user.user:
        send_welcome(msg)

    else:
        bot.send_message(
            msg.chat.id,
            'Добро пожаловать!\n'
            'Для продолжения работы необходимо привязать\n'
            'Ваш аккаунт на сайте https://example.com\n',
        )
        tg_user.set_verification_code()
        tg_user.save(update_fields=["verification_code"])
        bot.send_message(msg.chat.id, f"Верификационный  код: {tg_user.verification_code}")


def send_welcome(msg: Message):
    """ Отправка приветственного сообщения и помощи в командах """
    if msg.text == '/start':
        bot.send_message(msg.chat.id, f"Приветствую! {msg.chat.first_name}\n"
                                      'Бот может работать и обрабатывает следующие команды:\n'
                                      '/board -> выводит список досок задач\n'
                                      '/category -> выводит список категорий\n'
                                      '/goals -> выводит список целей\n'
                                      '/create -> позволяет создавать новые цели\n'
                                      '/cancel -> позволяет отменить создание цели (только на этапе создания)\n')

    elif ('user' not in user_states['state']) and (msg.text not in allowed_commands):
        bot.send_message(msg.chat.id, 'Неизвестная команда')


class Command(BaseCommand):
    help = "run bot"

    def handle(self, *args, **options):
        bot.polling()
