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
def distance(pos0, pos1, post):
    if post == True:
        dx = pos0['x'] - pos1[0]
        dy = pos0['y'] - pos1[1]
        #print ('x+y:',x,y)
        #print(pos0['x'], dx)
    else:
        dx = pos0['x'] - pos1['x']
        dy = pos0['y'] - pos1['y']
        #print ('x+y2:',x,y)

    return math.sqrt(dx**2 + dy**2)


class MyExperiment(ExperimentBase):

    def __init__(self, *args, **kwargs):
        ExperimentBase.__init__(self, *args, **kwargs)
        self._origin = None
        self._olock = threading.Lock()

        self.load_osg('/home/loopbio/Documents/stimuli/ten_post_stimulus.osgt')
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
        self.cntr = 0
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
        self.locPosition = {'x': x-ox, 'y': y-oy, 'z': z-oz }
        #print('self.locPositionx', self.locPosition['x'])
        #print('ox',ox, oy, oz)
        #print('x,y,z',x, y, z)
        
        #ox, oy, oz are constant throughout one experiment, set at reset_origin: self._origin wird mit x,y,z belegt,
        # dann werden ox, oy, oz mit self._origin belegt--> dann sollte locPosition wieder 0,0 sein.
        #*************x - ox is correct  position of the locust!!!*****************

    
    def running_writing_csv(self):
        global a
        global t0
        if a==0:
            #global a 
            a=1
            t0 = time.time()
        initialized=False
        reached=False
        write=True
        #sl_t0 = time.time()
        #lastMessage = True
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
                '''if t < 1.5:
                    #change to 3*60!!!
                    #control: no post at t< 3 min 
                    pass'''
                if t >= 0.45 and t < 0.45045:
                    #after 3 min *****WITHOUT STIMULUS**, locust is reset to origin (0,0) change to t >=3*60 and t < (3*60 + 0.5)!!!
                    #t >= 0.45 and t < 0.451 --> 
                    self.reset_origin()

                    #if self.cntr%1==0:
                    #    print('ORIGIN RESET , t=',t)
                        #print('LocPosition after reset:',self.locPosition['x'])
                
                if t>0.46 and self.locPosition['x'] == 0.0 and write==True:
                    print('LocPosition after reset:',self.locPosition['x'])
                    print('postPosition', self.postPosition[0,:])
                    write=False
                #****STIMULUS*****  
                if t >= 0.5:
                    if self.cntr%100==0:
                        pass
                        #print('LocPosition:',self.locPosition['x'], self.locPosition['y'], 'time=',t)
                        #change  to 3*60+0.5!!!
                    if initialized==False:
                        print('Stimulus has been updated')
                        self.updateStimuli(nStimuli)
                        initialized=True
                        #print('postPosition after update',self.postPosition[0,:])

                        


                    for nPost in range(0,10):
                        #dist is the variable that is the outcome of the function distance
                        # ':'means take all the values in that dimension which are x and y
                        dist = distance(self.locPosition, self.postPosition[nPost,:] ,  True)
                        if self.cntr%10000==0 and reached == False and dist<1000:
                            print('the distance to post %d is:' %(nPost),dist)
                            #distanz stimmt nicht. der post ist nicht 5 vom locust entfernt!!!
                        #bis hier alles gut dann self.origin fkt nicht*********************************************    
                        if dist < 4.8 and reached == False:
                            #change to dist < 0.5!!!
                            write=True
                            print('*******************************you reached the post***********************')
                            print('Locusts position', self.locPosition['x'],self.locPosition['y'])
                            #3 seconds no new stimulus, continously resetting org: (change to 3!!!)
                            reached=True

                            dt=t+0.5

                            '''while t<dt:
                                self.reset_origin()
                                print('wait for new stimulus')'''

                            #print('Locusts position after reset', self.locPosition['x'],self.locPosition['y'])
                            self.counter+=1
                            nStimuli = nStimuli+1
                            self.updateStimuli(nStimuli)
                            

                        if self.cntr%10000==0 and reached == True and dist<1000:
                            print('the distance to post %d is:' %(nPost),dist)
                            #distanz stimmt nicht. der post ist nicht 5 vom locust entfernt!!!
                         

                        #if self.cntr%10000==0:
                                #output.write('%.8f, %.8f, %.8f,  %d, %.8f, %s, %d\n' % (self.locPosition['x'],self.locPosition['y'],self.locPosition['z'], self.counter, t, str(nStimuli), dist))
                            # sleep time einbauen!!!
                        #while dist > 0.5:
                            #self.cntr+=1
                            #if self.cntr%100==0:
                                #output.write('%.8f, %.8f, %.8f,  %d, %.8f, %s\n' % (self.locPosition['x'], gy, gz, self.counter, t, str(nStimuli)))


                        #print('distance locust-post', dist)

                #if t> 0.8 and nStimuli < 4:
                    
                    


                self.cntr+=1
                #print pos in csv :
                #better would be: 1/200 sec
                #if b%0.2000==0:
                #funktioniert nicht. dann gibt er an bspw 0.2 s 10 werte aus, bei 0,4 s ebenfalls usw

                #ODER INCREMENT mit +1/200 und dann werte kleiner /groesser als
                #jeder 1000. macht etwa 100 werte pro sekunde

                if self.cntr%1000==0:
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

        # close all established connections
        conn.close()
        conn2.close()


    

    def updateStimuli(self,nStimuli):
        # establish a connecttion to the project database
        conn = sqlite3.connect(projectDB)
        # connect a cursor that goes through the project database
        cursorProject = conn.cursor()
        # pick a new stimulus from available permutations
        for nPost in range(0,10):
            #print((project,self.expTrial,self.replicate,nStimuli))
            cursorProject.execute("Select post"+str(nPost)+" from projects where project = ? and exp = ? and replicate = ? and nStimuli =?",(project,self.expTrial,self.replicate,nStimuli))
            fetched = cursorProject.fetchall()

            data = fetched[0][0]
            #print(fetched)
            #print('fetched in UPDATESTIMULI: ' + str(fetched))
            #data = fetched[0][0]
            #print(data)
            if data == 'None':
                #Should be the name of the blender file
                self.postPosition[nPost,:] = [1000,1000]
            else:
                dictData = eval(data)
                print('position from dictData',dictData['position'])
                self.postPosition[nPost,:] = dictData['position']
                self.postDistance = dictData['distance']
            #self.ds_proxy.move_node('Cylinder' + str(nPost), self.postPosition[nPost,0],  self.postPosition[nPost,1], 0)
            #print(self.postPosition)
        
        # close connection
        conn.close()


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
        
            

        
    
    
    def run_forever(self):
        #t0 = time.time()
        e.reset_origin()
        j=0
        
        try:
            while 1:
                time.sleep(0.1)
                # send state to motif to record (motif recording system homepage)
                self.publish_state()
                #print('koordinrunfor: ', e._origin, str(e._olock))

                t = time.time()
                

        except KeyboardInterrupt:
            self.stop()
      

    #def printing_coordinates(self):
    #    while 1:
    #        print('koord-in-def-printng: ',str(e._origin), e._origin)




      
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
    #e.experiment_start()
    #e.writeInDb()
    #uncomment write in Db so it writes!!!
    


    e.running_writing_csv()
    #print('koord: ',str(e._origin), e._origin)
    #e.printing_coordinates()
    

    #change to true for recording, atm too much rubbish recording!!!******************
    #e.getExperiment


    
    e.run_forever()
    
