Guess Word Game-Python Project
A Django RESTful backend for a two-player Guess Word game.
Players take turns guessing a single letter of a word (the word is chosen/seeded by an admin). Points are awarded or deducted based on correct/incorrect guesses. The backend exposes a REST API used by the frontend to create games, submit guesses, view game state, and read leaderboard information. Authentication is token-based.

***Table of contents***

*Project overview

*Key features

*Tech stack & architecture
***Project overview***

This service implements the backend logic for a simple turn-based word-guessing game:

An admin chooses a secret word (or the system selects a random word from a dictionary).

Two players join the same game session and take turns guessing a single letter.

The API responds whether the guess is correct, updates the masked word (e.g. _ a _ _ e), updates remaining attempts, and updates scores.

Game ends when the word is fully revealed (win) or when attempts are exhausted (loss).

Leaderboard stores wins/points for players.
Key features

Create / join game sessions

Admin-controlled word selection (or random word pool)

Turn-based single-letter guessing

Scoring for correct/incorrect guesses

Game state endpoint (masked word, guessed letters, remaining attempts, status)

Leaderboard & player stats

Token-based authentication for API endpoints

RESTful API built for easy frontend consumption
Tech stack & architecture

Language: Python

Framework: Django + Django REST Framework (DRF)

Database: SQLite (default for dev) 

Auth: Token-based authentication 

Migrations: Django migrations (built-in)

Testing: pytest / Django test framework (recommended)
