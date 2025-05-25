from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from main.models import Game


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if not username and not email:
            raise ValidationError("Either username or email must be provided.")

        if username and User.objects.filter(username=username).exists():
            raise ValidationError("This username has already been used.")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("This email has already been used.")

        return data

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')

        if not username:
            # استخراج بخش قبل از @ از ایمیل
            username = email.split('@')[0]
            # اگر این username هم وجود داشت، یکی اضافه کنیم (مثل username_1)
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1

        user = User.objects.create_user(
            username=username,
            password=validated_data['password'],
            email=email,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


# serializers.py

class GameDifficultySerializer(serializers.Serializer):
    difficulty = serializers.ChoiceField(choices=Game.DIFFICULTY_CHOICES)


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ['id', 'player1', 'player2', 'difficulty', 'status', 'word', 'masked_word', 'guessed_letters',
                  'current_turn', 'winner', 'created_at', ]
        # fields = ['id', 'difficulty']
