import os
import sys
import datetime
import time
import threading
import uuid
import sqlite3
import numpy as np

from locustvr.experiment import ExperimentBase

#change directories!!******************************************************************************
projectDB = '/home/loopbio/Documents/databases/locustProjects.db'
expDB = '/home/loopbio/Documents/databases/locustExperiments.db'
pathData = '/home/loopbio/Documents/data/'


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

        self.reset_origin()
        # assign experiment a unique id
        self.expId = uuid.uuid4()
        # get experiment conditions from database
        self.getExperiment()
        # start every experiment with a no post condition
        #self.updateStimuli(0)
        

    # the base class calls this with the current integrated position in the world. the default implementation
    # just calls move_world. However this keeps an origin and can reset it.
    def do_move_world(self, x, y, z):
        with self._olock:
            if self._origin is None:
                self._origin = x, y, z
            ox, oy, oz = self._origin

        # relative position
        self.move_world(x - ox, y - oy, z - oz)

    def reset_origin(self):
        self.log.info('reset origin')
        with self._olock:
            self._origin = None
    
    def getExperiment(self):
        pass
        
        # establish a connecttion to the project database
        conn = sqlite3.connect(projectDB)
        # connect a cursor that goes through the project database
        cursorProject = conn.cursor()
        # establish a second connecttion to the experiment database
        conn2 = sqlite3.connect(expDB)
        # connect a cursor that goes through the experiment database
        cursorExperiment = conn2.cursor()
        '''
        # pick a random experiment from specified project
        cursorProject.execute("Select exp from projects where project = ? ",(project,))
        fetched = cursorProject.fetchall()
        print('fetched : ' + str(fetched))
        
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
            print((project,self.expTrial,self.replicate,nStimuli))
            cursorProject.execute("Select post"+str(nPost)+" from projects where project = ? and exp = ? and replicate = ? and nStimuli =?",(project,self.expTrial,self.replicate,nStimuli))
            fetched = cursorProject.fetchall()

            data = fetched[0][0]
            #print(data)
            if data == 'None':
                #Should be the name of the blender file
                self.postPosition[nPost,:] = [1000,1000]
            else:
                dictData = eval(data)
                print(dictData['position'])
                self.postPosition[nPost,:] = dictData['position']
                self.postDistance = dictData['distance']
            self.ds_proxy.move_node('Cylinder' + str(nPost), self.postPosition[nPost,0],  self.postPosition[nPost,1], 0)
            #print(self.postPosition)
        
        # close connection
        conn.close()
    '''
    def run_forever(self):
        t0 = time.time()
        try:
            while 1:
                time.sleep(0.1)
                # send state to motif to record
                self.publish_state()

                t = time.time()
                if (t - t0) > 20:
                    #e.move_world(100, 12, 0)
                    #hier aendern!!!





                    t0 = t
                    self.reset_origin()

        except KeyboardInterrupt:
            self.stop()
      




      
if __name__ == '__main__':
    import logging
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--debug-display', action='store_true', default=False,
                        help='also run on the debug display server')
    args = parser.parse_args()

    e = MyExperiment.new_osg(debug=args.debug_display)
    e.start(record=True)
    #reset to zero?
    #if (t - t0) > 30:
       # pass
     #   t0 = t
      #  e.reset_origin()

    #e.move_world(30, 500, 0)

    e.run_forever()
   # if (t - t0) > 90:
    #    t0 = t
     #   e.reset_origin()


