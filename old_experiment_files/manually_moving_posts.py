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
        #self.getExperiment()
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
    
    '''def getExperiment(self):
        pass
        
        # establish a connecttion to the project database
        conn = sqlite3.connect(projectDB)
        # connect a cursor that goes through the project database
        cursorProject = conn.cursor()
        # establish a second connecttion to the experiment database
        conn2 = sqlite3.connect(expDB)
        # connect a cursor that goes through the experiment database
        cursorExperiment = conn2.cursor()'''
        

    '''
    
    '''
    def run_forever(self):
        t0 = time.time()
        j=0

        try:
            while 1:
                time.sleep(0.1)
                # send state to motif to record
                self.publish_state()
                t = time.time()
                for i in range(0,10):
                    #print('k=', k)
                    self.move_node('Cylinder' + str(i), 1000, 1000,  0)
                    #self.move_node('Cylinder2' , 2, 2,  0)
                    #self.move_node('Cylinder3' , 1.5, 1.5,  0)
                    #self.move_node('Cylinder4' , 0, 1,  0)
                    #self.move_node('Cylinder5' , -1.5, -1.5,  0)
                    self.move_node('Cylinder6' , 2*math.cos(time.time()), 2*math.sin(time.time()) ,50)
                    #self.move_node('Cylinder0' ,2+math.cos(time.time()-0.25)+ 2*math.cos(time.time()), math.cos(time.time()+0.25)+math.cos(time.time()),  50)
                    if j==0:
                        self.reset_origin()

                        print('reset or')
                        j=1
                    '''if (t - t0) < 4:
                        print('time=', t -t0)
                    elif (t - t0) < 7:
                        #self.move_node('Cylinder0' , 2, 2,  0)
                        e.reset_origin()
                        print('time=', t -t0)

                        print('t=10')
                        #keeps resetting the origin between t=4 and t<7. afterwards moving on

                    else:
                        self.move_node('Cylinder6' , -2, -2,  0)
                        #pass'''



  

                    #pass


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
    e.start(record=False)
    #change to true for recording, atm too much rubbish recording!******************
    #e.getExperiment
    #e.move_world(100, 12, 0)
    #  e.reset_origin()

    #funkt nicht: e.move_world(30, 500, 0), t0 etc auch nciht: vllt wg globale/lok variable

    e.run_forever()
   # if (t - t0) > 90:
    #    t0 = t
     #   e.reset_origin()



