import time
import math
import threading
import logging

import zmq

from motifapi import MotifApi
from motifapi.stream import StateMirror

from freemoovr.proxy.stimulus_osg import StimulusOSGController
from locustvr.communication.transmission import ThreadedDataReceiver
from locustvr.communication.vrcompat import VRCompatPositionPublisher
from locustvr.experiment.motif_io import SensorSender

class Experiment(object):

    PORT = 8888
    TRACKING_CAMERA_SN = 18475394

    def __init__(self, osg_controller):
        self.log = logging.getLogger('experiment.%s' % self.__class__.__name__)

        self._osg = osg_controller

        self._tdr = ThreadedDataReceiver((('127.0.0.1', 8889),),
                                         callback=self._on_exp_message,
                                         topic_filter=VRCompatPositionPublisher.EXPERIMENT_POSITION_NAME)
        self._lock = threading.Lock()

        self._motif = MotifApi()

        self.log.info('started')
        self.log.info('connected to motif version: %s' % self._motif.call('version')['software'])

        # mirror the tracking camera so we have framenumber
        stream = self._motif.get_stream(serial=str(self.TRACKING_CAMERA_SN),
                                        stream_type=MotifApi.STREAM_TYPE_STATE)
        if stream is None:
            raise ValueError('could not connect to camera')

        self.camera_state_mirror = StateMirror(stream)
        self.camera_state_mirror.start()

        # send the world state over zmq back to motif
        self._zctx = zmq.Context()
        self._motif_io_sensors = SensorSender(self._zctx)
        self._sensors = {}

        # the current state of the experiment, tracking, everything. a row in a csv
        self._state = {}

    @classmethod
    def new_osg(cls, debug=False):
        servers = ['locustvr-01', 'locustvr-02', 'locustvr-03']
        if debug:
            servers.append('locustvr-dev')
        osg = StimulusOSGController(servers, port=cls.PORT)
        return cls(osg)

    def start_recording(self):
        self.log.info('starting motif recording')
        self._motif.call('recording/start')

    def do_start_recording(self):
        self.start_recording()

    def do_stop_recording(self):
        self.log.info('stopping motif recording')
        self._motif.call('recording/stop')

    def start(self, record):
        if record:
            self.do_start_recording()
        self._tdr.start()

    def stop(self):
        self.do_stop_recording()

    def update_state(self, **kwargs):
        with self._lock:
            self._state.update(self.camera_state_mirror.get_state(**kwargs))

    def get_world_position(self, raw_x, raw_y, raw_z):
        self.update_state(raw_x=raw_x, raw_y=raw_y, raw_z=raw_z)
        # per default we keep the world at z because the locust can only walk in x and y
        return raw_x, raw_y, 0

    def move_world(self, x, y, z):
        self.update_state(world_x=x, world_y=y, world_z=z)
        self._osg.move_world(x, y, z)

    def do_move_world(self, x, y, z):
        self.move_world(x, y, 0)

    def publish_state(self):
        with self._lock:
            s = dict(self._state)
        self._motif_io_sensors.send(s)

    def _on_exp_message(self, data):
        try:
            p = data.pop('world')
            self.do_move_world(*self.get_world_position(p['position']['x'], p['position']['y'], p['position']['z']))
        except KeyError:
            pass

    def __getattr__(self, name):
        return getattr(self._osg, name)

    

def main_show_osg():

    import os.path
    import argparse
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--debug-display', action='store_true', default=False,
                        help='also run on the debug display server')
    parser.add_argument('--osg-file', help='path to osgt file to show', required=True)
    parser.add_argument('--record', action='store_true', help='also start recording movies', default=False)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    path = os.path.abspath(os.path.expanduser(args.osg_file))

    if not os.path.exists(path):
        raise parser.error('could not find osg file')

    e = Experiment.new_osg(debug=args.debug_display)
    e.start(False)

    e.load_osg(path)

    while 1:
        time.sleep(0.1)
        e.publish_state()



