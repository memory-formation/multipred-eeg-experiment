import datetime
import json
from pathlib import Path
import random



from psychos import Window
from psychos.gui import Dialog

from .constants import BACKGROUND_COLOR, DATA_FOLDER, PHASES

def generate_trials(seed=None):
    """
    Generates a list of trials for a multisensory experiment with non-uniform transitional probabilities.
    
    In the visual modality, there are two EXPictive stimuli (vertical, horizontal) and one neutral stimulus (neutralV).
    The probabilities are as follows (with weights shown in parentheses):
    
      - Under one mapping (Condition A):
          * Horizontal: EXPicted outcome is 45 (weight 3) and UEXicted outcome is 135 (weight 1)
          * Vertical:   EXPicted outcome is 135 (weight 3) and UEXicted outcome is 45 (weight 1)
      - Under the alternate mapping (Condition B):
          * Horizontal: EXPicted outcome is 135 (weight 3) and UEXicted outcome is 45 (weight 1)
          * Vertical:   EXPicted outcome is 45 (weight 3) and UEXicted outcome is 135 (weight 1)
    
    The neutral condition is always balanced:
      - neutralV -> 45 (weight 1) and neutralV -> 135 (weight 1).
    
    The auditory modality is structured analogously:
    
      - Two EXPictive tones (1000Hz, 1600Hz) and one neutral tone (neutralA).
      - Under Condition A (Auditory):
          * 1000Hz: EXPicted outcome is 100 (weight 3) and UEXicted outcome is 160 (weight 1)
          * 1600Hz: EXPicted outcome is 160 (weight 3) and UEXicted outcome is 100 (weight 1)
      - Under Condition B (Auditory):
          * 1000Hz: EXPicted outcome is 160 (weight 3) and UEXicted outcome is 100 (weight 1)
          * 1600Hz: EXPicted outcome is 100 (weight 3) and UEXicted outcome is 160 (weight 1)
      - The neutral condition is balanced:
          * neutralA -> 100 (weight 1) and neutralA -> 160 (weight 1)
    
    Trials are generated by taking the full cross–product of visual and auditory pairs.
    Each unique visual–auditory combination is repeated a number of times equal to the product
    of the visual weight and the auditory weight. Thus, the total number of trials is:
    
         Total visual weight (10) × Total auditory weight (10) = 100 trials.
    
    Parameters:
      seed (int, optional): Seed for the random number generator.
    
    Returns:
      List[dict]: A list of trial dictionaries. Each dictionary contains:
         - 'v_leading', 'v_trailing', 'v_pred'
         - 'a_leading', 'a_trailing', 'a_pred'
    """
    if seed is not None:
        random.seed(seed)
    
    # Randomize visual mapping: choose between two conditions.
    if random.choice([True, False]):
        # Condition A: horizontal->CW high, vertical->CCW high.
        visual_pairs = [
            # Vertical stimulus: high probability for CCW, low for CW.
            (90, 135, 'EXP', 3),
            (90, 45,  'UEX', 1),
            # Horizontal stimulus: high probability for CW, low for CCW.
            (0, 45, 'EXP', 3),
            (0, 135, 'UEX', 1),
        ]
    else:
        # Condition B: horizontal->CCW high, vertical->CW high.
        visual_pairs = [
            # Vertical stimulus: high probability for CW, low for CCW.
            (90, 45, 'EXP', 3),
            (90, 135, 'UEX', 1),
            # Horizontal stimulus: high probability for CCW, low for CW.
            (0, 135, 'EXP', 3),
            (0, 45, 'UEX', 1),
        ]
    # Add balanced neutral visual pairs.
    visual_pairs.append(('neutralV', 45, 'neutral', 2))
    visual_pairs.append(('neutralV', 135, 'neutral', 2))
    
    # Randomize auditory mapping: choose between two conditions.
    if random.choice([True, False]):
        # Condition A: 1000Hz->100Hz high, 1600Hz->160Hz high.
        auditory_pairs = [
            (1000, 100, 'EXP', 3),
            (1000, 160, 'UEX', 1),
            (1600, 160, 'EXP', 3),
            (1600, 100, 'UEX', 1),
        ]
    else:
        # Condition B: 1000Hz->160Hz high, 1600Hz->100Hz high.
        auditory_pairs = [
            (1000, 160, 'EXP', 3),
            (1000, 100, 'UEX', 1),
            (1600, 100, 'EXP', 3),
            (1600, 160, 'UEX', 1),
        ]
    # Add balanced neutral auditory pairs.
    auditory_pairs.append(('neutralA', 100, 'neutral', 2))
    auditory_pairs.append(('neutralA', 160, 'neutral', 2))
    
    # Build the cross–product.
    trials = []
    for v_lead, v_target, v_cond, v_weight in visual_pairs:
        for a_lead, a_target, a_cond, a_weight in auditory_pairs:
            count = v_weight * a_weight  # number of repetitions for this combination
            for _ in range(count):
                trial = {
                    'v_leading': v_lead,
                    'v_trailing': v_target,
                    'v_pred': v_cond,
                    'a_leading': a_lead,
                    'a_trailing': a_target,
                    'a_pred': a_cond
                }
                trials.append(trial)
    
    # Shuffle the trial order to randomize sequence.
    random.shuffle(trials)
    return trials


