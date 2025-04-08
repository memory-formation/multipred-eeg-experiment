import os

from experiment.phases import learning_phase, test_phase, explicit_phase, localizer_phase
from experiment.setup import setup


# Main function that runs the experiment
def main():
    # Setup
    window, participant_data, phase, block, full_screen, screen_info = setup()

    if phase == "localizer":
        localizer_phase(participant_data, block, window, full_screen, screen_info)
        
    if phase == "learning":
        learning_phase(participant_data, block, window, full_screen, screen_info)
    
    elif phase == "test":
        test_phase(participant_data, block, window, full_screen, screen_info)

    elif phase == "explicit":
        explicit_phase(participant_data, block, window, full_screen, screen_info)


if __name__ == "__main__":
    # Move to the directory where the script is located
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    try:
        main()
    except RuntimeError as e:
        raise e
