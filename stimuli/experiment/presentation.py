import numpy as np
from experiment.constants import (COLOR, FIXATION_FONT_SIZE, GABOR_PARAMS,
                                  INSTRUCTIONS_FONT_SIZE, FIXATION_PARAMS)
from psychos.core import Clock
from psychos.sound import FlatEnvelope, Sine
from psychos.visual import Gabor, Image, RawImage, Text, Circle
from psychos.visual.synthetic import gabor_3d, gabor_2d


def show_instructions(window, text, **kwargs):
    if isinstance(text, str):
        text = [text]

    # format the text if it contains placeholders
    text = [line.format(**kwargs) for line in text]

    text_widget = Text(font_size=INSTRUCTIONS_FONT_SIZE, color=COLOR)
    for line in text:
        text_widget.text = line
        text_widget.draw()
        window.flip()
        window.wait_key(["SPACE"])


def visual_angle_to_pixels(angle_deg, distance_cm, screen_width_cm, screen_width_px, sf=None):
    """
    Convert visual angle in degrees to pixels on the screen.
    :param angle_deg: Visual angle in degrees.
    :param distance_cm: Distance from the observer to the screen in cm.
    :param screen_width_cm: Width of the screen in cm.
    :param screen_width_px: Width of the screen in pixels.
    :param spatial_frequency: Spatial frequency in cycles per degree. If none it defaults to constant (2.4 cpd)
    """
    if sf is None:
        sf = GABOR_PARAMS["spatial_frequency"]

    # Convert angle to radians
    angle_rad = np.deg2rad(angle_deg)
    
    # Calculate physical size on screen in cm
    size_cm = 2 * distance_cm * np.tan(angle_rad / 2)
    
    # Calculate pixels/cm ratio
    px_per_cm = screen_width_px / screen_width_cm
    
    # Convert physical size to pixels
    size_px = size_cm * px_per_cm

    spatial_frequency = sf * angle_deg  # Adjust spatial frequency based on size

    return int(round(size_px)), spatial_frequency

def generate_neutral_gabor(screen_info, luminance_gain=1.0):
    if GABOR_PARAMS["units"] == "deg":
        size, spatial_frequency = visual_angle_to_pixels(
            GABOR_PARAMS["size"], screen_info["distance_cm"], screen_info["screen_width_cm"], screen_info["screen_width_px"]
            )
    else:
        size = 256 # default to percentage of screen width
        spatial_frequency = 20  # Adjust spatial frequency based on size
  
    data_0 = 255 * gabor_3d(
        size=(256, 256), spatial_frequency=spatial_frequency, orientation=0, contrast=1
    )
    data_90 = 255 * gabor_3d(
        size=(256, 256), spatial_frequency=spatial_frequency, orientation=90, contrast=1
    )
    data_neutral = 0.5 * (data_0 + data_90)
    data_neutral[..., :3] *= luminance_gain  # Only apply luminance to RGB channels
    # Clip only RGB channels (alpha left as-is) otherwise when increasing luminance above 255 they will loop back to 0
    data_neutral[..., :3] = np.clip(data_neutral[..., :3], 0, 255)

    data_neutral = data_neutral.astype("uint8")
    print("Mean luminance - G0:", np.mean(data_0), "Neutral:", np.mean(data_neutral))
    image = RawImage(
        raw_image=data_neutral,
        width=size,
        height=size,
    )

    return image 



def draw_gabor(orientation, screen_info, contrast=None, spatial_frequency=None, **kwargs):
    """
    Draw a Gabor patch on the screen.
    :param orientation: Orientation of the Gabor in degrees.
    :param screen_info: Dictionary containing screen information (distance, width, etc.).
    :param contrast: Contrast of the Gabor. If None, it will use the default from GABOR_PARAMS.
    :param spatial_frequency: Spatial frequency of the Gabor. If None, it will use the default from GABOR_PARAMS.
    """

    if contrast is None:
        contrast = GABOR_PARAMS["contrast"]

    if GABOR_PARAMS["units"] == "deg":
        size, spatial_frequency = visual_angle_to_pixels(
            GABOR_PARAMS["size"], screen_info["distance_cm"], screen_info["screen_width_cm"], screen_info["screen_width_px"], spatial_frequency
            )
    else:
        size = "50vw" # default to percentage of screen width
        spatial_frequency = 20  # Adjust spatial frequency based on size

    if orientation == "neutralV":
        image = generate_neutral_gabor(screen_info, **kwargs)
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
        
def draw_fixation(fixation_color, screen_info, radius=FIXATION_PARAMS["radius"]):
    """
    Draw a fixation dot on the screen.
    :param fixation_color: Color of the fixation dot.
    :param radius: Radius of the fixation dot in visual degrees, is converted to pixels.
    """
    # Convert radius from degrees to pixels
    size, _ = visual_angle_to_pixels(
            radius, screen_info["distance_cm"], screen_info["screen_width_cm"], screen_info["screen_width_px"]
            )
    fixation = Circle(color=fixation_color, radius=size)
    fixation.draw()

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