def setup():

    data_folder = Path(DATA_FOLDER)
    data_folder.mkdir(exist_ok=True) # create data folder if it does not exist

    # Initial dialog to check participant ID and create participant folder if it does not exist
    dialog1 = Dialog()
    dialog1.add_field(name="participant", default="01", label="Participant", format=int)
    data = dialog1.show()
    if not data:
        raise RuntimeError("User cancelled the dialog.")
    
    participant_id =  f"sub-{data['participant']:02d}"

    participant_folder = data_folder / participant_id
    # create participant folder if it does not exist
    participant_folder.mkdir(exist_ok=True)

    if not participant_folder.exists(): # open a second dialog to get the rest of the participant info

        dialog2 = Dialog("Demographic information")
        dialog2.add_field(name="gender", default="female", label="Gender", choices=["female", "male", "other"])
        dialog2.add_field(name="age", default="18", label="Age", format=int)
        dialog2.add_field(name="handedness", default="right", label="Handedness", choices=["right", "left"])
        data = dialog2.show()
        if not data:
            raise RuntimeError("User cancelled the dialog.")
        
        # We will store the participant data in a dictionary
        # Store basic participant info
        participant_data = {
            "participant_id": participant_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gender": data["gender"],
            "age": data["age"],
            "handedness": data["handedness"],
        }

        # We will also randomize the order of trials in the different phases, and key mappings
        key_mapping1 =  {"LEFT": "frequent", "RIGHT": "infrequent", "SPACE": "neutral"}
        key_mapping2 =  {"LEFT": "infrequent", "RIGHT": "frequent", "SPACE": "neutral"}

        random_key_order = random.choice([True, False])

        for block_i in range(PHASES["learning_blocks"]):
            participant_data[f"conditions_learning_{block_i + 1}"] = generate_trials() 
            participant_data[f"keymapping_learning_{block_i + 1}"] = key_mapping1 if block_i % 2 == random_key_order else key_mapping2

        for block_i in range(PHASES["test_blocks"]):
            participant_data[f"conditions_test_{block_i + 1}"] = generate_trials()
            participant_data[f"keymapping_test_{block_i + 1}"] = key_mapping1 if block_i % 2 == random_key_order else key_mapping2

        for block_i in range(PHASES["explicit_blocks"]):
            participant_data[f"conditions_explicit_{block_i + 1}"] = generate_trials()
            participant_data[f"keymapping_explicit_{block_i + 1}"] = key_mapping1 if block_i % 2 == random_key_order else key_mapping2

        # Save participant data
        with open(participant_folder / f"{participant_id}_info.json", "w") as f:
            json.dump(participant_data, f, indent=4)
    
    else:
        # Load participant data if it already exists
        with open(participant_folder / f"{participant_id}_info.json", "r") as f:
            participant_data = json.load(f)


    # We will run a final dialog to select the block and phase, and start each block
    # check which block we are in
    completed_learning = len([f for f in participant_folder.iterdir() if "learning" in f.name])
    completed_test = len([f for f in participant_folder.iterdir() if "test" in f.name])
    completed_explicit = len([f for f in participant_folder.iterdir() if "explicit" in f.name])

    if completed_learning < PHASES["learning_blocks"]:
        dialog3 = Dialog(title="Block selected based on participant progress")
        dialog3.add_field(name="phase", default="learning", label="Phase", choices=["learning", "test", "explicit"])
        dialog3.add_field(name="block", default=str(completed_learning + 1), label="Block", format=int)
        dialog3.add_field(name="full_screen", default="Yes", label="Full screen", choices=["Yes", "No"])
        data = dialog3.show()
        if not data:
            raise RuntimeError("User cancelled the dialog.")
        
    elif completed_test < PHASES["test_blocks"]:
        dialog3 = Dialog(title="Block selected based on participant progress")
        dialog3.add_field(name="phase", default="test", label="Phase", choices=["learning", "test", "explicit"])
        dialog3.add_field(name="block", default=str(completed_test + 1), label="Block", format=int)
        dialog3.add_field(name="full_screen", default="Yes", label="Full screen", choices=["Yes", "No"])
        data = dialog3.show()
        if not data:
            raise RuntimeError("User cancelled the dialog.")
        
    elif completed_explicit < PHASES["explicit_blocks"]:
        dialog3 = Dialog(title="Block selected based on participant progress")
        dialog3.add_field(name="phase", default="explicit", label="Phase", choices=["learning", "test", "explicit"])
        dialog3.add_field(name="block", default=str(completed_explicit + 1), label="Block", format=int)
        dialog3.add_field(name="full_screen", default="Yes", label="Full screen", choices=["Yes", "No"])
        data = dialog3.show()
        if not data:
            raise RuntimeError("User cancelled the dialog.")
    
    else:
        dialog3 = Dialog(title="All blocks have been completed. Running experiment again will override data of the selected block.")
        dialog3.add_field(name="phase", default="explicit", label="Phase", choices=["learning", "test", "explicit"])
        dialog3.add_field(name="block", default=PHASES["explicit_blocks"], label="Block", format=int)
        dialog3.add_field(name="full_screen", default="Yes", label="Full screen", choices=["Yes", "No"])
        data = dialog3.show()
        if not data:
            raise RuntimeError("User cancelled the dialog.")
    
    block = data["block"]
    phase = data["phase"]
    full_screen = data["full_screen"]

    
    window = Window(background_color=BACKGROUND_COLOR, fullscreen=full_screen == 'Yes')

    return window, participant_data, phase, block, full_screen





