import os

from experiment.phases import learning_phase
from experiment.setup import setup


# Main function that runs the experiment
def main():
    # Setup
    window, participant_data, phase, block, full_screen = setup()

    if phase == "learning":
        learning_phase(participant_data, block, window, full_screen)
    
    elif phase == "test":
        print("Test phase")

    elif phase == "explicit":
        print("Explicit phase")


if __name__ == "__main__":
    # Move to the directory where the script is located
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    try:
        main()
    except RuntimeError as e:
        raise e
