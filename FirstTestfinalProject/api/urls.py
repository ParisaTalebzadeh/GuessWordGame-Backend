from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from api.views import RegisterAPIView, CreateGameAPIView, JoinGameAPIView, WaitingGamesListAPIView, GuessAPIView, \
    PauseGameAPIView, ResumeGameAPIView, GuessFullWordAPIView, UserProfileAPIView, \
    UserGameHistoryAPIView, LeaderboardAPIView, GameStatusAPIView

urlpatterns = [
    path('login/', obtain_auth_token),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('games/<int:game_id>/status/', GameStatusAPIView.as_view(), name='game-status'),
    path('create/game/', CreateGameAPIView.as_view(), name='create-game'),
    path('waitinglist/', WaitingGamesListAPIView.as_view(), name='waiting-games-list'),
    path('games/<int:game_id>/join/', JoinGameAPIView.as_view(), name='join-game'),
    path('games/<int:game_id>/pause/', PauseGameAPIView.as_view(), name='pause-game'),
    path('games/<int:game_id>/resume/', ResumeGameAPIView.as_view(), name='resume-game'),
    path('games/<int:game_id>/guess/', GuessAPIView.as_view(), name='guess-letter'),
    path('games/<int:game_id>/guess-full-word/', GuessFullWordAPIView.as_view(), name='guess-full-word'),
    path('history/', UserGameHistoryAPIView.as_view(), name='game-history'),
    path('leaderboard/', LeaderboardAPIView.as_view(), name='leaderboard'),


]


