import sqlite3
import itertools
import numpy as np
from random import shuffle

projectDB = 'locustProjects_bias.db'
expDB = 'locustExperiments_bias.db'

project = 'DecisionBias'

nPosts = 3

posts = range(2,3)
posts = list(itertools.chain.from_iterable(itertools.repeat(x, 10) for x in posts))
distances = [3.0]	#in meter
start_ang_split = 16
angles2 = [np.pi/4, np.pi/3, np.pi]
angles3 = [4.5*np.pi/18, 3*np.pi/18, 2*np.pi/3]


# creates empty database
def FirstGen():
	# establish a connection to the project database
	conn = sqlite3.connect(projectDB)
	# connect a cursor that goes through the project database
	cursorProject = conn.cursor()
	# create a table with specified column names and datatypes
	cursorProject.execute('''CREATE TABLE projects (project text, exp integer,
										replicate integer,
										tExp int,tSwitch integer, 
										nSwitch integer,
										nStimuli integer, 
										post0 text,post1 text, 
										post2 text)''')
	# commit and close connection
	conn.commit()
	conn.close()
	
	# establish a connection to the experiment database
	conn = sqlite3.connect(expDB)
	# connectr a cursor that goes through the experiment database
	cursorExperiment = conn.cursor()
	# create a table with specified column names and datatypes
	cursorExperiment.execute('''CREATE TABLE experiments (project text, exp integer,
										replicate integer,
										date text, tStart text, tEnd text, 
										nameExperimenter text,expId text)''')
	# commit and close connection
	conn.commit()
	conn.close()

# creates a single post fixation control
def dataController():
	data=[]
	for j in range(0,nPosts):
		if j == 0:
			r = distances[0]
			theta = 2*np.pi*(np.random.randint(6)+1) / 6
			x = r*np.cos(theta)
			y = r*np.sin(theta)
			dataStimuli = {'position' : (x,y), 'distance' : r, 'angle' : theta}
		else:
			dataStimuli = 'None'
		data.append(str(dataStimuli))
	return data 


# define stimuli based on experimental condition
# the expType parameter defines which parameter is randomised for a given fly
# the other parameter is randomised between flies
def defineStimuli(expType, nSwitch, nReplicates=2, N=2, d=1.0, ang=np.pi/6, picked=[]):
	dataReplicates = []
	dataControl = dataController()


	data = []
	# define stimuli nSwitch-2 times since we have two control stimuli - one in the beginning; other in the end
	for k in range(0,nSwitch-2):
		data.append([])
		# pick a random start angle (one of six angles obtained by splitting angle of symmetry for N posts in six parts)
		start_ang = 2*np.pi*(np.random.randint(start_ang_split)+1) / start_ang_split
		# pick a random angle that will be the angle between successive posts
		ang = -1.0
		while ang in picked or ang < 0.0:
			ang = np.random.randint(3)
		picked.append(ang)
		# randomise left-right post (so the grey post may appear on either side of the black post)
		left = np.random.randint(2)

		for j in range(0,nPosts):
			if j < N:
				r = d
				angle = angles2[ang] if N == 2 else angles3[ang]
				theta = start_ang + j*angle if left == 0 else start_ang - j*angle
				x = r*np.cos(theta)
				y = r*np.sin(theta)
				dataStimuli = {'position' : (x,y), 'distance' : r, 'angle' : angle}
			else:
				dataStimuli = 'None'
			data[-1].append(str(dataStimuli))
	
	# permute replicates before adding them to the database
	# sandwich permutations between controls
	for k in range(0,nReplicates):
		dataReplicates.append([])
		dataReplicates[-1].append(dataControl)
		print(data)
		shuffle(data)
		for dataStimilus  in data:
			dataReplicates[-1].append(dataStimilus)
		dataReplicates[-1].append(dataControl)
	
	return dataReplicates


# write defined stimuli to database
def writeStimuli(cursor,projects,exp,nReplicate,tExp,tSwitch,nSwitch,data):

	for perm in range(0, nReplicate):
		for k in range(0, nSwitch):
			values = [projects, exp, perm, tExp, tSwitch, nSwitch, k, str(data[perm][k][0]), str(data[perm][k][1]), str(data[perm][k][2])]
			cursor.execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?)",values)


# fill database created by FirstGen
def main():
	# open the database
	conn = sqlite3.connect(projectDB)
	cursorProject = conn.cursor()

	# check the number of experiments in the project
	cursorProject.execute("Select exp from projects where project = ? ",(project,))
	fetched = cursorProject.fetchall()
	expType = np.unique(fetched)
	print(expType)
	print(len(expType))

	if len(expType) == 0:
		exp = -1
	else:
		exp = int(np.amax(expType))


	# define expType based on what variable needs randomisation within individual i.e. your experimental parameter
	expType = 'angles'
	tSwitch = 3
	nSwitch = 5
	tExp = tSwitch*nSwitch   
	nReplicates = 5

	N = 2
	d = 1.0
	ang = np.pi/6

	
	for N in posts:
		for d in distances:
			picked_angs = []
			# write your new stimuli
			exp += 1
			data = defineStimuli(expType, nSwitch, nReplicates, N=N, d=d, ang=ang, picked=picked_angs)
			writeStimuli(cursorProject, project, exp, nReplicate = nReplicates, tExp = tExp, tSwitch = tSwitch, nSwitch = nSwitch, data=data)


	# commit and close connection
	conn.commit()
	conn.close()

if __name__ == '__main__':
	main()