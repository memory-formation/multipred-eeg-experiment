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
    from experiment.constants import TRIGGER_MAPPING # Import here to avoid circular import issues
    if TRIGGER is None:
        # port = ParallelPort(address="0x378")
        # port = SerialPort(address="COM3", baudrate=115200)
        port = DummyPort()
        trigger = StepTrigger(port=port, mapping=TRIGGER_MAPPING) # StepTrigger does not introduce any delay in the experiment timings
        #trigger = DelayTrigger(port=port, mapping=TRIGGER_MAPPING, delay=0.01) 
        
        logger.info("Trigger initialized: %s", trigger)
        TRIGGER = trigger
    return TRIGGER


def send_trigger(trigger_type, context=None):
    trigger = get_trigger()
    trigger.send(trigger_type)

    context_info = f" | Context: {context}" if context else ""
    logger.info(f"Trigger sent: {trigger_type}{context_info}")



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
    # ===== TRIGGERS FOR LERNING AND TEST PHASES =====
    # Extract all factor names and corresponding level lists
    level_lists = list(condition_dict.values())

    # Compute all combinations (Cartesian product)
    combinations = list(product(*level_lists))
    num_triggers = len(combinations)
    
    triggers = {}
    for i, levels in enumerate(combinations, start=1):
        trial_type = "_".join(str(level) for level in levels)
    
        # Define sub-dictionary with trigger structure
        triggers[f"{trial_type}_trial_start"] = i 
        triggers[f"{trial_type}_cue_onset"] = i + num_triggers
        triggers[f"{trial_type}_isi"] = i + 2 * num_triggers
        triggers[f"{trial_type}_target_onset"] = i + 3 * num_triggers
        triggers[f"{trial_type}_response"] = i + 4 * num_triggers

    # ===== TRIGGERS FOR EXPLICIT PHASE =====
    # visual block conditions
    visual_explicit_conditions = {
        "v_stimulus": ["45", "135"],
        "v_pred_cond": ["EXP", "UEX"],
        }
    # auditory block conditions
    auditory_explicit_conditions = {
        "a_stimulus": ["100", "160"],
        "a_pred_cond": ["EXP", "UEX"],
        }
    
    # Adding visual explicit triggers
    # Extract all factor names and corresponding level lists
    visual_level_lists = list(visual_explicit_conditions.values())
    # Compute all combinations (Cartesian product)  
    visual_combinations = list(product(*visual_level_lists))
    visual_num_triggers = len(visual_combinations)

    for i, levels in enumerate(visual_combinations, start= max(triggers.values()) + 1): 
        trial_type = "_".join(str(level) for level in levels)
    
        # Define sub-dictionary with trigger structure
        triggers[f"explicit_{trial_type}_trial_start"] = i 
        triggers[f"explicit_{trial_type}_cue_onset"] = i + visual_num_triggers
        triggers[f"explicit_{trial_type}_isi"] = i + 2 * visual_num_triggers
        triggers[f"explicit_{trial_type}_target_onset"] = i + 3 * visual_num_triggers
        triggers[f"explicit_{trial_type}_response"] = i + 4 * visual_num_triggers
        triggers[f"explicit_{trial_type}_confidence"] = i + 5 * visual_num_triggers


    # Adding auditory explicit triggers
    # Extract all factor names and corresponding level lists
    auditory_level_lists = list(auditory_explicit_conditions.values())
    # Compute all combinations (Cartesian product)  
    auditory_combinations = list(product(*auditory_level_lists))
    auditory_num_triggers = len(auditory_combinations)

    for i, levels in enumerate(auditory_combinations, start= max(triggers.values()) + 1):
        trial_type = "_".join(str(level) for level in levels)

        # Define sub-dictionary with trigger structure
        triggers[f"explicit_{trial_type}_trial_start"] = i
        triggers[f"explicit_{trial_type}_cue_onset"] = i + auditory_num_triggers
        triggers[f"explicit_{trial_type}_isi"] = i + 2 * auditory_num_triggers
        triggers[f"explicit_{trial_type}_target_onset"] = i + 3 * auditory_num_triggers
        triggers[f"explicit_{trial_type}_response"] = i + 4 * auditory_num_triggers
        triggers[f"explicit_{trial_type}_confidence"] = i + 5 * auditory_num_triggers
    

    # ===== TRIGGERS FOR LOCALIZER PHASE =====
    highest_trigger = max(triggers.values()) # Get the highest trigger number
    localizer_triggers = {
    "loc_trial_start": highest_trigger + 1, 
    "loc_isi": highest_trigger + 2,
    "loc_45_100": highest_trigger + 3,
    "loc_45_160": highest_trigger + 4,
    "loc_135_100": highest_trigger + 5,
    "loc_135_160": highest_trigger + 6,
    "loc_response": highest_trigger + 7,
    }
    
    return triggers | localizer_triggers # Merge dictionaries 