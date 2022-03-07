from enum import Enum
import sys


# PROGRAM FLOW
# 1 : File IO - Parse input to array
# 2 : Graph creation - Transform formatted array into adjacency lists
# 3 : Search alg - Use DFS/BFS to convert the maze to a tree
# 4 : Solution - Pull a maze solution from the tree


class Color(Enum):
	NONE = 0
	RED = 1
	BLUE = 2

	def __str__(self):
		return str(self.name)


class Direction(Enum):
	NONE = 0             # If none, node is the destination
	NORTH = 1
	NORTHEAST = 2
	EAST = 3
	SOUTHEAST = 4
	SOUTH = 5
	SOUTHWEST = 6
	WEST = 7
	NORTHWEST = 8

	def __str__(self):
		return str(self.name)


class Node:
	def __init__(self, id):
		self.id = id
		self.color = Color.NONE
		self.dir = Direction.NONE
		self.circled = False

	def __str__(self):
		return f"Node {self.id}: {self.dir}, {self.color}{' circled' if self.circled else ''}"


class Graph:
	def __init__(self, data):
		self.data = []      # Adjacency list (node is indexed ID - 1)
		self.tree = []      # Parent pointer array
		self.rows = 0
		self.cols = 0 
		self.numnodes = -1
		self.build(data)

	def __str__(self):
		ret = ""
		for i, adj in enumerate(self.data):
			lst = ""
			for e in adj: lst += f"{((e - 1) % self.numnodes) + 1}{f'b, ' if e > self.numnodes else 'a, '}"
			ret += f"{(i % self.numnodes) + 1}{'a' if i < self.numnodes else 'b'}: {lst[:-2]}\n"
		return ret

	def build(self, graph):
		self.rows = len(graph)
		self.cols = len(graph[0])
		self.numnodes = self.rows * self.cols

		# Build forward-facing nodes
		for row in graph:
			for node in row:
				if node.color == Color.NONE:
					self.exit = node.id
					self.data.append([])
					continue

				x = 0      # Offset to search X 
				y = 0      # Offset to search Y

				# 'Switch' for direction
				# Potential refactor: Store direction as N = [-1, 1], E = [-1, 1] instead of Enum type
				if node.dir == Direction.NORTH: y = -1
				elif node.dir == Direction.NORTHEAST: x, y = 1, -1
				elif node.dir == Direction.EAST: x = 1
				elif node.dir == Direction.SOUTHEAST: x, y = 1, 1
				elif node.dir == Direction.SOUTH: y = 1
				elif node.dir == Direction.SOUTHWEST: x, y = -1, 1
				elif node.dir == Direction.WEST: x = -1
				elif node.dir == Direction.NORTHWEST: x, y = -1, -1

				adj = []
				r = int((node.id - 1) / self.cols)
				c = node.id - (r * self.cols) - 1

				while not (x == 0 and y == 0):       # Loop until failure unless node is the target
					try:
						r += y
						c += x
						if r < 0 or c < 0: break

						other = graph[r][c]
						#print("OTHER:", other)

						if node.color != other.color: 
							adj.append(other.id + (self.numnodes if other.circled else 0))

					except IndexError:
						break

				self.data.append(adj)

		# Build backwards-facing nodes
		for row in graph:
			for node in row:
				if node.color == Color.NONE: 
					self.data.append([])
					continue

				x = 0      # Offset to search X 
				y = 0      # Offset to search Y

				# 'Switch' for direction
				# Potential refactor: Store direction as N = [-1, 1], E = [-1, 1] instead of Enum type
				if node.dir == Direction.NORTH: y = 1
				elif node.dir == Direction.NORTHEAST: x, y = -1, 1
				elif node.dir == Direction.EAST: x = -1
				elif node.dir == Direction.SOUTHEAST: x, y = -1, -1
				elif node.dir == Direction.SOUTH: y = -1
				elif node.dir == Direction.SOUTHWEST: x, y = 1, -1
				elif node.dir == Direction.WEST: x = 1
				elif node.dir == Direction.NORTHWEST: x, y = 1, 1

				adj = []
				r = int((node.id - 1) / self.cols)
				c = node.id - (r * self.cols) - 1

				while not (x == 0 and y == 0):       # Loop until failure unless node is the target
					try:
						r += y
						c += x
						if r < 0 or c < 0: break

						other = graph[r][c]
						#print("OTHER:", other)

						if node.color != other.color: 
							adj.append(other.id + (0 if (other.circled or other.color == Color.NONE) \
								else self.numnodes))

					except IndexError:
						break

				self.data.append(adj)

	def bfs(self, entry):    # Entry is int specifying node ID (converted to respective coords)
		self.tree = [None for i in range(self.numnodes * 2)]
		visited = [False for i in range(self.numnodes * 2)]
		queue = [entry - 1]

		while True:
			try:
				cur = queue.pop(0) 
				adj = self.data[cur]
				visited[cur] = True
			except IndexError: break

			for node in adj:
				index = node - 1
				if not visited[index]:
					queue.append(index)
					self.tree[index] = cur + 1    # Build the tree

	def solve(self):
		solution = [self.exit]
		node = self.tree[self.exit - 1]

		while node is not None:
			solution.append(node)
			node = self.tree[node - 1]

		if len(solution) == 1: return "No solution exists"
		solution.reverse()

		ret = ""
		for step in solution:
			step = (step - 1) % self.numnodes
			ret += f"({int(step / self.cols) + 1},{(step % self.rows) + 1}) "

		return ret


def parse(path):
	with open(path) as inf:
		raw = [line.split() for line in inf]

	rows = int(raw[0][0])
	cols = int(raw[0][1])

	# Empty table of data
	data = [[Node((x * rows) + y + 1) for y in range(cols)] for x in range(rows)]

	# Populate each node with its respective values
	for x in range(1, len(raw)):
		line = raw[x]
		node = data[int(line[0]) - 1][int(line[1]) - 1]

		color = line[2]
		circled = line[3]
		direction = line[4]

		# 'Switch' for node color
		if color == 'R': node.color = Color.RED
		elif color == 'B': node.color = Color.BLUE

		# 'Switch' for node direction
		if direction == "N": node.dir = Direction.NORTH
		elif direction == "NE":	node.dir = Direction.NORTHEAST
		elif direction == "E":	node.dir = Direction.EAST
		elif direction == "SE":	node.dir = Direction.SOUTHEAST
		elif direction == "S":	node.dir = Direction.SOUTH
		elif direction == "SW":	node.dir = Direction.SOUTHWEST
		elif direction == "W":	node.dir = Direction.WEST
		elif direction == "NW":	node.dir = Direction.NORTHWEST

		# Specify if node is circled
		if circled == 'C': node.circled = True

	return Graph(data)

if __name__ == "__main__":
	path =  (sys.argv[1] if len(sys.argv) > 1 else None)
	if path is None:
		print("Usage maze.py {infile}")
		exit(-1)

	maze = parse(path)
	# print(graph)
	maze.bfs(1)
	solution = maze.solve()

	print(solution)


