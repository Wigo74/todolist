from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    tg_id = serializers.IntegerField(source='chat_id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    verification_code = serializers.CharField(write_only=True)

    def validate_verification_code(self, code: str) -> str:
        try:
            tg_user = TgUser.objects.get(verification_code=code)
        except TgUser.DoesNotExist:
            raise ValidationError('Invalid verification code')
        else:
            if tg_user.is_verified:
                raise ValidationError('Unsupported')
            self.instance = tg_user
            return code

    class Meta:
        model = TgUser
        fields = ('tg_id', 'username', 'verification_code', 'user_id')




