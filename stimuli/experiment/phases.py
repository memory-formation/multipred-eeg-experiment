import random
from datetime import datetime

from experiment.constants import (FIXATION_PARAMS, GABOR_PARAMS,
                                  INITIAL_STAIRCASE, INSTRUCTIONS_TEXT,
                                  ISOTONIC_SOUNDS, PHASES, STAIRCASE_PARAMS,
                                  STIM_INFO)
from experiment.presentation import (create_puretone, draw_fixation,
                                     draw_gabor, show_instructions)
from experiment.responses import (explicit_response, learning_response,
                                  load_last_staircase_data, localizer_response,
                                  save_block_data, staircase, test_response)
from experiment.triggers import send_trigger
from psychos.core import Clock, Interval


def localizer_phase(participant_data, block, window, full_screen, screen_info):
    # Instructions
    if block == 1:
        show_instructions(window, INSTRUCTIONS_TEXT["localizer_start"], screen_info)
    else:
        show_instructions(window, INSTRUCTIONS_TEXT["localizer_continue"], screen_info)
   
    conditions = participant_data[f"conditions_localizer_{block}"]
    block_data = []

    for i, trial in enumerate(conditions):
        context = f"Trial {i+1}, Block {block}, localizer phase" # context for trigger logs
        if i == 0:
            fixation_color = FIXATION_PARAMS["color"]  # set the fixation color. In subsequent trials, the fixation color will be updated based on the response to provide feedback
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
        interval = Interval(duration=iti_duration)  # This allows to init a time counter of duration
        send_trigger("loc_trial_start", context) # send trigger for the start of the trial
        interval.reset()  # This allows to reset the time counter
        draw_fixation(fixation_color, screen_info)  # draw the fixation dot with feedback color
        window.flip()
        timestamp_dicts["start_fixation"] = trial_clock.time()
        
        # ======= Stimuli sequence ========
        for auditory_freq, visual_ori, target, block_modality, target_modality in zip(trial["auditory_sequence"], trial["visual_sequence"], trial["target_sequence"], trial["block_modality"], trial["target_modality"]):      
            # pre-load stimuli
            fixation_color =  FIXATION_PARAMS["color"] # reset the fixation color to the default color for the ISI
            if block_modality == "multimodal":
                # Checking for visual or audiotry target, and setting the amplitude and spatial frequency accordingly
                if target_modality == "auditory":
                    if target == 1:
                        amplitude = ISOTONIC_SOUNDS[auditory_freq] * 0.2 # half the amplitude of sound
                        spatial_frequency = GABOR_PARAMS["spatial_frequency"] # default
                    else:
                        amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                        spatial_frequency = GABOR_PARAMS["spatial_frequency"] # default
                else: # target modality visual
                    if target == 1:
                        amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                        spatial_frequency = GABOR_PARAMS["spatial_frequency"] * 0.75 # reduce the spatial frequency of the gabor
                    else:
                        amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                        spatial_frequency = GABOR_PARAMS["spatial_frequency"] # default

                tone = create_puretone(
                    frequency=auditory_freq, duration=STIM_INFO["leading_duration"], amplitude=amplitude
                )
                draw_gabor(visual_ori, screen_info, spatial_frequency=spatial_frequency) # Preload gabor
                draw_fixation(fixation_color, screen_info) # Preload fixation

            elif block_modality == "auditory":
                if target == 1:
                    amplitude = ISOTONIC_SOUNDS[auditory_freq] * 0.2
                else:
                    amplitude = ISOTONIC_SOUNDS[auditory_freq] 
                tone = create_puretone(
                    frequency=auditory_freq, duration=STIM_INFO["leading_duration"], amplitude=amplitude
                )
                draw_fixation(fixation_color, screen_info) # Preload fixation

            else: # visual
                if target == 1:
                    spatial_frequency = GABOR_PARAMS["spatial_frequency"] * 0.75 # reduce the spatial frequency of the gabor
                else:
                    spatial_frequency = GABOR_PARAMS["spatial_frequency"] # default
                    
                tone = create_puretone(
                    frequency=auditory_freq, duration=STIM_INFO["leading_duration"], amplitude=0 # No sound in visual block
                )
                draw_gabor(visual_ori, screen_info, spatial_frequency=spatial_frequency) # Preload gabor
                draw_fixation(fixation_color, screen_info) # Preload fixation
            
            interval.wait()  # Waits for the remaining time of the interval
            
            #play_call_time = trial_clock.time()
            tone.play()  # play the leading tone
            #play_complete_time = trial_clock.time()

            #flip_call_time = trial_clock.time()
            window.flip()  # Flips the window to show the pre-loaded gabor
            #flip_complete_time = trial_clock.time()

            #trigger_send_time = trial_clock.time()
            send_trigger(f"loc_{visual_ori}_{auditory_freq}", context) # send trigger for the leading stimulus
            #trigger_sent_complete_time = trial_clock.time()

            # Print timings immediately for debugging (remove later for real experiments)
            # print(f"Flip Called at {flip_call_time:.6f}s, Flip Completed at {flip_complete_time:.6f}s")
            # print(f"play tone Called at {play_call_time:.6f}s, play tone Completed at {play_complete_time:.6f}s")
            # print(f"Trial {i+1}: Trigger Sent at {trigger_send_time:.6f}s, Trigger Sent Complete at {trigger_sent_complete_time:.6f}s")
            # print(f"Delay from play tone call to play complete: {(play_complete_time - play_call_time)*1000:.2f} ms")
            # print(f"Delay from Flip Call to Flip Complete: {(flip_complete_time - flip_call_time)*1000:.2f} ms")
            # print(f"Delay from completed flip to send trigger call: {(trigger_send_time - flip_complete_time)*1000:.2f} ms")
            # print(f"Delay from completed flip to play complete call: {(play_complete_time - flip_complete_time)*1000:.2f} ms")
            # print(f"Delay from send trigger call to send trigger complete: {(trigger_sent_complete_time - trigger_send_time)*1000:.2f} ms")
            # print("--------------------------------------------------------")

            timestamp_dicts["start_leading"] = trial_clock.time()
            window.wait(STIM_INFO["leading_duration"])  # Waits for the leading duration
            # ======= ISI ========
            interval = Interval(duration=STIM_INFO["isi_duration"])
            interval.reset()
            send_trigger("loc_isi", context) # send trigger for the ISI
            draw_fixation(fixation_color, screen_info)  # draw the fixation dot with feedback color
            window.flip()
            timestamp_dicts["start_isi"] = trial_clock.time()
        
        # ======= Response ========
        timestamp_dicts["start_response"] = trial_clock.time()
        response = localizer_response(window, target_modality, trial["target_count"], context)
        timestamp_dicts["end_trial"] = trial_clock.time()
        block_data.append(
            {
                "num_trial": i,
                "iti_duration": iti_duration,
                **trial,
                **response,
                **timestamp_dicts,
                **screen_info,
                "full_screen": full_screen,
            }
        )

    # Save the block data
    save_block_data(participant_data, block_data, "localizer", block)



