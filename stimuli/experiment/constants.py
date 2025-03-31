# constants for data storage
DATA_FOLDER = "data"

# Constants for the experiment setup
PHASES = {
    "learning_blocks": 2,
    "test_blocks": 1,
    "explicit_blocks": 1,
}

# Constants for the experiment visuals
BACKGROUND_COLOR = "grey" 
COLOR = "white" # Color of the text
INSTRUCTIONS_FONT_SIZE = 24
RESPONSE_FONT_SIZE = 20
FIXATION_FONT_SIZE = 30


# Instructions for the different blocks and phases
INSTRUCTIONS_TEXT = {
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


STIM_INFO = {
    "iti_range": (1.5, 2.25),
    "leading_duration": 0.5,
    "isi_duration": 0.5,
    "target_duration": 0.5,
}

GABOR_SIZE = "50vw"


