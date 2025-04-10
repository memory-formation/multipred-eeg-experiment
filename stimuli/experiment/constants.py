from experiment.triggers import generate_triggers

SCREENS = {
    "hp_laptop": {"screen_name": "HP Laptop",
                "distance_cm": 50,
                "screen_width_cm":34.5,
                "screen_width_px":1920,},
    "VU_experiment": {"screen_name": "VU Experiment",
                "distance_cm": 70,
                "screen_width_cm":52.6,
                "screen_width_px":1920,},

}

# constants for data storage
DATA_FOLDER = "data"

# Constants for the experiment setup
PHASES = {
    "localizer_trials": 10,
    "localizer_blocks": ["auditory", "visual"], # another option is ["multimodal", "multimodal"]
    "learning_blocks": 2,
    "test_blocks": 2,
    "explicit_blocks": 2,
}

# Constants for the experiment visuals
BACKGROUND_COLOR = "grey" 
COLOR = "white" # Color of the text
INSTRUCTIONS_FONT_SIZE = 24
RESPONSE_FONT_SIZE = 20
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
}

GABOR_PARAMS = {
    "contrast": 1,
    "spatial_frequency": 2.4, # Spatial frequency of the Gabor in cycles per degree
    "size": 20, 
    "units": "deg" #"deg", # Units of the Gabor size. If None it will be "50vw", and spatial_frquency 20 cycles for the whole image
}



ISOTONIC_SOUNDS = { # Amplitudes needed for each frequency to make them isotonic. (calculated according to ISO 266)
    100: 0.8, 
    160: 0.41,
    1000: 0.061,
    1600: 0.081,

}

CONDITIONS_MAIN = { # Define conditions in the test and learning phases
    "v_stimulus": [45, 135],
    "v_pred_cond": ["EXP", "UEX", "neutral"],
    "a_stimulus": [100, 160],
    "a_pred_cond": ["EXP", "UEX"],
}
TRIGGERS_MAIN = generate_triggers(CONDITIONS_MAIN) # Generate dictionary that assigns trigger numbers to each trial type and event
    
    
# Instructions for the different blocks and phases
INSTRUCTIONS_TEXT = {
    "localizer_start": [
        "Welcome to the localizer phase.",
        "You will see a visual stimulus followed by an auditory stimulus.",
        "Your task is to indicate whether the visual stimulus was frequent or infrequent.",
        "Press the space bar to continue.",
    ],

    "localizer_continue": [
        "You are about to start the next block.", 
        "Remember the associations you have learned. Your task is the same: discrimiante between frequent and infrequent pairs of orientations.", 
        "Press the space bar to continue.",
    ],
   
    "learning_start": [
        "Welcome to this experiment. In this phase, you will learn to associate pairs of visual stimuli.",
        "You will see an oriented visual stimulus followed by a second oriented stimulus.",
        "Some orientations are paired together more frequently.",
        "Your task is to learn the associations, and discrimiante between frequent and infrequent pairs.",
        "Press the space bar to continue.",
    ],

    "learning_continue": [
        "You are about to start the next block.", 
        "Remember the associations you have learned. Your task is the same: discrimiante between frequent and infrequent pairs of orientations.", 
        "Press the space bar to continue.",
    ],

    "test_start": [
        "Welcome to the test phase.",
        "You will continue seeing the same oriented stimuli, but your task will change.",
        "On half of the trials, the orientation of the second stimulus will deviate from the perfect diagonals you have seen so far.",
        'Your task is to indicate whether the second orientation is a "normal" or a "deviant" diagonal.',
        "Press the space bar to continue.",
    ],

    "test_continue": [
        "You are about to start the next block.", 
        'The task remains the same: indicate whether the second orientation is a "normal" or a "deviant" diagonal.', 
        "Press the space bar to continue.",
    ],

    "explicit_phase": [
        "Welcome to the explicit phase.",
        "You will see a visual stimulus followed by an auditory stimulus.",
        "Your task is to indicate whether the visual stimulus was frequent or infrequent.",
        "Press the space bar to continue.",
    ],
}
