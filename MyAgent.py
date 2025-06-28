from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0
        self._depthCount = 0
        self._count = 0
        self._lastBestMove = None

    def findMove(self, state):
        self._count += 1
        depth = 1
        while self.timeRemaining():
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1
            best = -float('inf')
            bestMove = None
            for a in self.moveOrder(state):
                if not self.timeRemaining():
                    break
                result, _ = state.result(a)
                v = self.value(result, depth - 1, -float('inf'), float('inf'))
                if v is None:
                    break
                if v > best:
                    best = v
                    bestMove = a
            if bestMove:
                self._lastBestMove = bestMove
                self.setMove(bestMove)
            elif self._lastBestMove:
                self.setMove(self._lastBestMove)
            depth += 1

    def value(self, state, depth, alpha, beta):
        self._nodeCount += 1
        self._childCount += 1
        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)
        self._parentCount += 1
        best = -float('inf')
        for a in self.moveOrder(state):
            if not self.timeRemaining():
                return None
            result, _ = state.result(a)
            v = self.value(result, depth - 1, alpha, beta)
            if v is None:
                return None
            best = max(best, v)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best

    def heuristic(self, state):
        board = [state.getTile(r, c) for r in range(4) for c in range(4)]
        values = [0 if v == 0 else 2 ** v for v in board]

        empty_tiles = values.count(0)
        empty_bonus = 300 * empty_tiles

        max_tile = max(values)
        max_index = values.index(max_tile)
        corner_bonus = 1500 * max_tile if max_index in [0, 3, 12, 15] else -800 * max_tile

        mono_score = 0
        for i in range(4):
            row = [values[4 * i + j] for j in range(4)]
            col = [values[i + 4 * j] for j in range(4)]
            for lst in [row, col]:
                increasing = all(lst[j] <= lst[j + 1] for j in range(3))
                decreasing = all(lst[j] >= lst[j + 1] for j in range(3))
                if increasing or decreasing:
                    mono_score += 500

        smoothness = 0
        for i in range(16):
            if board[i] == 0:
                continue
            for d in [1, 4]:
                neighbor = i + d
                if neighbor < 16 and (d == 1 and i % 4 != 3 or d == 4 and i < 12):
                    if board[neighbor] != 0:
                        smoothness -= abs((2 ** board[i]) - (2 ** board[neighbor]))

        return state.getScore() + empty_bonus + corner_bonus + mono_score + smoothness

    def moveOrder(self, state):
        actions = state.actions()
        preferred = ['UP', 'LEFT', 'RIGHT', 'DOWN']
        return sorted(actions, key=lambda x: preferred.index(x) if x in preferred else 99)

    def stats(self):
        print(f'Average depth: {self._depthCount/self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
