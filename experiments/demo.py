import time
import threading
import uuid

from locustvr.experiment import ExperimentBase

class MyExperiment(ExperimentBase):

    def __init__(self, *args, **kwargs):
        ExperimentBase.__init__(self, *args, **kwargs)
        self._origin = None
        self._olock = threading.Lock()
        self.load_osg('/home/loopbio/Documents/stimuli/demo_world_v3.osgt') #VR_Arena_Locusts.osgt
        self.move_node('Cylinder' , 0, 0,  0)#5

        self.expId = uuid.uuid4()
        uID =str(self.expId)
        print('here UID!!!!!',self.expId, uID)


        now = time.ctime(int(time.time()))
        self._motif.call('recording/start', filename= uID , metadata={}) #uID_Name+




        #self.load_osg('/home/loopbio/Documents/stimuli/')
        #debug_world.osgt       demo_world_v2.osgt   debug_world_2.osgt         +++++ demo_world_v3.osgt   3posts_20cm_radius_z_at_50.osgt
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

    def run_forever(self):
        t0 = time.time()
        try:
            while 1:
                time.sleep(0.1)
                # send state to motif to record
                self.publish_state()

                t = time.time()
                if (t - t0) > 30:
                    t0 = t
                    #self.reset_origin()

        except KeyboardInterrupt:
            self.stop()
            
if __name__ == '__main__':
    import logging
    import argparse
    #self._motif.call()
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--debug-display', action='store_true', default=False,
                        help='also run on the debug display server')
    args = parser.parse_args()

    e = MyExperiment.new_osg(debug=args.debug_display)
    e.start(record=False)
    e.run_forever()


