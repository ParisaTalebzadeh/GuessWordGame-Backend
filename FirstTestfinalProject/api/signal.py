from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from main.models import PlayerProfile,Game, ScoreHistory

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
#
@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    if created:
        PlayerProfile.objects.create(user=instance)

@receiver(post_save, sender=Game)
def create_score_history_on_game_finish(sender, instance: Game, created, **kwargs):
    if instance.status != 'finished':
        return
    players_and_scores = []
    if instance.player1:
        players_and_scores.append((instance.player1, instance.player1_score))
    if instance.player2:
        players_and_scores.append((instance.player2, instance.player2_score))

    for player, score in players_and_scores:
        sh_obj, sh_created = ScoreHistory.objects.get_or_create(
            user=player,
            game=instance,
            defaults={'score': score, 'is_winner': (player == instance.winner)}
        )
        if sh_created:
            profile, _ = PlayerProfile.objects.get_or_create(user=player)
            profile.total_score += score
            profile.save()
