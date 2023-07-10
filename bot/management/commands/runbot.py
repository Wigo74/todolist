import logging

from django.core.management import BaseCommand
from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import Goal, GoalCategory, BoardParticipant


states = {}
cat_id = []


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **kwargs):
        offset = 0

        self.stdout.write(self.style.SUCCESS('Bot started'))
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        self.tg_client.send_message(chat_id=msg.chat.id, text=msg.text)
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)
        if tg_user.is_verified:
            self.handle_authorized(tg_user, msg)
        else:
            self.handle_unauthorized(tg_user, msg)

    def handle_unauthorized(self, tg_user: TgUser, msg: Message):

        self.tg_client.send_message(tg_user.chat_id, 'Hello')
        tg_user.update_verification_code()
        self.tg_client.send_message(tg_user.chat_id, f'Your verification code: {tg_user.verification_code}')

    def handle_authorized(self, tg_user: TgUser, msg: Message):
        self.tg_client.send_message(tg_user.chat_id, 'Authorized')

        allowed_commands: list[str] = ['/goals', '/create', '/cancel']
        if "/board" in msg.text:
            self.board(msg, tg_user)
        elif '/goals' in msg.text:
            self.get_goals(msg, tg_user)

        elif '/create' in msg.text:
            self.handle_categories(msg, tg_user)

        elif '/cancel' in msg.text:
            self.get_cancel(tg_user)

        elif ('user' not in states) and (msg.text not in allowed_commands):
            self.tg_client.send_message(tg_user.chat_id, 'Command not found')

        elif (msg.text not in allowed_commands) and (states['user']) and \
                ('category' not in states):
            category = self.handle_save_category(tg_user, msg.text)
            if category:
                states['category'] = category
                self.tg_client.send_message(tg_user.chat_id,
                                            f'You choosed {category.title}, category, please enter name for your goal')

        elif (msg.text not in allowed_commands) and (states['user']) and \
                (states['category']) and ('goal_title' not in states):
            states['goal_title'] = msg.text
            goal = Goal.objects.create(title=states['goal_title'],
                                       user=states['user'],
                                       category=states['category'])
            self.tg_client.send_message(tg_user.chat_id, f'Your goal {goal} has been created')
            del states['user']
            del states['category']
            del states['goal_title']
            cat_id.clear()

    def board(self, msg, tg_user: TgUser):
        boards = BoardParticipant.objects.filter(user=tg_user.user)
        if boards:
            [self.tg_client.send_message(msg.chat.id, f"Boards: {item.board}\n") for item in boards]
        else:
            self.tg_client.send_message(msg.chat.id, "Not Board")

    def get_goals(self, msg: Message, tg_user: TgUser):
        goals = Goal.objects.filter(user=tg_user.user).exclude(status=Goal.Status.archived)

        if goals.count() > 0:
           [self.tg_client.send_message(msg.chat.id,
                                        f'Название: {goal.title},\n'
                                        f'Категория: {goal.category},\n'
                                        f'Статус: {goal.get_status_display()},\n'
                                        f'Пользователь: {goal.user},\n'
                                        f'Дедлайн {goal.due_date if goal.due_date else "Нет"} \n')
                                        for goal in goals]

        else:
            self.tg_client.send_message(msg.chat.id, 'No Goals to display, create one with /create command')

    def handle_categories(self, msg, tg_user: TgUser):
        categories = GoalCategory.objects.filter(user=tg_user.user, is_deleted=False)
        if categories.count() > 0:
            category_list = ''
            for cat in categories:
                category_list += f'{cat.id}: {cat.title} \n'
                cat_id.append(cat.id)
            self.tg_client.send_message(
                chat_id=tg_user.chat_id,
                text=f'Please choose the Category, to create goal\n{category_list}')
        if 'user' not in states:
            states['user'] = tg_user.user
        else:
            self.tg_client.send_message(msg.chat.id, 'No Categories found, first create category '
                                                     'on website for your goals')

    def handle_save_category(self, tg_user: TgUser, msg: str):
        messg = f'Unknown command'
        try:
            category_id = int(msg)
            category_data = GoalCategory.objects.filter(user=tg_user.user).get(pk=category_id)
            return category_data
        except ValueError:
            self.tg_client.send_message(chat_id=tg_user.chat_id, text=messg)
            return None

    def get_cancel(self, tg_user: TgUser):
        if 'user' in states:
            del states['user']
        if 'category' in states:
            del states['category']
        if 'goal_title' in states:
            del states['goal_title']
        self.tg_client.send_message(tg_user.chat_id, 'Operation canceled')
