import argparse
import os

from experiment.constants import BATCH_SEQUENCES
from experiment.phases import run_phase #(explicit_phase, learning_phase, run_phase,test_phase)
from experiment.setup import setup


def main(batch=None):
    """
    Main function that runs the experiment. 
    If no batch is specified, the experimenter will manually select an individual block and phase to run.
    Otherwise, if the script is run like: python main.py --batch 1,2..., it will run all blocks specified in the batch.
    """
    window, participant_data, phase, block, full_screen, screen_info = setup()
    if batch:
        for (p, b) in BATCH_SEQUENCES[batch]:
            if b in participant_data.get("completed_blocks", {}).get(p, []):
                print(f"Skipping {p} block {b}: already completed.")
                continue
            run_phase(p, b, window, participant_data, full_screen, screen_info)
    
    else:
        if block in participant_data.get("completed_blocks", {}).get(phase, []):
            print(f"Skipping {phase} block {block}: already completed.")
            return
        run_phase(phase, block, window, participant_data, full_screen, screen_info)


if __name__ == "__main__":
    # Move to the directory where the script is located
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # allow command line argument "batch" to run a specific batch of blocks
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=str, choices=BATCH_SEQUENCES.keys(), help="Run predefined part of the experiment")
    args = parser.parse_args()

    try:
        main(batch=args.batch)
    except RuntimeError as e:
        raise e
