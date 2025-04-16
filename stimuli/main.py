import argparse
import os

import experiment.eyelinker as eyelinker
from experiment.constants import BATCH_SEQUENCES
from experiment.phases import run_phase
from experiment.setup import setup
from experiment.triggers import get_tracker


def main(batch=None):
    """
    Main function that runs the experiment. 
    If no batch is specified, the experimenter will manually select an individual block and phase to run.
    Otherwise, if the script is run like: python main.py --batch 1,2..., it will run all blocks specified in the batch.
    """
    window, participant_data, phase, block, full_screen, screen_info, tracker = setup()
    mock_tracker = getattr(tracker, 'mock', False) # Check if the tracker is in mock mode
    get_tracker(tracker) # inject tracker object in the triggers module

    # Using batch sequences to run specific blocks
    if batch:
        for (p, b) in BATCH_SEQUENCES[batch]:

            if b in participant_data.get("completed_blocks", {}).get(p, []): # Check if the block has already been completed
                print(f"Skipping {p} block {b}: already completed.")
                continue
   
            if mock_tracker: # Check if the tracker is in mock mode
                print(f"Skipping eye tracking recording in mock mode.")
            else:
                eyelinker.offline_mode_start() # Start recording Eye

            run_phase(p, b, window, participant_data, full_screen, screen_info)

            if not mock_tracker:tracker.transfer_edf() # Send eye data at the end of each block
            
    # You can also run specific blocks 
    else:
        if block in participant_data.get("completed_blocks", {}).get(phase, []):
            print(f"Skipping {phase} block {block}: already completed.")
            return
        
        if mock_tracker:
            print(f"Skipping eye tracking recording in mock mode.")
        else:
            eyelinker.offline_mode_start() # Start recording Eye
        
        run_phase(phase, block, window, participant_data, full_screen, screen_info)
        if not mock_tracker: tracker.transfer_edf() # Send eye data at the end of each block


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
