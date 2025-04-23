import logging
from itertools import product
import subprocess
import serial
import time

# from psychos.triggers import ParallelPort, SerialPort # comment if using port = DummyPort(). Otherwise it raises an error

PORT = None # # Global variable for lazy initialization of the EEG trigger port
TRIGGER_MAPPING = None # Global variable for lazy initialization of the trigger mapping
TRACKER = None # Global variable for the tracker instance

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def precise_delay_ms(duration_ms: float):
    """Wait for a precise number of milliseconds using time.perf_counter()."""
    start_time = time.perf_counter()
    end_time = start_time + duration_ms / 1000.0
    while time.perf_counter() < end_time:
        pass


class MockSerial:
    """Mock class for serial port to simulate EEG trigger sending."""
    def __init__(self, *args, **kwargs):
        self.is_open = True
        print("Using mock serial port.")

    def open(self):
        self.is_open = True
        print("Mock serial port opened.")

    def close(self):
        self.is_open = False
        print("Mock serial port closed.")

    def write(self, data):
        print(f"Mock write to EEG: {list(data)}")

    def flush(self):
        pass

# Try to detect serial port
def get_serial_port():
    """Detect the serial port for EEG trigger."""
    global PORT
    if PORT is None: # Avoid re-initializing the port if it already exists
        try:
            comport = subprocess.check_output('python C:\\PROGS\\detectbiosemiserial.py').strip().decode()
        except Exception as e:
            print(f"Failed to detect serial port: {e}")
            comport = None

        # Attempt to open the serial port
        try:
            port = serial.Serial(
                port=comport,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            if not port.is_open:
                port.open()
            logger.info("Trigger initialized: %s", port)

        except Exception as e:
            print(f"Using MockSerial due to error: {e}")
            port = MockSerial()
            logger.info("Trigger initialized: %s", port)

        PORT = port # Set the global port variable

    return PORT

def get_trigger_mapping():
    """Get the trigger mapping."""
    global TRIGGER_MAPPING # Avoid re-initializing the trigger if it already exists
    if TRIGGER_MAPPING is None:
        from experiment.constants import TRIGGER_MAPPING # Import here to avoid circular import issues
        TRIGGER_MAPPING = TRIGGER_MAPPING
    return TRIGGER_MAPPING

def get_tracker(tracker_instance):
    """Inject the global tracker instance (from main.py)."""
    global TRACKER
    TRACKER = tracker_instance


def send_trigger(trigger_type, context=None):
    """
    Send a trigger to the EEG system and EyeLink tracker.
    """
    port = get_serial_port() # Get the serial port 
    trigger_mapping = get_trigger_mapping() # Get the trigger mapping
    triggerval = trigger_mapping[trigger_type] # Get the trigger value from the mapping

    try:
        port.write(triggerval.to_bytes(1,'little'))
        context_info = f" | Context: {context}" if context else ""
        logger.info(f"Trigger sent: {trigger_type}, value: {triggerval}{context_info}")
    except Exception as e:
        print(f"Failed to send trigger {trigger_type}: {e}")
        logger.warning(f"Failed to send trigger {trigger_type}: {e}")

    TRACKER.send_message(trigger_type) # Send trigger to EyeLink tracker

    precise_delay_ms(16) # Wait for 16 ms to ensure the trigger is sent
    

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
    "recording_on": 250, # Trigger for starting the recording
    "recording_off": 251, # Trigger for stopping the recording
    }
    
    return triggers | localizer_triggers # Merge dictionaries 