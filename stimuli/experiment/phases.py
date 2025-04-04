import random
from datetime import datetime

from experiment.constants import (COLOR, INITIAL_STAIRCASE, INSTRUCTIONS_TEXT,
                                  ISOTONIC_SOUNDS, STAIRCASE_PARAMS, STIM_INFO)
from experiment.presentation import (create_puretone, draw_fixation,
                                     draw_gabor, show_instructions)
from experiment.responses import (explicit_response, learning_response,
                                  load_last_staircase_data, localizer_response,
                                  save_block_data, staircase, test_response)
from psychos.core import Clock, Interval


def localizer_phase(participant_data, block, window, full_screen):
    # Instructions
    if block == 1:
        show_instructions(window, INSTRUCTIONS_TEXT["localizer_start"])
    else:
        show_instructions(window, INSTRUCTIONS_TEXT["localizer_continue"])
   
    conditions = participant_data[f"conditions_localizer_{block}"]
    block_data = []

    for i, trial in enumerate(conditions):
        if i == 0:
            fixation_color = COLOR  # set the fixation color. In subsequent trials, the fixation color will be updated based on the response to provide feedback
        
        trial_clock = Clock()  # This allows to init a clock to measure the RT
        trial_clock.reset()
        timestamp_dicts = {}
        # Time up to milliseconds (4 digits of )
        timestamp_dicts["start_trial_absolute"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )

        # ====== Inter trial interval ==========
        iti_duration = random.uniform(*STIM_INFO["iti_range"])
        interval = Interval(duration=iti_duration)  # This allows to init a time counter of duration
        interval.reset()  # This allows to reset the time counter
        draw_fixation(fixation_color)  # draw the fixation dot with feedback color
        window.flip()
        timestamp_dicts["start_fixation"] = trial_clock.time()

        # ======= Stimuli sequence ========
        for auditory_freq, visual_ori, target, block_modality, target_modality in zip(trial["auditory_sequence"], trial["visual_sequence"], trial["target_sequence"], trial["block_modality"], trial["target_modality"]):
            
            # Checking for visual or audiotry target, and setting the amplitude and contrast accordingly
            if block_modality == "multimodal":
                if target_modality == "auditory":
                    if target == 1:
                        amplitude = ISOTONIC_SOUNDS[auditory_freq] * 0.5 # half the amplitude of sound
                        contrast = 1 # keep the contrast of the gabor
                    else:
                        amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                        contrast = 1
                else: # target modality visual
                    if target == 1:
                        amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                        contrast = 0.5 # half the contrast of the gabor
                    else:
                        amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                        contrast = 1
            elif block_modality == "auditory":
                if target == 1:
                    amplitude = ISOTONIC_SOUNDS[auditory_freq] * 0.5
                    contrast = 1 # keep the contrast of the gabor
                else:
                    amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                    contrast = 1
            else: # visual
                if target == 1:
                    amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                    contrast = 0.5
                else:
                    amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                    contrast = 1

            # pre-load stimuli
            if block_modality == "multimodal":
                tone = create_puretone(
                    frequency=auditory_freq, duration=STIM_INFO["leading_duration"], amplitude=amplitude
                )
                draw_gabor(visual_ori, contrast) # Preload gabor
                draw_fixation(fixation_color) # Preload fixation
            elif block_modality == "auditory":
                tone = create_puretone(
                    frequency=auditory_freq, duration=STIM_INFO["leading_duration"], amplitude=amplitude
                )
                draw_fixation(fixation_color) # Preload fixation, but not the gabor
            else: # visual
                tone = create_puretone(
                    frequency=auditory_freq, duration=STIM_INFO["leading_duration"], amplitude=0 # No sound in visual block
                )
                draw_gabor(visual_ori, contrast)
                draw_fixation(fixation_color) # Preload fixation

            interval.wait()  # Waits for the remaining time of the interval
            tone.play()  # play the leading tone
            window.flip()  # Flips the window to show the pre-loaded gabor
            timestamp_dicts["start_leading"] = trial_clock.time()
            window.wait(STIM_INFO["leading_duration"])  # Waits for the leading duration
            # ======= ISI ========
            interval = Interval(duration=STIM_INFO["isi_duration"])
            interval.reset()
            draw_fixation(fixation_color)
            window.flip()
            timestamp_dicts["start_isi"] = trial_clock.time()
        
        # ======= Response ========
        timestamp_dicts["start_response"] = trial_clock.time()
        response = localizer_response(window, target_modality, target)
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
    save_block_data(participant_data, block_data, "localizer", block)



def learning_phase(participant_data, block, window, full_screen):
    # Instructions
    if block == 1:
        show_instructions(window, INSTRUCTIONS_TEXT["learning_start"])
    else:
        show_instructions(window, INSTRUCTIONS_TEXT["learning_continue"])
   

    conditions = participant_data[f"conditions_learning_{block}"]
    key_mapping = participant_data[f"keymapping_learning_{block}"]
    block_data = []

    for i, trial in enumerate(conditions[:10]):
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
            frequency=trial["a_leading"], duration=STIM_INFO["leading_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_leading"]]
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
            frequency=trial["a_trailing"], duration=STIM_INFO["target_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_trailing"]]
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




