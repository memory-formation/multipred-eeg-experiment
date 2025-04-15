import json
import os

from experiment.constants import COLOR, RESPONSE_FONT_SIZE, DATA_FOLDER
from experiment.triggers import send_trigger
from psychos.core import Clock
from psychos.visual import Text


def localizer_response(window, target_modality, target_count, context):
    text_widget = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR)
    if target_modality == "visual":
        text_widget.text = f"How many targets did you see?"
    else: # target_modality == "auditory":
        text_widget.text = f"How many weaker sounds did you hear?"

    text_widget.draw()
    clock = Clock()  # This allows to init a clock to measure the RT
    window.flip()
    clock.reset()  # This allows to reset the clock
    key_event = window.wait_key(["1", "2", "3", "4", "5", "6", "7", "8", "9"], clock=clock, max_wait=2)
    send_trigger("loc_response", context)  # Send the response trigger
    reaction_time = key_event.timestamp
    pressed_key = key_event.key

    if pressed_key is None:
        if target_count != 0: # at least one target
            outcome = 0
            fixation_color = "red"
        else: 
            outcome = 1
            fixation_color = "green"
    else:
        if  target_count == int(pressed_key): # if the number of targets is equal to the number pressed
            outcome = 1
            fixation_color = "green"
        else: 
            outcome = 0
            fixation_color = "red"
    return {
        "pressed_key": pressed_key,
        "outcome": outcome,
        "response": pressed_key,
        "fixation_color": fixation_color,
        "reaction_time": reaction_time,
        "timeout": pressed_key is None,
    }


def learning_response(window, key_mapping, trial, response_trigger, context):
    text_widget = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR)
    text_widget.text = f"< {key_mapping['LEFT']}    neutral    {key_mapping['RIGHT']} >"
    text_widget.draw()
    clock = Clock()  # This allows to init a clock to measure the RT
    window.flip()
    clock.reset()  # This allows to reset the clock
    key_event = window.wait_key(["SPACE", "LEFT", "RIGHT"], clock=clock, max_wait=2)
    send_trigger(response_trigger, context)  # Send the response trigger
    reaction_time = key_event.timestamp
    pressed_key = key_event.key

    if pressed_key is None:
        outcome = 0
        fixation_color = "red"
    else:
        correct_conditions = (
            (key_mapping[pressed_key] == "neutral" and trial["v_pred"] == "neutral")
            or (key_mapping[pressed_key] == "frequent" and trial["v_pred"] == "EXP")
            or (key_mapping[pressed_key] == "infrequent" and trial["v_pred"] == "UEX")
        )

        outcome = 1 if correct_conditions else 0  # saving the outcome of the trial
        fixation_color = (
            "green" if outcome else "red"
        )  # setting the fixation color based on the outcome to provide visual feedback

    return {
        "pressed_key": pressed_key,
        "outcome": outcome,
        "response": key_mapping.get(pressed_key, "NA"),
        "fixation_color": fixation_color,
        "reaction_time": reaction_time,
        "timeout": pressed_key is None,
    }


def test_response(window, key_mapping, trial, response_trigger, context):

    text_widget = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR)
    text_widget.text = f"< {key_mapping['LEFT']}            {key_mapping['RIGHT']} >"
    text_widget.draw()
    clock = Clock()  # This allows to init a clock to measure the RT
    window.flip()
    clock.reset()  # This allows to reset the clock
    key_event = window.wait_key(["LEFT", "RIGHT"], clock=clock, max_wait=2)
    send_trigger(response_trigger, context)  # Send the response trigger
    reaction_time = key_event.timestamp
    pressed_key = key_event.key

    if pressed_key is None:
        outcome = 0
        fixation_color = "red"
    else:
        correct_conditions = (
            key_mapping[pressed_key] == "normal" and trial["target"] == 0
        ) or (key_mapping[pressed_key] == "deviant" and trial["target"] == 1)

        outcome = 1 if correct_conditions else 0  # saving the outcome of the trial
        fixation_color = (
            "green" if outcome else "red"
        )  # setting the fixation color based on the outcome to provide visual feedback

    return {
        "pressed_key": pressed_key,
        "outcome": outcome,
        "response": key_mapping.get(pressed_key, "NA"),
        "fixation_color": fixation_color,
        "reaction_time": reaction_time,
        "timeout": pressed_key is None,
    }