def setup():

    data_folder = Path(DATA_FOLDER)
    data_folder.mkdir(exist_ok=True)  # Create data folder if it does not exist

    # Initial dialog to check participant ID
    dialog1 = Dialog(title="Participant Info")
    dialog1.add_field(name="participant", default="01", label="Participant ID", format=int)
    data = dialog1.show()
    if not data:
        raise RuntimeError("User cancelled the dialog.")

    participant_id = f"sub-{data['participant']:02d}"
    participant_folder = data_folder / participant_id
    participant_folder.mkdir(exist_ok=True)  # Create participant folder

    participant_info_path = participant_folder / f"{participant_id}_info.json"

    # 🔹 Check if participant data already exists
    if not participant_info_path.exists():
        # Second dialog to collect demographic info
        dialog2 = Dialog(title="Demographic Information")
        dialog2.add_field(name="gender", default="female", label="Gender", choices=["female", "male", "other"])
        dialog2.add_field(name="age", default="18", label="Age", format=int)
        dialog2.add_field(name="handedness", default="right", label="Handedness", choices=["right", "left"])
        data = dialog2.show()
        if not data:
            raise RuntimeError("User cancelled the dialog.")

        # Store participant info
        participant_data = {
            "participant_id": participant_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gender": data["gender"],
            "age": data["age"],
            "handedness": data["handedness"],
        }

        # Key mappings
        key_mapping1 = {"LEFT": "frequent", "RIGHT": "infrequent", "SPACE": "neutral"}
        key_mapping2 = {"LEFT": "infrequent", "RIGHT": "frequent", "SPACE": "neutral"}
        random_key_order = random.choice([True, False])

        # Learning phase
        for block in range(PHASES["learning_blocks"]):
            participant_data[f"conditions_learning_{block + 1}"] = generate_trials()
            participant_data[f"keymapping_learning_{block + 1}"] = key_mapping1 if block % 2 == random_key_order else key_mapping2

        # Test phase
        for block in range(PHASES["test_blocks"]):
            participant_data[f"conditions_test_{block + 1}"] = generate_trials()
            participant_data[f"keymapping_test_{block + 1}"] = key_mapping1 if block % 2 == random_key_order else key_mapping2

        # Explicit phase
        for block in range(PHASES["explicit_blocks"]):
            participant_data[f"conditions_explicit_{block + 1}"] = generate_trials()
            participant_data[f"keymapping_explicit_{block + 1}"] = key_mapping1 if block % 2 == random_key_order else key_mapping2

        # 🔹 Save JSON file
        with open(participant_info_path, "w") as f:
            json.dump(participant_data, f, indent=4)

    else:
        # Load participant data if the file exists
        with open(participant_info_path, "r") as f:
            participant_data = json.load(f)

    # Check which blocks have been completed
    completed_learning = len([f for f in participant_folder.iterdir() if "learning" in f.name])
    completed_test = len([f for f in participant_folder.iterdir() if "test" in f.name])
    completed_explicit = len([f for f in participant_folder.iterdir() if "explicit" in f.name])

    # Dialog to select block and phase based on progress
    dialog3 = Dialog(title="Block Selection Based on Participant Progress")
    if completed_learning < PHASES["learning_blocks"]:
        dialog3.add_field(name="phase", default="learning", label="Phase", choices=["learning", "test", "explicit"])
        dialog3.add_field(name="block", default=str(completed_learning + 1), label="Block", format=int)
    elif completed_test < PHASES["test_blocks"]:
        dialog3.add_field(name="phase", default="test", label="Phase", choices=["learning", "test", "explicit"])
        dialog3.add_field(name="block", default=str(completed_test + 1), label="Block", format=int)
    elif completed_explicit < PHASES["explicit_blocks"]:
        dialog3.add_field(name="phase", default="explicit", label="Phase", choices=["learning", "test", "explicit"])
        dialog3.add_field(name="block", default=str(completed_explicit + 1), label="Block", format=int)
    else:
        dialog3 = Dialog(title="All blocks completed. Running experiment again will overwrite data.")
        dialog3.add_field(name="phase", default="explicit", label="Phase", choices=["learning", "test", "explicit"])
        dialog3.add_field(name="block", default=PHASES["explicit_blocks"], label="Block", format=int)

    dialog3.add_field(name="full_screen", default="Yes", label="Full screen", choices=["Yes", "No"])
    data = dialog3.show()
    if not data:
        raise RuntimeError("User cancelled the dialog.")

    block = data["block"]
    phase = data["phase"]
    full_screen = data["full_screen"]

    #  window for the experiment
    window = Window(background_color=BACKGROUND_COLOR, fullscreen=full_screen == "Yes")

    return window, participant_data, phase, block, full_screen