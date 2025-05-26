from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.total_score} pts"


class Word(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),    # کلمات 4-5 حرفی
        ('medium', 'Medium'),  # کلمات 6-7 حرفی
        ('hard', 'Hard'),     # کلمات 8 حرفی یا بیشتر
    ]

    text = models.CharField(max_length=100, unique=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)

    def __str__(self):
        return f"{self.text} ({self.difficulty})"


class Game(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),  # 4-5 حرفی، 10 دقیقه
        ('medium', 'Medium'),  # 6-7 حرفی، 7 دقیقه
        ('hard', 'Hard'),  # 8+ حرفی، 5 دقیقه
    ]

    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
        ('paused','Paused')
    ]

    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_created')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='games_joined')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)

    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='word_games')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)

    # چه کسی الان باید حدس بزنه؟
    current_turn = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='turn_games')

    # برنده بازی بعد از اتمام مشخص می‌شود
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')

    # حروفی که حدس زده شده‌اند: مثلاً A,D,E
    guessed_letters = models.TextField(default="")

    # نمایش وضعیت کلمه: مثلاً _ _ A _ E
    masked_word = models.CharField(max_length=100, default="")
    wrong_guesses = models.JSONField(default=dict)
    def __str__(self):
        return f"Game #{self.id} - {self.get_difficulty_display()}"

    def is_full(self):
        return self.player1 is not None and self.player2 is not None

    def __str__(self):
        return f"{self.player1.username} vs {self.player2.username if self.player2 else 'Waiting...'}"


class Guess(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='guesses')
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    letter = models.CharField(max_length=1)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} guessed '{self.letter}' in Game #{self.game.id}"


class ScoreHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField()
    is_winner = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        result = "Won" if self.is_winner else "Lost"
        return f"{self.user.username} - {self.score} pts ({result})"
