import factory
from pytest_factoryboy import register

from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import User
from goals.models import GoalCategory, Board, Goal, GoalComment, BoardParticipant
from bot.models import TgUser

USER_MODEL = get_user_model()


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User:
        return User.objects.create_user(*args, **kwargs)


class SignUpRequest(factory.DictFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    password_repeat = factory.LazyAttribute(lambda o: o.password)


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)


@register
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, owner=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(factory.django.DjangoModelFactory):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


@register
class CategoryFactory(factory.django.DjangoModelFactory):
    # title = 'New Category'
    title = factory.Faker('catch_phrase')
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = GoalCategory


@register
class GoalFactory(factory.django.DjangoModelFactory):
    # title = 'New Goal'
    # description = 'Description of New Goal'
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    title = factory.Faker('catch_phrase')

    class Meta:
        model = Goal

@register
class CreateGoalRequest(factory.DictFactory):
    title = factory.Faker('catch_phrase')


@register
class GoalCommentFactory(factory.django.DjangoModelFactory):
    # text = 'test comment'
    goal = factory.SubFactory(GoalFactory)
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence')

    class Meta:
        model = GoalComment


@register
class TuserFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    chat_id = factory.Faker('pyint')
    # user_ud = chat_id
    # username = user,
    verification_code = 'correct'

    class Meta:
        model = TgUser


# ======== ПРИМЕР ТЕСТА ТЕЛЕГРАММ БОТА ОТ УЧИТЕЛЯ =========================
@register
class TgUserFactory(factory.django.DjangoModelFactory):
    chat_id = factory.Faker('pyint', )
    # user_ud = factory.Faker('pyint',)
    # username = factory.Faker('user_name')
    verification_code = factory.Faker('pystr', max_chars=20)

    class Meta:
        model = TgUser
