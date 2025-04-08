import logging

from experiment.constants import TRIGGER_MAPPING
from psychos.triggers import DummyPort, StepTrigger, DelayTrigger
# from psychos.triggers import ParallelPort, SerialPort # comment if using port = DummyPort(). Otherwise it raises an error

TRIGGER = None # Global variable for lazy initialization of the trigger

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_trigger():
    """Get the trigger object."""
    global TRIGGER # Avoid re-initializing the trigger if it already exists
    if TRIGGER is None:
        # port = ParallelPort(address="0x378")
        # port = SerialPort(address="COM3", baudrate=115200)
        port = DummyPort()
        trigger = StepTrigger(port=port, mapping=TRIGGER_MAPPING) # StepTrigger does not introduce any delay in the experiment timings
        #trigger = DelayTrigger(port=port, mapping=TRIGGER_MAPPING, delay=0.01) 
        
        logger.info("Trigger initialized: %s", trigger)
        TRIGGER = trigger
    return TRIGGER

def send_trigger(trigger_type):
    trigger = get_trigger()
    trigger.send(trigger_type)
    logger.info("Trigger sent: %s", trigger_type)