def test_phase(participant_data, block, window, full_screen):
    # Instructions
    if block == 1:
        show_instructions(window, INSTRUCTIONS_TEXT["test_start"])
    else:
        show_instructions(window, INSTRUCTIONS_TEXT["test_continue"])
   

    conditions = participant_data[f"conditions_test_{block}"]
    key_mapping = participant_data[f"keymapping_test_{block}"]
    block_data = []

    for i, trial in enumerate(conditions[:20]):
        if i == 0: # first trial of the block
            fixation_color = COLOR  # set the fixation color. In subsequent trials, the fixation color will be updated based on the response to provide feedback

            # Get staircase history
            if block == 1: 
                staircase_data = INITIAL_STAIRCASE # get the initial parameters, same for every participant
            else: 
                # get the last parameters from the previous block
                staircase_data = load_last_staircase_data(participant_data, block)

        else: # subsequent trials
            fixation_color = response["fixation_color"] # update fixation color based on the last response to provide feedback
        
     
        trial_clock = Clock()  # This allows to init a clock to measure the RT
        trial_clock.reset()
        timestamp_dicts = {}
        # Time up to milliseconds (4 digits of )
        timestamp_dicts["start_trial_absolute"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )

        # ====== Inter trial interval ==========
        iti_duration = random.uniform(*STIM_INFO["iti_range"])
        interval = Interval(duration=iti_duration)  # This allows to init a time counter of duration
        interval.reset()  # This allows to reset the time counter
        draw_fixation(fixation_color)  # draw the fixation dot with feedback color
        window.flip()
        timestamp_dicts["start_fixation"] = trial_clock.time()

        # ======= Leding stimuli ========
        leading_tone = create_puretone(frequency=trial["a_leading"], duration=STIM_INFO["leading_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_leading"]])
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
        trailing_tone = create_puretone(frequency=trial["a_trailing"], duration=STIM_INFO["target_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_trailing"]])
        if trial["target"] == 0:
            current_ori_diff = 0
        else: # in target trials we add a random orientation difference to the trailing gabor
            current_ori_diff = staircase_data["ori_diff"]
            current_ori_diff = random.choice([-current_ori_diff, current_ori_diff])

        draw_gabor(trial["v_trailing"] + current_ori_diff)  # draw the trailing gabor
        interval.wait()
        trailing_tone.play()
        window.flip()
        timestamp_dicts["start_trailing"] = trial_clock.time()
        window.wait(STIM_INFO["target_duration"])

        # ======= Response ========
        timestamp_dicts["start_response"] = trial_clock.time()
        response = test_response(window, key_mapping, trial)
        timestamp_dicts["end_trial"] = trial_clock.time()

        # --- Update the staircase if this is a target trial ---
        if trial["target"] == 1:
            # Update staircase_data
            staircase_data["last_outcome"] = response["outcome"]
            # Update staircase parameters based on participant's response.
            staircase_data = staircase(**staircase_data, **STAIRCASE_PARAMS)
                

        block_data.append(
            {
                "num_trial": i,
                "iti_duration": iti_duration,
                **trial,
                **response,
                **timestamp_dicts,
                **staircase_data,
                "full_screen": full_screen,
            }
        )


    # Save the block data
    save_block_data(participant_data, block_data, "test", block)



def explicit_phase(participant_data, block, window, full_screen):
    # Instructions
    show_instructions(window, INSTRUCTIONS_TEXT["explicit_phase"])
   
    conditions = participant_data[f"conditions_explicit_{block}"]
    key_mapping = participant_data[f"keymapping_explicit_{block}"]
    block_data = []

    for i, trial in enumerate(conditions):
        if i == 0:
            fixation_color = COLOR  # set the fixation color. In subsequent trials, in this phase there is no feedback so it won't be updated
        
        trial_clock = Clock()  # This allows to init a clock to measure the RT
        trial_clock.reset()
        timestamp_dicts = {}
        # Time up to milliseconds (4 digits of )
        timestamp_dicts["start_trial_absolute"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )

        # ====== Inter trial interval ==========
        iti_duration = random.uniform(*STIM_INFO["iti_range"])
        interval = Interval(duration=iti_duration)  # This allows to init a time counter of duration
        interval.reset()  # This allows to reset the time counter
        draw_fixation(fixation_color)  # draw the fixation dot with feedback color
        window.flip()
        timestamp_dicts["start_fixation"] = trial_clock.time()

        # ======= Leding stimuli ========
        # pre-load stimuli
        if trial["modality"] == "auditory":
            leading_tone = create_puretone(
                frequency=trial["a_leading"], duration=STIM_INFO["leading_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_leading"]]
            )
            draw_fixation(fixation_color)
        else:
            draw_gabor(trial["v_leading"])  # initiate the leading gabor,
            draw_fixation(fixation_color)

        interval.wait()  # Waits for 
        if trial["modality"] == "auditory": leading_tone.play()  # play the leading tone only in auditory block
        window.flip()  # Flips the window to show the pre-loaded gabor and fixation
        timestamp_dicts["start_leading"] = trial_clock.time()
        window.wait(STIM_INFO["leading_duration"])  # Waits for the leading duration

        # ======= ISI ========
        interval = Interval(duration=STIM_INFO["isi_duration"])
        interval.reset()
        draw_fixation(fixation_color)
        window.flip()
        timestamp_dicts["start_isi"] = trial_clock.time()

        # ======= Trailing stimuli ========
        # pre-load stimuli
        if trial["modality"] == "auditory":
            draw_fixation(fixation_color)
            trailing_tone = create_puretone(
                frequency=trial["a_trailing"], duration=STIM_INFO["target_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_trailing"]]
            )
        else:
            draw_gabor(trial["v_trailing"])
            draw_fixation(fixation_color)
        
        interval.wait()
        if trial["modality"] == "auditory": trailing_tone.play()  # play the leading tone only in auditory block
        window.flip()
        timestamp_dicts["start_trailing"] = trial_clock.time()
        window.wait(STIM_INFO["target_duration"])

        # ======= Response ========
        timestamp_dicts["start_response"] = trial_clock.time()
        response = explicit_response(window, key_mapping, trial)
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
    save_block_data(participant_data, block_data, "explicit", block)
