import os
import random
from datetime import datetime

from experiment.constants import COLOR, INSTRUCTIONS_TEXT, STIM_INFO
from experiment.presentation import (create_puretone, draw_fixation,
                                     draw_gabor, learning_response,
                                     show_instructions)
from experiment.responses import save_block_data
from experiment.setup import setup
from psychos.core import Clock, Interval

# Functions to control the flow of the experiment


def learning_phase(participant_data, block, window, full_screen):
    # Instructions
    if block == 1:
        show_instructions(window, INSTRUCTIONS_TEXT["learning_start"])
    else:
        show_instructions(window, INSTRUCTIONS_TEXT["learning_continue"])
   

    conditions = participant_data[f"conditions_learning_{block}"]
    key_mapping = participant_data[f"keymapping_learning_{block}"]
    block_data = []

    for i, trial in enumerate(conditions[:2]):
        if i == 0:
            fixation_color = COLOR  # set the fixation color. In subsequent trials, the fixation color will be updated based on the response to provide feedback
        else: 
            fixation_color = response["fixation_color"]
        trial_clock = Clock()  # This allows to init a clock to measure the RT
        trial_clock.reset()
        timestamp_dicts = {}
        # Time up to milliseconds (4 digits of )
        timestamp_dicts["start_trial_absolute"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )

        # ====== Inter trial interval ==========
        iti_duration = random.uniform(*STIM_INFO["iti_range"])
        interval = Interval(
            duration=iti_duration
        )  # This allows to init a time counter of duration
        interval.reset()  # This allows to reset the time counter
        draw_fixation(fixation_color)  # draw the fixation dot with feedback color
        window.flip()
        timestamp_dicts["start_fixation"] = trial_clock.time()

        # ======= Leding stimuli ========
        leading_tone = create_puretone(
            frequency=trial["a_leading"], duration=STIM_INFO["leading_duration"]
        )
        draw_gabor(trial["v_leading"])  # initiate the leading gabor,
        interval.wait()  # Waits for the remaining time of the interval

        leading_tone.play()  # play the leading tone
        window.flip()  # Flips the window to show the pre-loaded gabor
        timestamp_dicts["start_leading"] = trial_clock.time()
        window.wait(STIM_INFO["leading_duration"])  # Waits for the leading duration

        # ======= ISI ========
        interval = Interval(duration=STIM_INFO["isi_duration"])
        interval.reset()
        fixation_color = COLOR  # reset the fixation color to the default color for the ISI
        draw_fixation(fixation_color)
        window.flip()
        timestamp_dicts["start_isi"] = trial_clock.time()

        # ======= Trailing stimuli ========
        trailing_tone = create_puretone(
            frequency=trial["a_trailing"], duration=STIM_INFO["target_duration"]
        )
        draw_gabor(trial["v_trailing"])
        interval.wait()
        trailing_tone.play()
        window.flip()
        timestamp_dicts["start_trailing"] = trial_clock.time()
        window.wait(STIM_INFO["target_duration"])
        timestamp_dicts["start_response"] = trial_clock.time()
        response = learning_response(window, key_mapping, trial)
        timestamp_dicts["end_trial"] = trial_clock.time()
        block_data.append(
            {
                "num_trial": i,
                "iti_duration": iti_duration,
                **trial,
                **response,
                **timestamp_dicts,
                "full_screen": full_screen,
            }
        )
    # Save the block data
    save_block_data(participant_data, block_data, "learning", block)


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
