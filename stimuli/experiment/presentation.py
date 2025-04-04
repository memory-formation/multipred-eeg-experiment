from experiment.constants import (COLOR, FIXATION_FONT_SIZE, GABOR_PARAMS,
                                  GABOR_SIZE, INSTRUCTIONS_FONT_SIZE)
from psychos.core import Clock
from psychos.sound import FlatEnvelope, Sine
from psychos.visual import Gabor, Image, RawImage, Text
from psychos.visual.synthetic import gabor_3d


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


def generate_neutral_gabor():
    size = (256, 256)
    data_0 = 255 * gabor_3d(
        size=size, spatial_frequency=GABOR_PARAMS["spatial_frequency"], orientation=0, contrast=0.5
    )
    data_90 = 255 * gabor_3d(
        size=size, spatial_frequency=GABOR_PARAMS["spatial_frequency"], orientation=90, contrast=0.5
    )
    data_neutral = 0.5 * (data_0 + data_90)
    data_neutral = data_neutral.astype("uint8")
    image = RawImage(
        raw_image=data_neutral,
        width=GABOR_SIZE,
        height=GABOR_SIZE,
    )

    return image


def draw_gabor(orientation):

    if orientation == "neutralV":
    #     image = Image("images/eye.png", width="30vw", height="30vw")
    #     image1 = Gabor(
    #         orientation=0,
    #         width=GABOR_SIZE,
    #         height=GABOR_SIZE,
    #         spatial_frequency=GABOR_PARAMS["spatial_frequency"],
    #         contrast=0.5,
    #     )
    #     image2 = Gabor(
    #         orientation=90,
    #         width=GABOR_SIZE,
    #         height=GABOR_SIZE,
    #         spatial_frequency=GABOR_PARAMS["spatial_frequency"],
    #         contrast=0.5,
    #     )

    #     image1.draw()
    #     image2.draw()

        image = generate_neutral_gabor()
        image.draw()

    else:  # gabor
        image = Gabor(
            orientation=orientation,
            width=GABOR_SIZE,
            height=GABOR_SIZE,
            spatial_frequency=GABOR_PARAMS["spatial_frequency"],
        )

        image.draw()
        


def create_puretone(frequency, duration=0.5, amplitude=1):
    """
    Create a puretone sound stimulus.
    :param frequency: Frequency of the puretone in Hz.
    :param duration: Duration of the puretone in seconds.
    :return: A Sine object representing the puretone.
    """
    envelope = FlatEnvelope(
        amplitude=amplitude,
    )
    puretone = Sine(
        duration=duration,
        frequency=int(frequency),
        envelope=envelope,
    )
    return puretone