def learning_phase(participant_data, block, window, full_screen, screen_info):
    # Instructions
    if block == 1:
        show_instructions(window, INSTRUCTIONS_TEXT["learning_start"], screen_info,)
    else:
        show_instructions(window, INSTRUCTIONS_TEXT["learning_continue"], screen_info,)
   

    conditions = participant_data[f"conditions_learning_{block}"]
    key_mapping = participant_data[f"keymapping_learning_{block}"]
    block_data = []

    for i, trial in enumerate(conditions):
        # Get trigger ids for the current trial type
        trial_type = f"{trial['v_trailing']}_{trial['v_pred']}_{trial['a_trailing']}_{trial['a_pred']}"
        trial_start_trigger =f"{trial_type}_trial_start"
        cue_onset_trigger = f"{trial_type}_cue_onset"
        isi_trigger = f"{trial_type}_isi"
        target_onset_trigger = f"{trial_type}_target_onset"
        response_trigger = f"{trial_type}_response"
        context = f"Trial {i+1}, Block {block}, learning phase" # context for trigger logs

        if i == 0:
            fixation_color = FIXATION_PARAMS["color"]  # set the fixation color. In subsequent trials, the fixation color will be updated based on the response to provide feedback
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
        interval = Interval(duration=iti_duration)  # This allows to init a time counter of duration
        interval.reset()  # This allows to reset the time counter

        send_trigger(trial_start_trigger, context) # send trigger for the start of the trial

        draw_fixation(fixation_color, screen_info)  # draw the fixation dot with feedback color
        window.flip()
        timestamp_dicts["start_fixation"] = trial_clock.time()

        # ======= Leading stimuli ========
        # pre-load stimuli
        fixation_color = FIXATION_PARAMS["color"]  # reset the fixation color to the default color for the ISI
        leading_tone = create_puretone(
            frequency=trial["a_leading"], duration=STIM_INFO["leading_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_leading"]]
        )
        draw_gabor(trial["v_leading"], screen_info)  # initiate the leading gabor,
        draw_fixation(fixation_color, screen_info)  # Preload fixation
        interval.wait()  # Waits for the remaining time of the interval

        # presentation
        leading_tone.play()  # play the leading tone

        draw_cue_call_time = trial_clock.time()
        window.flip()  # Flips the window to show the pre-loaded gabor
        draw_cue_complete_time = trial_clock.time()

        cue_trigger_send_time = trial_clock.time()
        send_trigger(cue_onset_trigger, context) # send trigger for the leading stimulus
        cue_trigger_complete_time = trial_clock.time()

        timestamp_dicts["start_leading"] = trial_clock.time()
        window.wait(STIM_INFO["leading_duration"])  # Waits for the leading duration
        draw_finished_time = trial_clock.time()
        # ======= ISI ========
        interval = Interval(duration=STIM_INFO["isi_duration"])
        interval.reset()
        isi_interval_reset_time = trial_clock.time()

        isi_trigger_send_time = trial_clock.time()
        send_trigger(isi_trigger, context) # send trigger for the ISI)
        isi_trigger_complete_time = trial_clock.time()

        draw_fixation(fixation_color, screen_info)
        window.flip()
        timestamp_dicts["start_isi"] = trial_clock.time()

        # ======= Trailing stimuli ========
        # pre-load stimuli
        trailing_tone = create_puretone(
            frequency=trial["a_trailing"], duration=STIM_INFO["target_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_trailing"]]
        )
        draw_gabor(trial["v_trailing"], screen_info)
        draw_fixation(fixation_color, screen_info)
        interval.wait()
        isi_interval_complete_time = trial_clock.time()

        # presentation
        trailing_tone.play()
        
        draw_target_call_time = trial_clock.time()
        window.flip()  # Flips the window to show the pre-loaded gabor
        draw_target_complete_time = trial_clock.time()

        target_trigger_send_time = trial_clock.time()
        send_trigger(target_onset_trigger, context) # send trigger for the trailing stimulus
        target_trigger_complete_time = trial_clock.time()

        timestamp_dicts["start_trailing"] = trial_clock.time()
        window.wait(STIM_INFO["target_duration"])

        # print(f"cue presentation - trigger delay: {(draw_cue_complete_time - draw_cue_complete_time)*1000:.2f} ms")
        # print(f"ISI delay: {(isi_interval_complete_time - isi_interval_reset_time)*1000:.2f} ms")
        # print(f"target presentation - trigger delay: {(draw_target_complete_time - target_trigger_send_time)*1000:.2f} ms")
        # print(f"target draw - target finish: {(draw_finished_time - draw_cue_complete_time)*1000:.2f} ms")

        # ======= Response ========
        timestamp_dicts["start_response"] = trial_clock.time()
        response = learning_response(window, key_mapping, trial, response_trigger, context)
        timestamp_dicts["end_trial"] = trial_clock.time()
        block_data.append(
            {
                "num_trial": i,
                "iti_duration": iti_duration,
                **trial,
                **response,
                **timestamp_dicts,
                **screen_info,
                "full_screen": full_screen,
            }
        )
    # Save the block data
    save_block_data(participant_data, block_data, "learning", block)




