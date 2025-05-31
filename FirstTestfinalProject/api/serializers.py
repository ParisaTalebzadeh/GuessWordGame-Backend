from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers

from main.models import Game, ScoreHistory, PlayerProfile


class GameDifficultySerializer(serializers.Serializer):
    difficulty = serializers.ChoiceField(choices=Game.DIFFICULTY_CHOICES)


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            'id', 'player1', 'player2', 'difficulty', 'status',
            'word', 'masked_word', 'guessed_letters',
            'current_turn', 'winner', 'created_at',
        ]


class ScoreHistorySerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()
    opponent_name = serializers.SerializerMethodField()
    word = serializers.CharField(source='game.word')
    difficulty = serializers.CharField(source='game.difficulty')

    class Meta:
        model = ScoreHistory
        fields = ['score', 'result', 'opponent_name', 'word', 'difficulty', 'date']

    def get_result(self, obj):
        # نتیجه برد یا باخت بسته به اینکه کاربر برابر با برنده بازی است یا خیر
        if obj.game.winner == obj.user:
            return 'برد'
        return 'باخت'

    def get_opponent_name(self, obj):
        # نام حریف بازی (به عنوان مثال اگر مدل بازی دو فیلد player1 و player2 داشته باشد)
        if obj.game.player1 == obj.user:
            return obj.game.player2.username
        return obj.game.player1.username

class UserProfileSerializer(serializers.ModelSerializer):
    total_score = serializers.IntegerField(source='profile.total_score')
    games = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'total_score', 'games']

    def get_games(self, obj):
        # فیلتر بازی‌های تمام‌شده کاربر
        finished_games = ScoreHistory.objects.filter(user=obj, game__status='finished')
        return ScoreHistorySerializer(finished_games, many=True).data


class LeaderboardSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(source='profile.total_score', read_only=True)
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'score', 'rank']
        read_only_fields = fields


    def get_rank(self, obj):
        """
        محاسبهٔ رتبه بر اساس total_score (نزولی).
        برای هر User، ابتدا لیستی از همهٔ PlayerProfileها را می‌گیریم،
        به ترتیب نزولی روی total_score مرتب می‌کنیم، سپس
        idxِ user.id را پیدا می‌کنیم و +1 می‌کنیم.
        """
        # لیست user_idها را بر اساس total_score نزولی می‌گیریم
        ordered_ids = list(
            PlayerProfile.objects
            .order_by('-total_score')
            .values_list('user_id', flat=True)
        )
        try:
            return ordered_ids.index(obj.id) + 1
        except ValueError:
            # اگر کاربری در PlayerProfile نباشد (نباید پیش بیاید)
            return None