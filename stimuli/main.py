# import ctypes
# # do not let windows scale the app to the screen resolution, keep control of the window size
# try:
#     ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 2 = PROCESS_PER_MONITOR_DPI_AWARE
# except Exception as e:
#     print("Could not set DPI awareness:", e)

import argparse
import os

import experiment.eyelinker as eyelinker
from experiment.constants import BATCH_SEQUENCES
from experiment.phases import run_phase
from experiment.setup import setup
from experiment.triggers import get_tracker, send_trigger


def main(batch=None):
    """
    Main function that runs the experiment. 
    If no batch is specified, the experimenter will manually select an individual block and phase to run.
    Otherwise, if the script is run like: python main.py --batch 1,2..., it will run all blocks specified in the batch.
    """
    # === SETUP ===
    window, participant_data, phase, block, full_screen, screen_info, edf_filename = setup(batch)
    print(window.width)
    # === EYE TRACKER ===
    # Initialize the EyeLink tracker
    tracker = eyelinker.EyeLinker(window, edf_filename, 'RIGHT')  # {data_folder}/{participant_id}/{participant_id}_eye.edf'
    tracker.init_tracker()
    mock_tracker = getattr(tracker, 'mock', False) # Check if the tracker is in mock mode
    get_tracker(tracker) # inject tracker object in the triggers module

    # Calibrate
    tracker.testFunAndCalib()

    # Start recording eye
    if mock_tracker: # Check if the tracker is in mock mode
        print(f"Skipping eye tracking recording in mock mode.")
    else:
        eyelinker.offline_mode_start() # Start recording Eye

    # ==== RUN EXPERIMENT ====
    # Using batch sequences to run specific blocks
    if batch:
        context = f"BATCH {batch}" # context for trigger logs
        send_trigger("recording_on", context=context) # Send trigger to EEG system to start recording

        for (p, b) in BATCH_SEQUENCES[batch]:

            if b in participant_data.get("completed_blocks", {}).get(p, []): # Check if the block has already been completed
                print(f"Skipping {p} block {b}: already completed.")
                continue

            run_phase(p, b, window, participant_data, full_screen, screen_info)

        if not mock_tracker: tracker.transfer_edf() # Send eye data at the end of each batch
        send_trigger("recording_off", context=context) # Send trigger to EEG system to stop recording
            
    # You can also run specific blocks 
    else:
        if block in participant_data.get("completed_blocks", {}).get(phase, []):
            print(f"Skipping {phase} block {block}: already completed.")
            return
        
        run_phase(phase, block, window, participant_data, full_screen, screen_info)
        if not mock_tracker: tracker.transfer_edf() # Send eye data at the end of each block

    tracker.close_connection()


if __name__ == "__main__":
    # Move to the directory where the script is located
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # allow command line argument "batch" to run a specific batch of blocks
    parser = argparse.ArgumentParser()