def test_phase(participant_data, block, window, full_screen, screen_info):
    # Instructions
    if block == 1:
        show_instructions(window, INSTRUCTIONS_TEXT["test_start"], screen_info,)
    else:
        remaining_blocks = PHASES["test_blocks"] - block + 1
        show_instructions(window, INSTRUCTIONS_TEXT["test_continue"], screen_info,block=block, remaining_blocks=remaining_blocks)
   
    conditions = participant_data[f"conditions_test_{block}"]
    key_mapping = participant_data[f"keymapping_test_{block}"]
    block_data = []

    for i, trial in enumerate(conditions):
        # Get trigger ids for the current trial type
        trial_type = f"{trial['v_trailing']}_{trial['v_pred']}_{trial['a_trailing']}_{trial['a_pred']}"
        trial_start_trigger =f"{trial_type}_trial_start"
        cue_onset_trigger = f"{trial_type}_cue_onset"
        isi_trigger = f"{trial_type}_isi"
        target_onset_trigger = f"{trial_type}_target_onset"
        response_trigger = f"{trial_type}_response"
        context = f"Trial {i+1}, Block {block}, test phase" # context for trigger logs

        if i == 0: # first trial of the block
            fixation_color = FIXATION_PARAMS["color"]  # set the fixation color. In subsequent trials, the fixation color will be updated based on the response to provide feedback

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

        send_trigger(trial_start_trigger, context) # send trigger for the start of the trial

        draw_fixation(fixation_color, screen_info)  # draw the fixation dot with feedback color
        window.flip()
        timestamp_dicts["start_fixation"] = trial_clock.time()

        # ======= Leding stimuli ========
        # pre-load stimuli
        fixation_color = FIXATION_PARAMS["color"]  # reset the fixation color to the default color for the ISI
        leading_tone = create_puretone(
            frequency=trial["a_leading"], duration=STIM_INFO["leading_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_leading"]]
            )
        draw_gabor(trial["v_leading"], screen_info)  # initiate the leading gabor,
        draw_fixation(fixation_color, screen_info)  # Preload fixation
        interval.wait()  # Waits for the remaining time of the interval

        # presentation
        leading_tone.play()  # play the leading tone
        window.flip()  # Flips the window to show the pre-loaded gabor
        send_trigger(cue_onset_trigger, context) # send trigger for the leading stimulus
        
        timestamp_dicts["start_leading"] = trial_clock.time()
        window.wait(STIM_INFO["leading_duration"])  # Waits for the leading duration

        # ======= ISI ========
        interval = Interval(duration=STIM_INFO["isi_duration"])
        interval.reset()

        send_trigger(isi_trigger, context) # send trigger for the ISI)
        draw_fixation(fixation_color, screen_info)
        window.flip()
        
        timestamp_dicts["start_isi"] = trial_clock.time()

        # ======= Trailing stimuli ========
        # pre-load stimuli
        trailing_tone = create_puretone(frequency=trial["a_trailing"], duration=STIM_INFO["target_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_trailing"]])
        if trial["target"] == 0:
            current_ori_diff = 0
        else: # in target trials we add a random orientation difference to the trailing gabor
            current_ori_diff = staircase_data["ori_diff"]
            current_ori_diff = random.choice([-current_ori_diff, current_ori_diff])

        draw_gabor(trial["v_trailing"] + current_ori_diff, screen_info)  # draw the trailing gabor
        draw_fixation(fixation_color, screen_info)  # Preload fixation
        interval.wait()

        # presentation
        trailing_tone.play()
        window.flip()
        send_trigger(target_onset_trigger, context) # send trigger for the trailing stimulus
        timestamp_dicts["start_trailing"] = trial_clock.time()
        window.wait(STIM_INFO["target_duration"])

        # ======= Response ========
        timestamp_dicts["start_response"] = trial_clock.time()
        response = test_response(window, key_mapping, trial, response_trigger, context)
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
                **screen_info,
                "full_screen": full_screen,
            }
        )


    # Save the block data
    save_block_data(participant_data, block_data, "test", block)



