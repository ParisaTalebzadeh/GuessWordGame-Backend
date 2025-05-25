from django.contrib import admin

from main.models import Game, Word, PlayerProfile, Guess, ScoreHistory

admin.site.register(PlayerProfile)
admin.site.register(Word)
admin.site.register(Game)
admin.site.register(Guess)
admin.site.register(ScoreHistory)
