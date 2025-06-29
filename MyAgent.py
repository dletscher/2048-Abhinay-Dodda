from Game2048 import *
import math
import random


##MyAgent

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self._lastBestMove = None

    def findMove(self, state):
        free_tiles = state._board.count(0)
        depth = 4 if free_tiles > 5 else 3
        best_score = -float('inf')
        best_move = None

        for move in self.moveOrder(state):
            if not self.timeRemaining():
                break
            next_state = state.move(move)
            if next_state._board == state._board:
                continue
            val = self.expectimax(next_state, depth - 1, isPlayer=False)
            if val is None:
                break
            if val > best_score:
                best_score = val
                best_move = move

        if best_move:
            self.setMove(best_move)
            self._lastBestMove = best_move
        elif self._lastBestMove:
            self.setMove(self._lastBestMove)

    def expectimax(self, state, depth, isPlayer):
        if not self.timeRemaining():
            return None
        if state.gameOver() or depth == 0:
            return self.heuristic(state)

        if isPlayer:
            best = -float('inf')
            for move in state.actions():
                next_state = state.move(move)
                if next_state._board == state._board:
                    continue
                val = self.expectimax(next_state, depth - 1, False)
                if val is None:
                    return None
                best = max(best, val)
            return best
        else:
            expected = 0
            zeros = [i for i, v in enumerate(state._board) if v == 0]
            if not zeros:
                return self.heuristic(state)
            for idx in zeros:
                for val, prob in [(1, 0.9), (2, 0.1)]:
                    new_board = state._board[:]
                    new_board[idx] = val
                    new_state = Game2048(new_board, state._score)
                    res = self.expectimax(new_state, depth - 1, True)
                    if res is None:
                        return None
                    expected += (prob * res) / len(zeros)
            return expected

    def heuristic(self, state):
        board = state._board
        score = state.getScore()
        empty = board.count(0)
        empty_bonus = 500 * empty
        max_tile = max(board)
        corner_bonus = 2500 if any(board[i] == max_tile for i in [0, 3, 12, 15]) else -1000
        snake = [0, 1, 2, 3, 7, 6, 5, 4,
                 8, 9, 10, 11, 15, 14, 13, 12]
        snake_score = sum(board[i] * (16 - idx) for idx, i in enumerate(snake))
        mono_score = 0
        for i in range(4):
            row = board[4*i:4*i+4]
            col = board[i::4]
            if self.monotonic(row): mono_score += 1200
            if self.monotonic(col): mono_score += 1200
        smoothness = 0
        for i in range(4):
            for j in range(3):
                a = board[i*4 + j]
                b = board[i*4 + j + 1]
                if a and b:
                    smoothness -= abs(math.log2(a) - math.log2(b))
                a = board[j*4 + i]
                b = board[(j+1)*4 + i]
                if a and b:
                    smoothness -= abs(math.log2(a) - math.log2(b))
        smoothness *= 50
        merges = self.mergePotential(board) * 400

        return score + empty_bonus + corner_bonus + snake_score + mono_score + smoothness + merges

    def mergePotential(self, board):
        count = 0
        for i in range(4):
            for j in range(3):
                if board[i*4 + j] and board[i*4 + j] == board[i*4 + j + 1]:
                    count += 1
                if board[j*4 + i] and board[j*4 + i] == board[(j+1)*4 + i]:
                    count += 1
        return count

    def monotonic(self, line):
        return all(x <= y for x, y in zip(line, line[1:])) or all(x >= y for x, y in zip(line, line[1:]))

    def moveOrder(self, state):
        actions = list(state.actions())
        preferred = ['L', 'D', 'U', 'R']
        random.shuffle(actions)
        return sorted(actions, key=lambda m: preferred.index(m) if m in preferred else 99)

    def stats(self):
        print("Heuristic agent running. No depth tracking implemented.")