def explicit_phase(participant_data, block, window, full_screen, screen_info):
    conditions = participant_data[f"conditions_explicit_{block}"]
    key_mapping = participant_data[f"keymapping_explicit_{block}"]
    block_data = []

    # Instructions
    if conditions[0]["modality"] == "auditory":
        show_instructions(window, INSTRUCTIONS_TEXT["explicit_phase"], screen_info, modality_task="noticed that some sounds were also paired more frequently than others.", modality_verb="hear", modality="an auditory")
    else: # visual
        show_instructions(window, INSTRUCTIONS_TEXT["explicit_phase"], screen_info, modality_task="can remember the visual pairs that you learned at the start of the experiment.", modality_verb="see", modality="a visual")

    for i, trial in enumerate(conditions):
        # Get trigger ids for the current trial type
        if trial["modality"] == "auditory":
            trial_type = f"explicit_{trial['a_trailing']}_{trial['a_pred']}"
            context = f"Trial {i+1}, Block {block} (auditory), explicit phase" # context for trigger logs
        else:
            trial_type = f"explicit_{trial['v_trailing']}_{trial['v_pred']}"
            context = f"Trial {i+1}, Block {block} (visual), explicit phase" # context for trigger logs
        
        if i == 0:
            fixation_color = FIXATION_PARAMS["color"]  # set the fixation color. In subsequent trials, in this phase there is no feedback so it won't be updated
        
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

        send_trigger(f"{trial_type}_trial_start", context) # send trigger for the start of the triall

        draw_fixation(fixation_color, screen_info)  # draw the fixation dot with feedback color
        window.flip()
        timestamp_dicts["start_fixation"] = trial_clock.time()
        # ======= Leding stimuli ========
        # pre-load stimuli
        if trial["modality"] == "auditory":
            leading_tone = create_puretone(
                frequency=trial["a_leading"], duration=STIM_INFO["leading_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_leading"]]
            )
            draw_fixation(fixation_color, screen_info)
        else:
            draw_gabor(trial["v_leading"], screen_info)  # initiate the leading gabor,
            draw_fixation(fixation_color, screen_info)
        interval.wait()  

        # presentation
        if trial["modality"] == "auditory": leading_tone.play()  # play the leading tone only in auditory block
        window.flip()  # Flips the window to show the pre-loaded gabor and fixation
        send_trigger(f"{trial_type}_cue_onset", context) # send trigger for the leading stimulus
        timestamp_dicts["start_leading"] = trial_clock.time()
        window.wait(STIM_INFO["leading_duration"])  # Waits for the leading duration

        # ======= ISI ========
        interval = Interval(duration=STIM_INFO["isi_duration"])
        interval.reset()

        send_trigger(f"{trial_type}_isi", context) # send trigger for the ISI)
        draw_fixation(fixation_color, screen_info)
        window.flip()
        
        timestamp_dicts["start_isi"] = trial_clock.time()
        # ======= Trailing stimuli ========
        # pre-load stimuli
        if trial["modality"] == "auditory":
            draw_fixation(fixation_color, screen_info)
            trailing_tone = create_puretone(
                frequency=trial["a_trailing"], duration=STIM_INFO["target_duration"], amplitude=ISOTONIC_SOUNDS[trial["a_trailing"]]
            )
        else:
            draw_gabor(trial["v_trailing"], screen_info)
            draw_fixation(fixation_color, screen_info)
        interval.wait()

        # presentation
        if trial["modality"] == "auditory": trailing_tone.play()  # play the leading tone only in auditory block
        window.flip()
        send_trigger(f"{trial_type}_target_onset", context) # send trigger for the trailing stimulus
        timestamp_dicts["start_trailing"] = trial_clock.time()
        window.wait(STIM_INFO["target_duration"])

        # ======= Response ========
        timestamp_dicts["start_response"] = trial_clock.time()
        response = explicit_response(window, key_mapping, trial, f"{trial_type}_response", f"{trial_type}_confidence", context)
        timestamp_dicts["end_trial"] = trial_clock.time()
        block_data.append(
            {
                "num_trial": i,
                "iti_duration": iti_duration,
                **trial,
                **response,
                **timestamp_dicts,
                **screen_info,
                "full_screen": full_screen,
            }
        )
    # Save the block data
    save_block_data(participant_data, block_data, "explicit", block)


def run_phase(phase, block, window, participant_data, full_screen, screen_info):
    """
    dispatcher function to run the different phases of the experiment
    """
    if phase == "localizer":
        localizer_phase(participant_data, block, window, full_screen, screen_info)
    elif phase == "learning":
        learning_phase(participant_data, block, window, full_screen, screen_info)
    elif phase == "test":
        test_phase(participant_data, block, window, full_screen, screen_info)
    elif phase == "explicit":
        explicit_phase(participant_data, block, window, full_screen, screen_info)
