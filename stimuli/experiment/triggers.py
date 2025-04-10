import logging
from itertools import product

from psychos.triggers import DelayTrigger, DummyPort, StepTrigger

# from psychos.triggers import ParallelPort, SerialPort # comment if using port = DummyPort(). Otherwise it raises an error

TRIGGER = None # Global variable for lazy initialization of the trigger

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_trigger():
    """Get the trigger object."""
    global TRIGGER # Avoid re-initializing the trigger if it already exists
    from experiment.constants import TRIGGERS_MAIN # Import here to avoid circular import issues
    if TRIGGER is None:
        # port = ParallelPort(address="0x378")
        # port = SerialPort(address="COM3", baudrate=115200)
        port = DummyPort()
        trigger = StepTrigger(port=port, mapping=TRIGGERS_MAIN) # StepTrigger does not introduce any delay in the experiment timings
        #trigger = DelayTrigger(port=port, mapping=TRIGGER_MAPPING, delay=0.01) 
        
        logger.info("Trigger initialized: %s", trigger)
        TRIGGER = trigger
    return TRIGGER

def send_trigger(trigger_type):
    trigger = get_trigger()
    trigger.send(trigger_type)
    logger.info("Trigger sent: %s", trigger_type)



# This function is called in constants.py
def generate_triggers(condition_dict):
    """
    Generate a dictionary of trigger definitions based on combinations of condition levels.

    Parameters:
        condition_dict (dict): A dictionary where keys are factor names (e.g., 'v_stimulus')
                               and values are lists of condition levels for that factor.

    Returns:
        triggers (dict): A dictionary with trial_type + event as strings as keys and trigger numbers as values.
    """
    # Extract all factor names and corresponding level lists
    factor_names = list(condition_dict.keys())
    level_lists = list(condition_dict.values())

    # Compute all combinations (Cartesian product)
    combinations = list(product(*level_lists))
    num_triggers = len(combinations)
    
    triggers = {}
    for i, levels in enumerate(combinations, start=1):
        # Create trial_type string
        trial_type = "_".join(str(level) for level in levels)
        
        # Define sub-dictionary with trigger structure
        triggers[f"{trial_type}_trial_start"] = i 
        triggers[f"{trial_type}_cue_onset"] = i + num_triggers
        triggers[f"{trial_type}_isi"] = i + 2 * num_triggers
        triggers[f"{trial_type}_target_onset"] = i + 3 * num_triggers
        triggers[f"{trial_type}_response"] = i + 4 * num_triggers

    return triggers