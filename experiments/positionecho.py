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

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    def on_exp_message(dat):
        print dat

    tdr = ThreadedDataReceiver((('127.0.0.1', 8889),),
                               callback=on_exp_message,
                               topic_filter=VRCompatPositionPublisher.EXPERIMENT_POSITION_NAME)
    tdr.start()

    while True:
        time.sleep(1)
