from Game2048 import *

class Player(BasePlayer):
	def __init__(self, timeLimit):
		BasePlayer.__init__(self, timeLimit)

		self._nodeCount = 0
		self._parentCount = 0
		self._childCount = 0
		self._depthCount = 0
		self._count = 0

	def findMove(self, state):
		self._count += 1
		actions = self.moveOrder(state)
		depth = 1
		while self.timeRemaining():
			self._depthCount += 1
			self._parentCount += 1
			self._nodeCount += 1
			print('Search depth', depth)
			
			best = -1000
			for a in actions:
				if not self.timeRemaining(): return
				result, score = state.result(a)
				v = self.value(result, depth-1)
				if v is None: return
				if v > best:
					best = v
					bestMove = a
					
			self.setMove(bestMove)
			print('\tBest value', best, bestMove)

			depth += 1
			
	def value(self, state, depth):
		self._nodeCount += 1
		self._childCount += 1

		if state.gameOver():
			return state.getScore()
			
		actions = self.moveOrder(state)

		if depth == 0:
			return self.heuristic(state)

		self._parentCount += 1
		
		best = -10000
		for a in actions:
			if not self.timeRemaining(): return None
			result, score = state.result(a)
			v = self.value(result, depth-1)
			if v is None: return None
			if v > best:
				best = v

		return best

	def heuristic(self, state):
		board = state._board
		size = 4  
		values = [0 if x == 0 else 2**x for x in board]
		max_tile = max(values)
		max_index = values.index(max_tile)
		corner_bonus = 0
		if max_index == 12:
			corner_bonus = max_tile * 2
		monotonicity_vert = 0
		for r in range(size - 1, 0, -1):
			curr = values[r * size]
			prev = values[(r - 1) * size]
			if curr >= prev:
				monotonicity_vert += prev - curr
		monotonicity_horz = 0
		base_row = size - 1
		for c in range(size - 1):
			curr = values[base_row * size + c]
			nxt = values[base_row * size + c + 1]
			if curr <= nxt:
				monotonicity_horz += curr - nxt
		empty = values.count(0)
		empty_weight = 2.7
		empty_score = empty * empty_weight
		score = empty_score + corner_bonus - (monotonicity_vert + monotonicity_horz)

		return score


		
	def moveOrder(self, state):
		return state.actions()

	def stats(self):
		print(f'Average depth: {self._depthCount/self._count:.2f}')
		print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
