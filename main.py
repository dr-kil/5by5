## 5by5 - A Richard Kil joint - last updated: 160131
#########################
### Variables that are decided when playing the game:
#########################
max_players = 4		#max number of players
points_goal = 10 	#points threshold above which the game ends
num_blanks = 2  	#how many blanks in letter distribution. raise for more randomness
#########################
### Points per letter
letter_points = {'A':1,'B':3,'C':3,'D':2,'E':1,'F':4,'G':2,'H':4,'I':1,
				'J':8,'K':5,'L':5,'M':3,'N':1,'O':1,'P':3,'Q':10,'R':1,
				'S':1,'T':1,'U':1,'V':4,'W':4,'X':8,'Y':4,'Z':10}
### Distribution of letters (N.B. # of blanks above)
let_distr = {'A':9,'B':2,'C':2,'D':4,'E':12,'F':2,'G':3,'H':2,'I':9,
			'J':1,'K':1,'L':4,'M':2,'N':6,'O':8,'P':2,'Q':1,'R':6,
			'S':4,'T':6,'U':4,'V':2,'W':2,'X':1,'Y':2,'Z':1} 
# standard scrabble distribution: 
#	let_distr = {'A':9,'B':2,'C':2,'D':4,'E':12,'F':2,'G':3,'H':2,'I':9,
#	'J':1,'K':1,'L':4,'M':2,'N':6,'O':8,'P':2,'Q':1,'R':6,
#	'S':4,'T':6,'U':4,'V':2,'W':2,'X':1,'Y':2,'Z':1} 
len_val = {'3':0,'4':0,'5':2,'6':3,'7':5,'8':8,'9':12,'10':17,
			'11':23,'12':30,'13':38,'14':47,'15':57,'16':68,
			'17':70,'18':83,'19':97,'20':112,'21':999999999}
#########################
#########################
board = [["-"]*5 for x in range(5)]	#mod for wider board, but other things change with
player_list = []	#This gets populated during the prompts in player_assignment
player_hands = []	#populated automatically
player_scores = []
#########################
from random import randint
#########################
distr = ""
for key in let_distr:
    distr += key*let_distr[key]
#########################
def assign_players():
	while True:
	    try:
	        players = int(raw_input("How many players? (1-4) "))
	        if players in range(1,max_players+1):
	        	for x in range(1,players+1):
	        		player_list.append(str(raw_input("Name of player " + str(x) + "? ")).upper())
	        		player_hands.append([random_letter(num_blanks),random_letter(num_blanks)])
	        		player_scores.append(0)
	        	break
	        print "Only 1-" + str(max_players) + " players"
	    except ValueError:
	        print "Try a number from 1-" + str(max_players) + "."

def print_board(x):
	for row in board:
		print " ".join(row)

def opening_board():
	for x in range(5):
		for y in range(2,5):
			board[y][x] = random_letter(0)
	board[1][0] = random_letter(0)
	board[1][4] = random_letter(0)	

def random_letter(num_blanks):
	new_distr = distr + "*"*num_blanks
	let = randint(1,len(new_distr)-1)
	return new_distr[let]

def take_turn(whose_turn):
	while True:  
		turn_let = str(raw_input("Which tile? ")).upper()
		# forces the chosen letter to be in player hand
		if turn_let in player_hands[whose_turn]:
			player_hands[whose_turn].remove(turn_let)
			if turn_let == "*":
				turn_let = str(raw_input("What letter for the blank? ")).upper()

			# This loop determines if the column choice is valid.
			while True:
				try:
					col_choose = int(raw_input("Which column? "))
					if col_choose in range(1,6):
						break
					else:
						print "Try again..."
				except ValueError:
					print "Try again..."

			# finds the lowest empty space in the column and assigns it to turn_let
			for x in range(4,-1,-1):
				if board[x][col_choose-1] == "-":
					board[x][col_choose-1] = turn_let
					#########################
					path = [(x,col_choose-1)]
					#########################
					break
			print "\n"
			print_board(board)
	# This loop determines if the word is valid.
			while True:
				played_word = str(raw_input("What word? ")).upper()
				#laying out conditions for success
				if turn_let in played_word:
					# confirms if the word is the right length, and if all it's letters are on the board
					if len(played_word) >= 3 and len(played_word) <= 21:   ##THIS can be the number of letters on the board + 1, affected by the width of the board
						if all(x in(board[0]+board[1]+board[2]+board[3]+board[4]) for x in played_word):
	#########################
							if is_it_there(turn_let,played_word,path):
								player_scores[whose_turn] += word_score(played_word)  ##THIS SHOULD BE MOVED But Played_word is not global
	# The final check should be if the word is in the dictionary.
								break
	# Something should go here that returns the word once all the checks have been done
	# and the word is decided to be successful. This will then allow the word_score to be 
	# decided outside this loop.
							print "That word is not valid."
	#########################
						else:
							print "A letter is missing."
					else:
						print "Must be 3 letters or longer."
				else:
					print "Your tile is not in your word!"

			# gives the player a new letter
			player_hands[whose_turn].append(random_letter(num_blanks))
			break
		print turn_let + " was not in your hand!"

#########################
#########################
# This section is required for checking if the word is playable.
# If is_it_there returns True, the word is accepted.
#########################

def let_pos_in_played(turn_let,played_word):
	return [i for i, x in enumerate(played_word) if x == turn_let] 
	#FINDS THE VARIOUS POSITIONS OF THE LETTER PLAYED IN THE WORD - Returned as a list

