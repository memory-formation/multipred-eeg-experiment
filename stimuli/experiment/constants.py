from experiment.triggers import generate_triggers

SCREENS = {
    "hp_laptop": {"screen_name": "HP Laptop",
                "distance_cm": 50,
                "screen_width_cm":34.5,
                "screen_width_px":1920 *0.8,
                "screen_height_px":1080 *0.8,},
    "VU_experiment": {"screen_name": "VU Experiment",
                "distance_cm": 70,
                "screen_width_cm":52.6,
                "screen_width_px":1920,
                "screen_height_px":1080,},

}

# constants for data storage
DATA_FOLDER = "data"

# Constants for the experiment setup
PHASES = {
    "localizer_trials": 50,
    "localizer_blocks": ["multimodal", "multimodal"], # can be "visual", "auditory" or "multimodal"
    "localizer_targets": ["visual", "visual"], # When blocks are multimodal, this will define the target modality
    "learning_blocks": 2,
    "test_blocks": 10, # make it even
    "explicit_blocks": 2,
}

# This controls batch execution. Each batch will run a different set of blocks in the order specified here.
BATCH_SEQUENCES = {
    "1": [("localizer", 1), ("learning", 1), ("learning", 2)],
    "2": [("test", i) for i in range(1, PHASES["test_blocks"]//2 + 1)],
    "3": [("test", i) for i in range(PHASES["test_blocks"]//2 + 1, PHASES["test_blocks"] + 1)],
    "4": [("localizer", 2), ("explicit", 1), ("explicit", 2)],
}


# Constants for the experiment visuals
BACKGROUND_COLOR = "grey" 
COLOR = "white" # Color of the text
INSTRUCTIONS_FONT_SIZE = 16
RESPONSE_FONT_SIZE = 18
FIXATION_FONT_SIZE = 15


STIM_INFO = {
    "iti_range": (0.75, 1.5),
    "leading_duration": 0.5,
    "isi_duration": 0.5,
    "target_duration": 0.5,
}

INITIAL_STAIRCASE = { # Intiial values for the staircase, same for all partiicpants bu updated during the experiment
    "last_outcome": None, # Just needed to initialize the staircase
    "ori_diff": 15, # initial value of orientation difference. In the first 
    "inversions_count": 0, # How many times the staircase has changed direction, from increasing to decreasing or vice versa
    "last_direction" : "down", # Last direction of the staircase
    "history": 0, # How many consecutive trials have been correct before this one
    "step_size": None, # This is updated during the experiment, based on staircase_params
}
   
STAIRCASE_PARAMS = { # Parameters to control how the staircase adapts to performance
    "step_size_list": [6, 4, 2, 1], # How much ori_diff is updated after a given number of inversions
    "step_update": [2, 4, 8], # After how manny inversions the step size is updated
    "max_diff": 20, # Maximum orientation difference allowed for diagonal targets. Greater than 22.5 would be closer to cardinal orientations
}

FIXATION_PARAMS = {
    "color": "white",
    "radius": 0.1, # in degrees
}

GABOR_PARAMS = {
    "contrast": 1,
    "spatial_frequency": 2.4, # Spatial frequency of the Gabor in cycles per degree
    "size": 20, 
    "units": "deg" #"deg", # Units of the Gabor size. If None it will be "50vw", and spatial_frquency 20 cycles for the whole image
}


ISOTONIC_SOUNDS = { # Amplitudes needed for each frequency to make them isotonic. (calculated according to ISO 266)
    100: 1, 
    160: 0.25, # according to ISO it should be 0.41 but different people preceive it louder than the rest
    1000: 0.061,
    1600: 0.081,

}

CONDITIONS_MAIN = { # Define conditions in the test and learning phases
    "v_stimulus": [45, 135],
    "v_pred_cond": ["EXP", "UEX", "neutral"],
    "a_stimulus": [100, 160],
    "a_pred_cond": ["EXP", "UEX"],
}

TRIGGER_MAPPING = generate_triggers(CONDITIONS_MAIN) # Generate dictionary that assigns trigger numbers to each trial type and event

# Instructions for the different blocks and phases
INSTRUCTIONS_TEXT = {
    "localizer_start": [
        "We are about to start the functional localizer phase.",
        "You will see a sequence of 8 Gabor patches, accompanied by a sound.",
        "Your task is to count how many Gabor patches had a lower spatial frequency (lines more spread out)",
        "Press the space bar when you are ready to start.",
    ],

    "localizer_continue": [
        "We are going to do another functional localizer.", 
        "You will see a sequence of 8 Gabor patches, accompanied by a sound.",
        "Your task is to count how many Gabor patches had a lower spatial frequency (lines more spread out)",
        "Press the space bar to continue.",
    ],
   
    "learning_start": [
        "Now the experiment begins: you will learn to associate pairs of visual stimuli.",
        "You will see an oriented visual stimulus followed by a second oriented stimulus.",
        "Some orientations are paired together more frequently.",
        "Your task is to learn the associations, and discriminate between frequent and infrequent pairs.",
        "Press the space bar to continue.",
    ],

    "learning_continue": [
        "You are about to start a second block, identical to the previous one. Remember the associations you have learned. ", 
        "Your task is the same: discriminate between frequent and infrequent pairs of orientations.", 
        "Press the space bar to start.",
    ],

    "test_start": [
        f"The main part of the experiment is about to start. You will complete a total of {PHASES['test_blocks']} blocks.",
        "You will continue seeing the same oriented stimuli, but your task will change.",
        "On half of the trials, the orientation of the second stimulus will deviate from the perfect diagonals you have seen so far.",
        'Your task is to indicate whether the second orientation is a "normal" or a "deviant" diagonal.',
        "Press the space bar to start.",
    ],

    "test_continue": [
        "You are about to start block {block}! {remaining_blocks} more to go.", 
        'The task remains the same: indicate whether the second orientation is a "normal" or a "deviant" diagonal.', 
        "Press the space bar to start.",
    ],

    "explicit_phase": [
        "Now we will test if you {modality_task}",
        "You will {modality_verb} {modality} stimulus followed by another one.",
        "Your task is to indicate whether the pair was frequent or infrequent.",
        "After responding, you will have to indicate how confident you are about your answer (1-5).",
        "Press the space bar to start.",
    ],
}