def explicit_response(window, key_mapping, trial, response_trigger, confidence_trigger, context):

    text_widget = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR)
    text_widget.text = f"< {key_mapping['LEFT']}            {key_mapping['RIGHT']} >"
    text_widget.draw()
    clock = Clock()  # This allows to init a clock to measure the RT
    window.flip()
    clock.reset()  # This allows to reset the clock
    key_event1 = window.wait_key(["LEFT", "RIGHT"], clock=clock, max_wait=60)
    send_trigger(response_trigger, context)  # Send the response trigger
    reaction_time = key_event1.timestamp
    pressed_key1 = key_event1.key if key_event1 else None
    response = key_mapping.get(pressed_key1, "NA")
    modality = trial["modality"]

    if pressed_key1 is None:
        outcome = 0
    else:
        if modality == "visual":
            # Check if the response is correct based on the visual modality
            correct_conditions = (
                response == "frequent" and trial["v_pred"] == "EXP"
            ) or (response == "infrequent" and trial["v_pred"] == "UEX")
        else:  # auditory
            # Check if the response is correct based on the auditory modality
            correct_conditions = (
                response == "frequent" and trial["a_pred"] == "EXP"
            ) or (response == "infrequent" and trial["a_pred"] == "UEX")

        outcome = 1 if correct_conditions else 0  # saving the outcome of the trial

    # Confidence rating
    if response != "NA":
        # Display the confidence rating question
        question_text = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR, position=(0, .2))
        question_text.text = "How confident are you in your response?"
        rating1_text = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR, position=(-.5, -.2))
        rating1_text.text = "1: not at all"
        rating2_text = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR, position=(-.25, -.2))
        rating2_text.text = "2: a little"
        rating3_text = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR, position=(0, -.2))
        rating3_text.text = "3: moderately"
        rating4_text = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR, position=(.25, -.2)) 
        rating4_text.text = "4: very"
        rating5_text = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR, position=(.5, -.2))
        rating5_text.text = "5: completely"
        question_text.draw()
        rating1_text.draw()
        rating2_text.draw()
        rating3_text.draw()
        rating4_text.draw()
        rating5_text.draw()
        window.flip()
        clock.reset()  # Reset the clock for the confidence rating
        key_event2 = window.wait_key(["1", "2", "3", "4", "5"], clock=clock, max_wait=60)
        send_trigger(confidence_trigger, context)  # Send the confidence trigger
        confidence = key_event2.key if key_event2 else None
        confidence_RT = key_event2.timestamp 

    return {  # returning the response data
        "pressed_key1": pressed_key1,
        "outcome": outcome,
        "response": response,
        "reaction_time": reaction_time,
        "confidence": confidence,
        "confidence_RT": confidence_RT,
        "timeout": pressed_key1 is None,
    }



def staircase(last_outcome, ori_diff, inversions_count, last_direction, history, step_size, step_size_list, step_update, max_diff):
    """
    Adapative staircase procedure to adapt the difficulty of the task to the participant's performance.
    After three correct responses, the orientation difference (ori_diff) is decreased (more difficult).
    After one incorrect response, the orientation difference is increased (easier).
    3 up 1 down rule aims at a threshold of ~80% correct responses.
    last_outcome: outcome of the last trial (0 or 1)
    ori_diff: current orientation difference
    inversions_count: number of times the staircase has changed direction
    last_direction: last direction of the staircase (up or down)
    history: number of consecutive correct responses
    step_size: current step size
    step_size_list: list of step sizes to use for the staircase
    step_update: list of step sizes to use for the staircase
    """


    if inversions_count < step_update[0]:
        step_size = step_size_list[0]
    elif inversions_count >= step_update[0] and inversions_count < step_update[1]:
        step_size = step_size_list[1]
    elif inversions_count >= step_update[1] and inversions_count < step_update[2]:
        step_size = step_size_list[2]
    else:
        step_size = step_size_list[3]

    if last_outcome == 0:
        if ori_diff + step_size <= max_diff: # Check if the new ori_diff is within the allowed range
            ori_diff += step_size  # If last target was incorrect increase ori_diff
            history = 0
            if last_direction == "down":
                inversions_count += 1
            last_direction = "up"
        else:
            ori_diff = max_diff  # If the new ori_diff is greater than max_diff, set it to max_diff
    else:
        history += 1
        if history == 3:
            history = 0  # If 3 consecutive correct response restart count
            ori_diff -= step_size  # and drecrease ori_diff
            if last_direction == "up":
                inversions_count += 1
            last_direction = "down"
        else:  # history == 1 or 2
            history = history
            ori_diff = ori_diff  # remains the same
            last_direction = last_direction

    staircase_data = { # Intiial values for the staircase, same for all partiicpants bu updated during the experiment
        "ori_diff": ori_diff, # initial value of orientation difference
        "inversions_count": inversions_count, # How many times the staircase has changed direction, from increasing to decreasing or vice versa
        "last_direction" : last_direction, # Last direction of the staircase
        "history": history, # How many consecutive trials have been correct before this one
        "step_size": step_size, # How much to increase/decrease the orientation difference. Just saving it for storage
    }
  
    return staircase_data


def load_last_staircase_data(participant_data, block):
    """
    Loads staircase_data from the final trial of the previous block.
    """
    participant_id = participant_data["participant_id"]
    prev_block = block - 1
    filepath = f"data/{participant_id}/test_block{prev_block}.json"

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            block_trials = json.load(f)
        last_trial = block_trials[-1] #[0]  # Get the final trial of previous block

        staircase_data = {
            "ori_diff": last_trial["ori_diff"],
            "inversions_count": last_trial["inversions_count"],
            "last_direction": last_trial["last_direction"],
            "history": last_trial["history"],
            "step_size": last_trial["step_size"],
        }

        return staircase_data
    else:
        raise FileNotFoundError(f"No previous block data found at: {filepath}")
    


def save_block_data(participant_data, block_data, phase, block):
    """
    Save the data of the block in the participant data directory as a json file
    If file already exists, and contains data from previous blocks append the data to the existing json
    """
    out_path = f"data/{participant_data['participant_id']}/{phase}_block{block}.json"
    if os.path.exists(out_path):
        with open(out_path, "r") as f:
            data = json.load(f)
            data.append(block_data)
        with open(out_path, "w") as f:
            json.dump(data, f)
    else:
        with open(out_path, "w") as f:
            json.dump(block_data, f)

    print(f"Block data saved to {out_path}")

    # Update completed_blocks tracker in participant_data
    completed = participant_data.setdefault("completed_blocks", {
        "localizer": [],
        "learning": [],
        "test": [],
        "explicit": []
    })
    if block not in completed[phase]:
        completed[phase].append(block)

    # Save updated participant_data back to disk
    participant_data_path = f"{DATA_FOLDER}/{participant_data['participant_id']}/{participant_data["participant_id"]}_info.json"
    with open(participant_data_path, "w") as f:
        json.dump(participant_data, f, indent=4)
