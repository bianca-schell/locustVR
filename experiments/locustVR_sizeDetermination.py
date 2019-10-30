import os
import sys
import datetime
import time
import threading
import uuid
import sqlite3
import numpy as np
import math

from locustvr.experiment import ExperimentBase


replication = 3

projectDB = '/home/loopbio/Documents/locustVR/databases/locustProjects.db'
expDB = '/home/loopbio/Documents/locustVR/databases/locustExperiments.db'
pathData = '/home/loopbio/Documents/locustVR/data/'


project = 'DecisionGeometry'
experimenter = 'BS'
a = 0
running = 1
numberPost = 10
t0 = time.time()
db_post_distance = 2

def pathDefine(path,ids, params=[]):
    path = path + str(ids)
    if not os.path.exists(path):
        os.makedirs(path)
    for param in params:
        path = path + '/' + str(param)
        if not os.path.exists(path):
            os.makedirs(path)
    #print(path)
    return path


#fct distance between locust position and post
def distance(pos0, pos1):
    
    dx = pos0['x'] - pos1[0]
    dy = pos0['y'] - pos1[1]
        #print ('x+y:',x,y)
        #print(pos0['x'], dx)
   
    return math.sqrt(dx**2 + dy**2)


class MyExperiment(ExperimentBase):

    def __init__(self, *args, **kwargs):
        ExperimentBase.__init__(self, *args, **kwargs)
        self._origin = None
        self._olock = threading.Lock()

        self.load_osg('/home/loopbio/Documents/locustVR/stimulus/ten_post_stimulus_diffsize4.osgt')

        self.expTrial = -1
        self.replicate = -1
        self.tSwitch = 0
        self.tExp = 0
        self.dateStart = ''
        
        # set starting position for stimuli
        self.rootPosition = np.zeros((1,2))
        self.postPosition = np.zeros((numberPost,2))


        self.reset_origin()
        # assign experiment a unique id
        self.expId = uuid.uuid4()
        # get experiment conditions from database
        self.getExperiment()
        # start every experiment with a no post condition
        #self.updateStimuli(0)
        
        # assign experiment a unique id
        self.expId = uuid.uuid4()
        # event counter (number of times locust position is reset)
        self.rand = 0
        self.counter=0
        self.running = True
        self.locPosition = {'x':0,'y':0,'z':0}
        #self.resetting= False


    # the base class calls this with the current integrated position in the world. the default implementation
    # just calls move_world. However this keeps an origin and can reset it.
    def do_move_world(self, x, y, z):
        #resetting to 0,0: 
        with self._olock:
            if self._origin is None:
                self._origin = x, y, z
            ox, oy, oz = self._origin

        # relative position
        self.move_world(x - ox, y - oy, z - oz)
        self.locPosition = {'x': -x+ox, 'y': -y+oy, 'z': -z+oz }
        #print('self.locPositionx', self.locPosition['x'])
        #print('ox',ox, oy, oz)
        #print('x,y,z',x, y, z)
        
        #ox, oy, oz are constant throughout one experiment, set at reset_origin: self._origin wird mit x,y,z belegt,
        # dann werden ox, oy, oz mit self._origin belegt--> dann sollte locPosition wieder 0,0 sein.
        #*************x - ox is correct  position of the locust!!!*****************

    
    def running_writing_csv(self):
        t0 = time.time()
        firstinitialized=False
        initialized=False
        reached=True
        write=True
        reset= False
        go=False
        #sl_t0 = time.time()
        #lastMessage = True
        stimfourisreached=True
        nStimuli = 0
        n=1
        path = pathDefine(pathData,self.expId)
        #print('saved in csv in:', path)
        #opn the csv file and then 'a' for appending the next line, instead of overwriting ('w')
        with open(path+'/results.csv', 'a') as output:
            #self.locPosition = {'x':0,'y':0,'z':0}
            #self.publish_state()
            #print('self state',self._state())
            #have 5 experiments:
            while nStimuli<=4:
                self.publish_state()
                #while 1 vielleicht aendern zu while self.start oder runforever oder variable xy=1, diese  
                # bei if nStimuli==4 dann auf 0 setzen!!!
                #time starts at t = t0=0
                t = time.time() - t0
                

                #first stimulus is no post condition from database as control. should last for 3 / 5 min.
                #once resetting bf stimulus
                if nStimuli==0 and firstinitialized==False:
                    self.reset_origin()
                    self.updateStimuli(nStimuli)
                    firstinitialized=True
                    print('nStimuli:', nStimuli)
                    print( ' no post condition, control')
                    write=True
                    #print('LocPosition after reset:',self.locPosition['x'])
                    #print('1 postPosition', self.postPosition[0,:])
                    print('************************************************************************')
                    print(' ')
                    #unveraenderliche variable t_exp
                     
                        
                if t>0.1:#*60:
                    #change to 5*60!!!
                    for nPost in range(0,4):
                        #dist is the variable that is the outcome of the function distance
                        # ':'means take all the values in that dimension which are x and y
                        dist = distance(self.locPosition, self.postPosition[nPost,:])
                      



                        if self.rand%100000==0 and reached == False and dist<800:
                            #print('dist to post', self.postDistance, dictData['distance'])
                            print('the distance to post %d is:' %(nPost),dist)
                            #print(self.postPosition[0,:])
                            
                            if self.rand%1000000==0:
                                print('min:', t/60)
                                print('locpos', self.locPosition['x'],self.locPosition['y'])

                            #print('position post  move world',self._osg())
                            pass
                            #for nPost in range(0,10):
                            #print('postpos', self.postPosition[nPost,:])



                        if reached==True:

                            #nStimuli = nStimuli+1
                            if nStimuli==0:
                                nStimuli +=1
                                t_exp=t
                                t_exp_trial=t
                            
                            #print('**********coordin*********',self._x, self._y ,self._ox ,self._oy )   



                            print('*******nStimuli:', nStimuli, 'trial:', self.counter)
                            self.updateStimuli(nStimuli)
                            self.reset_origin()

                            #no of times locust runs through same stimulus
                            
                            #here while as sleep time until reset has been successfully done:
                            while self.locPosition['x'] != 0.0 and self.locPosition['y']!=0:
                                pass
                                #print('wait for reset')


                            output.write('%.8f, %.8f, %.8f,  %d, %.8f, %s\n' % (self.locPosition['x'],self.locPosition['y'],self.locPosition['z'], self.counter, t, str(nStimuli)))
                            
                            #print('+++++++++++start von texp', t_exp, 't=',t)
                            print('t_exp=', t_exp-t)
                            print('*Locusts position after reset*', self.locPosition['x'],self.locPosition['y'])
                            #should be equal to old post pos:
                            print('*new post Position*', self.postPosition[0,:])
                            reached=False


                        #if t













                        '''if dist < 0.1 and reached == False:
                            #change to dist < 0.5!!! b4 4.85 change to t_exp +10*60
                            write=True
                            print('Locusts position at reaching', self.locPosition['x'],self.locPosition['y'])
                            print('*******************************stimulus',nStimuli,'trial:', self.counter,':you reached the post ***********************')
                            print('texp' , t-t_exp)
                            print('************************************************************************')
                            print(' ')
                            self.counter += 1
                            reached=True
                            t_exp_trial=t

                        #ending at dist/t expiry, locusts that dont do the job very well: for post 0!!!!!!!!!!!!!!!
                        if dist > 2.5 and dist < 900:
                            #distance locust can max. reach without reaching post
                            print('Locust has reached a distance of > 2.5')
                            print('************************************************************************')
                            print(' ')
                            self.counter += 1
                            reached=True
                            t_exp_trial=t

                        if t > t_exp_trial+(25*60):
                            #change t_exp_trial +5*60, time locust can spend to reach one post
                            print('Locusts position at reaching t_exp', self.locPosition['x'],self.locPosition['y'])
                            print('*******************************stimulus',nStimuli,'trial:',self.counter,': times up***********************')
                            print('time for trial has expired:',((t-t_exp_trial)), 'min',  't=',t)
                            print('************************************************************************')
                            print(' ')
                            self.counter += 1
                            t_exp_trial=t
                            reached=True



                        

                        if t> t_exp+50*60:
                            #change to 10*60,  each stimulus should be repeated after reaching for ten min
                            
                            print('Locusts position at reaching t_exp', self.locPosition['x'],self.locPosition['y'])
                            print('*******************************stimulus',nStimuli,'trial:',self.counter,': times up***********************')
                            print('time has reached t_exp of:',((t-t_exp)), 'min',  't=',t)
                            print('************************************************************************')
                            print(' ')
                            nStimuli = nStimuli+1
                            self.counter = 0
                            print('nStimulus',nStimuli, 'trial:',self.counter )
                            self.updateStimuli(nStimuli)
                            self.reset_origin()
                            while self.locPosition['x'] != 0.0 and self.locPosition['y']!=0:
                                pass
                            t_exp=t
                            t_exp_trial=t
                            print('texp' , t-t_exp)

                        #remove!!!!!next two lines / (for checking end of experiment, entering stim4 immed)

                        #self.updateStimuli(4)
                        #nStimuli=4   
                        #!!!!!
                        if nStimuli == 4:
                            #5 min of control at the end
                            if stimfourisreached == True:
                                t_beginning_of_stim4 = t
                                print('**********no post condition control**********')
                                stimfourisreached = False
                                #print('stim4 starts at t=',t_beginning_of_stim4)    
                            if t > (t_beginning_of_stim4 + 5):
                                #change to 5*60!!!
                                print('total experiment time',t)
                                print('Experiment completed')
                                #print( 't',t,'stim4 beginning', t_beginning_of_stim4)
                                sys.exit()'''





                self.rand+=1
                #print pos in csv :
                #better would be: 1/200 sec
                #if b%0.2000==0:
                #funktioniert nicht. dann gibt er an bspw 0.2 s 10 werte aus, bei 0,4 s ebenfalls usw

                #ODER INCREMENT mit +1/200 und dann werte kleiner /groesser als
                #jeder 1000. macht etwa 100 werte pro sekunde

                if self.rand%1000==0:
                    output.write('%.8f, %.8f, %.8f,  %d, %.8f, %s\n' % (self.locPosition['x'],self.locPosition['y'],self.locPosition['z'], self.counter, t, str(nStimuli)))
            

    def reset_origin(self):
        self.log.info('reset origin')
        with self._olock:
            self._origin = None

    
    def getExperiment(self):
                
        # establish a connecttion to the project database
        conn = sqlite3.connect(projectDB)
        # connect a cursor that goes through the project database
        cursorProject = conn.cursor()
        # establish a second connecttion to the experiment database
        conn2 = sqlite3.connect(expDB)
        # connect a cursor that goes through the experiment database
        cursorExperiment = conn2.cursor()
        
        # pick a random experiment from specified project
        cursorProject.execute("Select exp from projects where project = ? ",(project,))
        fetched = cursorProject.fetchall()
        #print('in get exp fetched:', fetched)
        print('fetched: ' + str(fetched))


        expType = np.unique(fetched)
        print('the type of experiment i have in stock are '+str(expType))
        self.expTrial = -1
        
        # if number of replicates is not met, run experiment
        for k in range(0,len(expType)):
            expTemp = int(expType[k])
            print((project,expTemp,))
            cursorExperiment.execute("Select * from experiments where project = ? and exp = ? ",(project,expTemp,))
            fetched2 = cursorExperiment.fetchall()
            print('We already have ' + str(len(fetched2)) + ' replicates')
            if len(fetched2) < replication:
                self.expTrial = expTemp
                break

        if self.expTrial > -1:
            cursorProject.execute("Select replicate from projects where project = ? and exp = ? ",(project,self.expTrial,))
            fetched = cursorProject.fetchall()
            repType = np.unique(fetched)
            print('plenty of replicates : ' + str(repType))
            repIdx = np.random.randint(len(repType), size=1)
            print(repType)
            self.replicate = int(repType[repIdx])
            print('so lets pick ' + str(self.replicate))
            cursorProject.execute("Select tSwitch from projects where project = ? and exp = ? and replicate = ?",(project,self.expTrial,self.replicate,))
            fetched = cursorProject.fetchall()
            print('fetched : ' + str(fetched))
            self.tSwitch = np.unique(fetched)
            cursorProject.execute("Select tExp from projects where project = ? and exp = ? and replicate = ?",(project,self.expTrial,self.replicate,))
            self.tExp = np.unique(cursorProject.fetchall())  
            self.dateStart = datetime.datetime.now()      
        else:
            tExp = 0


    

    def updateStimuli(self,nStimuli):
        # establish a connecttion to the project database
        #conn = sqlite3.connect(projectDB)
        # connect a cursor that goes through the project database
        #cursorProject = conn.cursor()
        # pick a new stimulus from available permutations
        for nPost in range(0,1):
            #print((project,self.expTrial,self.replicate,nStimuli))
            '''cursorProject.execute("Select post"+str(nPost)+" from projects where project = ? and exp = ? and replicate = ? and nStimuli =?",(project,self.expTrial,self.replicate,nStimuli))
            fetched = cursorProject.fetchall()

            data = fetched[0][0]
            #print(data)
            if data == 'None':
                #Should be the name of the blender file
                self.postPosition[nPost,:] = [1000,1000]
            else:
                dictData = eval(data)
                print('post position',dictData['position'])
                self.postPosition[nPost,:] = dictData['position']
                self.postDistance = dictData['distance']'''
            #self.move_node('Cylinder' + str(nPost), 1,1, 49.3)
            self.move_node('Cube' , 0,0, 0)#0.707,0.707, 25)
            self.move_node('Cylinder0' , 1,-1, 50)#0,1 , 25) #49,3
            self.move_node('Cylinder1' , 1,1,50)#0.707,0.707, 25)
            self.move_node('Cylinder2' , -1,-1,50)#1,0, 25) #49,3
            self.move_node('Cylinder3' ,   1000,-1000,0)
            #self.move_node('Cylinder4' ,   1000,1000,0) 
            #self.move_node('Cylinder5' ,   1,-1,0)
            #self.move_node('Cylinder6' , 1000,1000,0)
            #self.move_node('Cylinder7' , 1000,1000,0)
            #self.move_node('Cylinder8' , 1000,1000,0)
            #self.move_node('Cylinder9' , 1000,1000,0)
            #print('osg_model_pose')

            #print('*Position*', self.postPosition[0,:])
            self.postPosition[0,:]= [1,-1]
            self.postPosition[1,:]= [1,1]
            self.postPosition[2,:]= [-1,-1]
            self.postPosition[3,:]= [10000,-10000]

        
        '''self.move_node('Cylinder0' , 2,2,50.01)
        self.reset_origin()
        for i in range(1,10):
            self.move_node('Cylinder'+str(i) , 0,0,1000)'''






    def writeInDb(self):
        todayDate = self.dateStart.strftime('%Y-%m-%d')
        self.startTime = self.dateStart.strftime('%H:%M')
        self.endTime = datetime.datetime.now().strftime('%H:%M')
        # establish a connection to the experiment database
        conn2 = sqlite3.connect(expDB)
        # connect a cursor that goes through the experiment database
        cursorExperiment = conn2.cursor()

        expId = 0
        values = [project,self.expTrial,self.replicate,
                      todayDate,self.startTime,self.endTime,
                      experimenter,str(self.expId)]
        cursorExperiment.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?,?)",values)
        
        # commit and close connection
        conn2.commit()
        conn2.close()
        
            


      
if __name__ == '__main__':
    import logging
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--debug-display', action='store_true', default=False,
                        help='also run on the debug display server')
    args = parser.parse_args()

    e = MyExperiment.new_osg(debug=args.debug_display)
    e.start(record=False)
    #e.writeInDb()
    #uncomment write in Db so it writes!!! record=True so it records!!!
    


    e.running_writing_csv()
   
    
