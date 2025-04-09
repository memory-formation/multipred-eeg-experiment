import numpy as np
from experiment.constants import (COLOR, FIXATION_FONT_SIZE, GABOR_PARAMS,
                                  INSTRUCTIONS_FONT_SIZE)
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


def visual_angle_to_pixels(angle_deg, distance_cm, screen_width_cm, screen_width_px):
    # Convert angle to radians
    angle_rad = np.deg2rad(angle_deg)
    
    # Calculate physical size on screen in cm
    size_cm = 2 * distance_cm * np.tan(angle_rad / 2)
    
    # Calculate pixels/cm ratio
    px_per_cm = screen_width_px / screen_width_cm
    
    # Convert physical size to pixels
    size_px = size_cm * px_per_cm

    spatial_frequency = GABOR_PARAMS["spatial_frequency"] * angle_deg  # Adjust spatial frequency based on size

    return int(round(size_px)), spatial_frequency



def generate_neutral_gabor(screen_info):
    if GABOR_PARAMS["units"] == "deg":
        size, spatial_frequency = visual_angle_to_pixels(GABOR_PARAMS["size"], screen_info["distance_cm"], screen_info["screen_width_cm"], screen_info["screen_width_px"])
    else:
        size = 256 # default to percentage of screen width
        spatial_frequency = 20  # Adjust spatial frequency based on size
  
    data_0 = 255 * gabor_3d(
        size=(256, 256), spatial_frequency=spatial_frequency, orientation=0, contrast=0.5
    )
    data_90 = 255 * gabor_3d(
        size=(256, 256), spatial_frequency=spatial_frequency, orientation=90, contrast=0.5
    )
    data_neutral = 0.5 * (data_0 + data_90)
    data_neutral = data_neutral.astype("uint8")
    image = RawImage(
        raw_image=data_neutral,
        width=size,
        height=size,
    )

    return image




def draw_gabor(orientation, screen_info, contrast=None):
    if contrast is None:
        contrast = GABOR_PARAMS["contrast"]

    if GABOR_PARAMS["units"] == "deg":
        size, spatial_frequency = visual_angle_to_pixels(GABOR_PARAMS["size"], screen_info["distance_cm"], screen_info["screen_width_cm"], screen_info["screen_width_px"])
    else:
        size = "50vw" # default to percentage of screen width
        spatial_frequency = 20  # Adjust spatial frequency based on size

    if orientation == "neutralV":
        image = generate_neutral_gabor(screen_info)
        image.draw()

    else:  # gabor
        image = Gabor(
            orientation=orientation,
            width=size,
            height=size,
            spatial_frequency=spatial_frequency,
            contrast=contrast,
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
