from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers

from main.models import Game, ScoreHistory, PlayerProfile


class GameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['difficulty']



class GameSerializer(serializers.ModelSerializer):
    player1_username = serializers.CharField(source='player1.username', read_only=True)
    player2_username = serializers.CharField(source='player2.username', read_only=True)
    current_turn_username = serializers.CharField(source='current_turn.username', read_only=True)
    winner_username = serializers.CharField(source='winner.username', read_only=True, default=None)

    class Meta:
        model = Game
        fields = [
            'id', 'player1', 'player1_username',
            'player2', 'player2_username',
            'difficulty', 'status', 'word', 'masked_word',
            'guessed_letters', 'current_turn', 'current_turn_username',
            'winner', 'winner_username', 'created_at',
        ]
class GameStatusSerializer(serializers.ModelSerializer):
    player1_username = serializers.CharField(source='player1.username', read_only=True)
    player2_username = serializers.CharField(source='player2.username', read_only=True)
    current_turn_username = serializers.CharField(source='current_turn.username', read_only=True)
    winner_username = serializers.SerializerMethodField()
    your_score = serializers.SerializerMethodField()
    player1_score = serializers.IntegerField(read_only=True)
    player2_score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Game
        fields = [
            'id','status','player1_username','player2_username','current_turn_username','masked_word',
            'player1_score','player2_score','your_score','winner_username',
        ]

    def get_winner_username(self, obj):
        if obj.status != 'finished':
            return None
        if obj.player1_score > obj.player2_score:
            return obj.player1.username
        elif obj.player2_score > obj.player1_score:
            return obj.player2.username
        else:
            return None  # مساوی

    def get_your_score(self, obj):
        user = self.context['request'].user
        if user == obj.player1:
            return obj.player1_score
        elif user == obj.player2:
            return obj.player2_score
        return 0
class ScoreHistorySerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()
    opponent_name = serializers.SerializerMethodField()
    word = serializers.CharField(source='game.word')
    difficulty = serializers.CharField(source='game.difficulty')

    class Meta:
        model = ScoreHistory
        fields = ['score', 'result', 'opponent_name', 'word', 'difficulty', 'date']

    def get_result(self, obj):
        if obj.game.winner is None:
            return 'مساوی'
        if obj.is_winner:
            return 'برد'
        return 'باخت'

    def get_opponent_name(self, obj):
        if obj.game.player1 == obj.user:
            return obj.game.player2.username
        return obj.game.player1.username

class UserProfileSerializer(serializers.ModelSerializer):
    total_score = serializers.IntegerField(source='profile.total_score')
    games = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()  # ← اضافه شد

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'total_score', 'games', 'rank']

    def get_games(self, obj):
        finished_games = ScoreHistory.objects.filter(user=obj, game__status='finished')
        return ScoreHistorySerializer(finished_games, many=True).data

    def get_rank(self, obj):
        ordered_ids = list(
            PlayerProfile.objects
            .order_by('-total_score')
            .values_list('user_id', flat=True)
        )
        try:
            return ordered_ids.index(obj.id) + 1
        except ValueError:
            return None


class LeaderboardSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(source='profile.total_score', read_only=True)
    rank = serializers.SerializerMethodField()
    games_played = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'score', 'rank', 'games_played']
        read_only_fields = fields

    def get_rank(self, obj):
        ordered_ids = list(
            PlayerProfile.objects
            .order_by('-total_score')
            .values_list('user_id', flat=True)
        )
        try:
            return ordered_ids.index(obj.id) + 1
        except ValueError:
            return None

    def get_games_played(self, obj):
        return ScoreHistory.objects.filter(user=obj, game__status='finished').count()


    def get_rank(self, obj):
        ordered_ids = list(
            PlayerProfile.objects
            .order_by('-total_score')
            .values_list('user_id', flat=True)
        )
        try:
            return ordered_ids.index(obj.id) + 1
        except ValueError:
            return None
