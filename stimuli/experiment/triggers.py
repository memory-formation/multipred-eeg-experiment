import logging

from psychos.triggers import StepTrigger, DummyPort
# from psychos.triggers import ParallelPort, SerialPort

TRIGGER = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TRIGGER_MAPPING = {
    "stimulus": 1,
    "stimulus_on": 1,
    "stimulus_off": 2,
    "reset": 0,
}

def get_trigger():
    """Get the trigger object."""
    global TRIGGER
    if TRIGGER is None:
        # port = ParallelPort(address="0x378")
        # port = SerialPort(address="COM3", baudrate=115200)
        port = DummyPort()
        trigger = StepTrigger(port=port, mapping=TRIGGER_MAPPING)
        
        logger.info("Trigger initialized: %s", trigger)
        TRIGGER = trigger
    return TRIGGER

def send_trigger(trigger_type):
    trigger = get_trigger()
    trigger.send(trigger_type)
    logger.info("Trigger sent: %s", trigger_type)