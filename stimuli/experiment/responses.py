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