def find_neighbours(x,y): #builds a list of the neighbours worth checking. 
	### N.B. This can be adjusted to reflect the size of the board
	neighbours = [(x-1,y-1),(x-1,y),(x-1,y+1),
					(x,y-1),		(x,y+1),
					(x+1,y-1),(x+1,y),(x+1,y+1)]
	for x in neighbours[::-1]:
		if x[0]<0 or x[0]>4 or x[1]<0 or x[1]>4: #reduces possible neighbours to those that fit on grid
			neighbours.remove(x)
	return neighbours
#########################
### Pathfinder takes in a path, the position of the letter, and the direction being explored
### and returns a list of all possible paths to the preceding letter
#########################
def pathfinder(path,x,sign,played_word): #x is the position of the letter in the word
	step_paths = []
	# since x is the position in the word, x - len(path) is the letter now being looked for
	# so it knows what letter to look for. This function is called in a loop over x, so no
	# iterating on x needs to be done inside the function.
	position = x + sign*len(path)
	if position == -1 or position == len(played_word):
		return [path]

	if sign<0:
		for coor in find_neighbours(path[0][0],path[0][1]):
			if played_word[position] == board[coor[0]][coor[1]]:
				#placing the coordinates where the letter was found in new_path
				new_path = [coor] + path
				step_paths.append(new_path)
	elif sign > 0:
		for coor in find_neighbours(path[len(path)-1][0],path[len(path)-1][1]):
			if played_word[position] == board[coor[0]][coor[1]]:
				new_path = path + [coor]
				step_paths.append(new_path)

	return step_paths

#########################
# Traces the letters preceding the turn letter
####
def front_half(turn_let,played_word,path):
	front_paths = []
	for x in let_pos_in_played(turn_let,played_word):  #This starts the path on the possible starting points within the word.
		step_1 = pathfinder(path,x,-1,played_word)
		try:
			# stops if the length of step_1 is the length of the word up to the position
			# so if x is 4, the fifth letter in the word, when a path hits five letters, 
			# this loop stops, and adds the path to front_paths
			while len(step_1[0]) < x+1:
				all_paths = []
				for y in step_1:
					all_paths += pathfinder(y,x,-1,played_word)				
				step_1 = all_paths
			else:
				front_paths += step_1
		except IndexError:
			pass
	for x in range(len(front_paths)-1,-1,-1):
		if len(front_paths[x]) != len(set(front_paths[x])):
			front_paths.remove(front_paths[x])
	if len(front_paths) == 0:
		return False
	else:
		return front_paths

#########################
# Traces the letters following the turn letter
####
def back_half(turn_let,played_word,path):
	back_paths = []
	for x in let_pos_in_played(turn_let,played_word):
		step_2 = pathfinder(path,x,1,played_word)
		try:
			# should stop if the length of step_1 is the length of the word after the position
			# so if x is 1, the second letter of the word, and the word is 5 letters long,
			# it should stop if the path is 4 steps long
			while len(step_2[0]) < len(played_word)-x:
				all_paths = []
				for y in step_2:
					all_paths += pathfinder(y,x,1,played_word)
				step_2 = all_paths
			else:
				back_paths += step_2
		except IndexError:
			pass
	for x in range(len(back_paths)-1,-1,-1):
		if len(back_paths[x]) != len(set(back_paths[x])):
			back_paths.remove(back_paths[x])
	if len(back_paths) == 0:
		return False
	else:
		return back_paths

#########################
# checks if both the front and back half are valid and checks to see if a path
# exists that gives the combined length of the word, and has no repeats
####
def is_it_there(turn_let,played_word,path):
	if front_half(turn_let,played_word,path) and back_half(turn_let,played_word,path):
		for x in front_half(turn_let,played_word,path):
			for y in back_half(turn_let,played_word,path):
				y.pop(0)
				if len(x + y) == len(played_word) and len(x+y) == len(set(x+y)):
	#					print "SUCCESS!!!"
					return True
		else:
			print "you reused a letter"
	else:
		return False

#########################
#########################
#########################

def row_flip():
	for x in range(5):
		if board[0][x] != "-":
			board[4] = board[3]
			board[3] = board[2]
			board[2] = board[1]
			board[1] = board[0]
			board[0] = ["-"]*5
			break

def word_score(played_word):
	word_score = 0
	for x in played_word:
		word_score += letter_points[x]
	word_score += len_val[str(len(played_word))]
	return word_score


#########################
#########################


#########################
### THIS IS WHERE THE GAME STARTS
#########################
assign_players()
print "Welcome", " & ".join(player_list)
print "The winner is the first to", str(points_goal), "points.\n\n"
opening_board()
print_board(board)

whose_turn = 0 # should loop between the number of players during the while loop
b = 0
#########################
### THE LOOP STARTS HERE
#########################
while True:
	if whose_turn == 0: # shows how many turns played, counts each time player 1 begins turn 
		b += 1
		print "\nROUND", b

	print player_list[whose_turn] + "s hand: " + " & ".join(player_hands[whose_turn])
	
	take_turn(whose_turn) #A LOT IS CONTAINED HERE.

	print player_list[whose_turn], "now has:", player_scores[whose_turn], "points."

	#if a player has passed the threshold, end the game immediately
	if player_scores[whose_turn] >= points_goal:
		break

	print player_list[whose_turn] + "s new hand: " + " & ".join(player_hands[whose_turn]) + ".\n\n"

	row_flip()
	print_board(board) # This may not need a variable passed into it.

	whose_turn += 1 # iterates through the turn order
	if whose_turn == len(player_list):
		whose_turn = 0
#########################
### When the loop ends
#########################
print "\n\nGame Over!! \n" + player_list[whose_turn], "reached", points_goal, "in", b, "turns."




