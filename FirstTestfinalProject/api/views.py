import random

from django.http import JsonResponse
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from api.serializers import UserSerializer, GameSerializer, GameDifficultySerializer
from main.models import Word, Game,Guess



class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                }, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GameDifficultySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        difficulty = serializer.validated_data['difficulty']

        words = Word.objects.filter(difficulty=difficulty)
        if not words.exists():
            return Response({'error': 'No words available for this difficulty.'}, status=status.HTTP_404_NOT_FOUND)

        word_obj = random.choice(words)
        word = word_obj.text.upper()
        masked = '_' * len(word)

        game = Game.objects.create(
            player1=request.user,
            word=word_obj,
            difficulty=difficulty,
            masked_word=masked,
            status='waiting',
            current_turn=request.user
        )

        response_serializer = GameSerializer(game)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class JoinGameAPIView(APIView):

    def post(self, request, *args, **kwargs):
        game_id = kwargs.get('game_id')
        game = get_object_or_404(Game, pk=game_id)
        if game.status != 'waiting':
            return Response(
                {'message': 'You can only join games in waiting status'},
                status=400
            )
        if game.player2:
            return Response(
                {'message': 'This game is already full!'},
                status=400)
        if game.player1 == request.user:
            return Response(
                {'message': 'You cant join your own game!'},
                status=400)
        game.player2 = request.user
        game.status = 'in_progress'
        game.save()

        return Response(
            {'message': 'You have joined the game!'},
            status=200)


class WaitingGamesListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GameSerializer

    def get_queryset(self):
        user = self.request.user

        # بازی‌هایی که در حالت waiting هستن و هنوز بازیکن دوم ندارن
        waiting_games = Game.objects.filter(status='waiting', player2__isnull=True)

        # بازی‌هایی که در حالت paused هستن و کاربر فعلی توش شرکت داشته
        paused_games = Game.objects.filter(
            status='paused'
        ).filter(
            player1=user
        ) | Game.objects.filter(
            status='paused',
            player2=user
        )

        # Union این دو queryset
        return waiting_games.union(paused_games)

class PauseGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)

        if game.status != 'in_progress':
            return Response({'error': 'Only games in progress can be paused.'}, status=400)

        if request.user != game.player1 and request.user != game.player2:
            return Response({'error': 'You are not a player in this game.'}, status=403)

        game.status = 'paused'
        game.save()

        return Response({'message': 'Game paused successfully.'}, status=200)


class ResumeGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)

        if game.status != 'paused':
            return Response({'error': 'Only paused games can be resumed.'}, status=400)

        if request.user != game.player1 and request.user != game.player2:
            return Response({'error': 'You are not a player in this game.'}, status=403)

        game.status = 'in_progress'
        game.save()

        return Response({'message': 'Game resumed successfully.'}, status=200)


class GuessAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        user = request.user
        letter = request.data.get('letter')
        position = request.data.get('position')  # position: یک عدد

        if letter is None or position is None:
            return Response({'detail': 'Both "letter" and "position" are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            position = int(position)
        except ValueError:
            return Response({'detail': '"position" must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        game = get_object_or_404(Game, id=game_id)

        # بررسی وضعیت بازی
        if game.status != 'in_progress':
            return Response({'detail': 'Game is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        if game.current_turn != user:
            return Response({'detail': 'Not your turn!'}, status=status.HTTP_403_FORBIDDEN)

        if position < 0 or position >= len(game.word.text):
            return Response({'detail': 'Invalid position.'}, status=status.HTTP_400_BAD_REQUEST)

            # بررسی اینکه آیا موقعیت قبلاً حدس زده شده (حرف جایگزین شده)
        if game.masked_word[position] != '_':
            return Response({'detail': 'This position has already been guessed correctly.'},
                            status=status.HTTP_400_BAD_REQUEST)

        word = game.word.text
        masked = list(game.masked_word)
        # اطمینان از اینکه masked دقیقا به اندازه طول کلمه است:
        if len(masked) < len(word):
            masked += ['_'] * (len(word) - len(masked))
        elif len(masked) > len(word):
            masked = masked[:len(word)]

        actual_letter = word[position]
        is_correct = (letter == actual_letter)

        # ثبت حدس در مدل Guess
        Guess.objects.create(game=game, player=user, letter=letter, is_correct=is_correct)

        if is_correct:
            masked[position] = letter
            game.masked_word = ''.join(masked)

            # افزایش امتیاز بازیکن به میزان +20
            if user == game.player1:
                game.player1_score += 20
            elif user == game.player2:
                game.player2_score += 20
        else:
            pos_key = str(position)
            wrong = game.wrong_guesses or {}
            wrong.setdefault(pos_key, [])
            if letter not in wrong[pos_key]:
                wrong[pos_key].append(letter)
            game.wrong_guesses = wrong
            # کاهش امتیاز بازیکن به میزان -10 (امکان منفی شدن امتیاز)
            if user == game.player1:
                game.player1_score -= 10
            elif user == game.player2:
                game.player2_score -= 10

        # بررسی پایان بازی
        if '_' not in game.masked_word:
            game.status = 'finished'
            # تعیین برنده
            if game.player1_score > game.player2_score:
                game.winner = game.player1
            elif game.player2_score > game.player1_score:
                game.winner = game.player2
            else:
                game.winner = None  # مساوی
        else:
            # نوبت بازیکن بعدی
            if user == game.player1:
                game.current_turn = game.player2
            else:
                game.current_turn = game.player1

        game.save()

        return Response({
            'is_correct': is_correct,
            'masked_word': game.masked_word,
            'score_player1': game.player1_score,
            'score_player2': game.player2_score,
            'next_turn': game.current_turn.username if game.current_turn else None,
            'game_status': game.status,
            'winner': game.winner.username if game.winner else None,
        }, status=status.HTTP_200_OK)
class GuessFullWordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        user = request.user
        guessed_word = request.data.get('word', '').strip().upper()

        if not guessed_word:
            return Response({'detail': 'You must provide a word.'}, status=status.HTTP_400_BAD_REQUEST)

        game = get_object_or_404(Game, id=game_id)

        if game.status != 'in_progress':
            return Response({'detail': 'Game is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        if game.current_turn != user:
            return Response({'detail': 'Not your turn!'}, status=status.HTTP_403_FORBIDDEN)

        actual_word = game.word.text.upper()

        # کسر 30 امتیاز برای استفاده از این قابلیت
        if user == game.player1:
            game.player1_score -= 30
        elif user == game.player2:
            game.player2_score -= 30

        if guessed_word == actual_word:
            # حدس درست - پایان بازی و +100 امتیاز
            if user == game.player1:
                game.player1_score += 100
            elif user == game.player2:
                game.player2_score += 100

            game.masked_word = actual_word
            game.status = 'finished'

            # تعیین برنده
            if game.player1_score > game.player2_score:
                game.winner = game.player1
            elif game.player2_score > game.player1_score:
                game.winner = game.player2
            else:
                game.winner = None  # مساوی
        else:
            # حدس اشتباه، فقط نوبت تغییر می‌کند
            if user == game.player1:
                game.current_turn = game.player2
            else:
                game.current_turn = game.player1

        game.save()

        return Response({
            'is_correct': guessed_word == actual_word,
            'masked_word': game.masked_word,
            'score_player1': game.player1_score,
            'score_player2': game.player2_score,
            'next_turn': game.current_turn.username if game.current_turn else None,
            'game_status': game.status,
            'winner': game.winner.username if game.winner else None,
        }, status=status.HTTP_200_OK)
