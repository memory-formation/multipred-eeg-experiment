import json
import os

from experiment.constants import COLOR, RESPONSE_FONT_SIZE
from psychos.core import Clock
from psychos.visual import Text


def learning_response(window, key_mapping, trial):

    text_widget = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR)
    text_widget.text = f"< {key_mapping['LEFT']}    neutral    {key_mapping['RIGHT']} >"
    text_widget.draw()
    clock = Clock()  # This allows to init a clock to measure the RT
    window.flip()
    clock.reset()  # This allows to reset the clock
    key_event = window.wait_key(["SPACE", "LEFT", "RIGHT"], clock=clock, max_wait=2)
    reaction_time = key_event.timestamp
    pressed_key = key_event.key

    if pressed_key is None:
        outcome = 0
        fixation_color = "red"
    else:
        correct_conditions = (
            (key_mapping[pressed_key] == "neutral" and trial["v_pred"] == "neutral")
            or (key_mapping[pressed_key] != "frequent" and trial["v_pred"] == "EXP")
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

def test_response(window, key_mapping, trial):

    text_widget = Text(font_size=RESPONSE_FONT_SIZE, color=COLOR)
    text_widget.text = f"< {key_mapping['LEFT']}            {key_mapping['RIGHT']} >"
    text_widget.draw()
    clock = Clock()  # This allows to init a clock to measure the RT
    window.flip()
    clock.reset()  # This allows to reset the clock
    key_event = window.wait_key(["LEFT", "RIGHT"], clock=clock, max_wait=2)
    reaction_time = key_event.timestamp
    pressed_key = key_event.key

    if pressed_key is None:
        outcome = 0
        fixation_color = "red"
    else:
        correct_conditions = (
            (key_mapping[pressed_key] == "normal" and trial["target"] == 0)
            or (key_mapping[pressed_key] == "deviant" and trial["target"] == 1)
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

# def staircase_response(last_outcome, ):
#     """
#     Adapative staircase procedure to adapt the difficulty of the task to the participant's performance.
#     After three correct responses, the orientation difference (ori_diff) is decreased (more difficult).
#     After one incorrect response, the orientation difference is increased (easier).
#     3 up 1 down rule aims at a threshold of ~80% correct responses.
#     """
#     if last_outcome == 1:
#         return current_stimulus
#     else:
#         return last_stimulus
    
# # Initial values for each separate adaptive staircase 
# # Visual 
# v_diff = 20; v_hist = 1; v_inv = 0; v_lastdir = "down"
# vstep = [6, 4, 2, 1]
# vstep_update = [2, 4, 8] 
# ori_diff = 


# def staircase(last_outcome, ori_diff, stepsize, history, last_dir, n_inv, step, step_update):
#     """
#     Adapative staircase procedure to adapt the difficulty of the task to the participant's performance.
#     After three correct responses, the orientation difference (ori_diff) is decreased (more difficult).
#     After one incorrect response, the orientation difference is increased (easier).
#     3 up 1 down rule aims at a threshold of ~80% correct responses.
#     ori_diff: current orientation difference
#     stepsize: How much to increase/decrease the orientation difference
#     history: How many consecutive correct responses
#     last_dir: last direction of the staircase (up or down)
#     """
#     if n_inv < step_update[0]: stepsize = step[0]
#     elif n_inv >=step_update[0] and n_inv < step_update[1]: stepsize = step[1]
#     elif n_inv >= step_update[1] and n_inv < step_update[2]: stepsize = step[2]
#     else: stepsize = step[3]
        
#     if last_outcome == 0: 
#         if diff + stepsize <= 40: 
#             diff += stepsize #If last target was incorrect increase diff
#             history = 0
#             if last_dir == "down": n_inv += 1
#             last_dir = "up"
#         else:
#             diff = diff
#     else:
#         history += 1
#         if history == 3:
#             history = 0 # If 3 consecutive correct response restart count
#             diff -= stepsize # and drecrease diff
#             if last_dir == "up": n_inv += 1 
#             last_dir = "down"
#         else: # history == 1 or 2
#             history = history  
#             diff = diff #remains the same
#             last_dir = last_dir
        
#     return diff, history, last_dir, n_inv





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
            json.dump([block_data], f)

    print(f"Block data saved to {out_path}")