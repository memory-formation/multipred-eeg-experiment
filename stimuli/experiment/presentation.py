from experiment.constants import (
    COLOR,
    INSTRUCTIONS_FONT_SIZE,
    FIXATION_FONT_SIZE,
    RESPONSE_FONT_SIZE,
    GABOR_SIZE,
)
from psychos.visual import Text, Image, Gabor
from psychos.sound import Sine
from psychos.core import Clock


def show_instructions(window, text):
    if isinstance(text, str):
        text = [text]

    text_widget = Text(font_size=INSTRUCTIONS_FONT_SIZE, color=COLOR)
    for line in text:
        text_widget.text = line
        text_widget.draw()
        window.flip()
        key_event = window.wait_key()


def draw_fixation(fixation_color):
    text_widget = Text(font_size=FIXATION_FONT_SIZE, color=fixation_color)
    text_widget.text = "o"
    text_widget.draw()


def draw_gabor(orientation):
    # Here as a dummy we show the fixed image instead of use the visual lead

    if orientation == "neutralV":
        image = Image("images/eye.png", width="30vw", height="30vw")

    else:  # gabor
        image = Gabor(
            orientation=orientation,
            width=GABOR_SIZE,
            height=GABOR_SIZE,
            spatial_frequency=10,
            )
        
    image.draw()



def create_puretone(frequency, duration=0.5):

    if frequency == "neutralA":
        frequency = 440

    puretone = Sine(
        duration=duration,
        frequency=int(frequency),
    )
    return puretone


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