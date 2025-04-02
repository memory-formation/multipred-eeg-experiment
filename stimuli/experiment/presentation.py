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
