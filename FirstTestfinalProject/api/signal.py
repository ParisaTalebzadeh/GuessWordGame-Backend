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

# @receiver(post_save, sender=Game)
# def create_scorehistory_for_finished_game(sender, instance, created, **kwargs):
#     if not created and instance.status == 'finished':
#         for player, score in [
#             (instance.player1, instance.player1_score),
#             (instance.player2, instance.player2_score),
#         ]:
#             if player:
#                 ScoreHistory.objects.get_or_create(
#                     user=player,
#                     game=instance,
#                     defaults={
#                         'score': score,
#                         'is_winner': (instance.winner == player)
#                     }
#                 )
#                 # و اگر می‌خواهید total_score را هم آپدیت کنید:
#                 profile = player.profile
#                 profile.total_score += score
#                 profile.save()
