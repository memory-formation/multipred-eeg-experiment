from psychos import Window
from experiment.constants import BACKGROUND_COLOR, GABOR_PARAMS, SCREENS, COLOR, FIXATION_PARAMS
from experiment.presentation import draw_gabor, draw_fixation

from psychos.visual import Text

full_screen = "Yes"  # This should be set based on the user's choice or the environment
screen_info = SCREENS["hp_laptop"]
fixation_color = FIXATION_PARAMS["color"]
window = Window(background_color=BACKGROUND_COLOR, fullscreen=full_screen == "Yes", coordinates="px")

draw_gabor(0, screen_info, spatial_frequency=0.7)
draw_fixation(fixation_color, screen_info)
window.flip()
key_event = window.wait_key(["SPACE"])

draw_gabor(90, screen_info, spatial_frequency=0.7)
draw_fixation(fixation_color, screen_info)
window.flip()
key_event = window.wait_key(["SPACE"])

draw_gabor(45, screen_info, spatial_frequency=0.7)
draw_fixation(fixation_color, screen_info)
window.flip()
key_event = window.wait_key(["SPACE"])

draw_gabor(135, screen_info, spatial_frequency=0.7)
draw_fixation
window.flip()
key_event = window.wait_key(["SPACE"])


# Initial luminance gain
luminance_gain = 1.0
step_size = 0.001  # adjust as needed

while True:
    # Draw stimulus with current gain
    draw_gabor("neutralV", screen_info, luminance_gain=luminance_gain)
    draw_fixation(fixation_color, screen_info)
    window.flip()

    # Print to console for monitoring
    print(f"Current luminance gain: {luminance_gain:.3f}")

    # Wait for key input
    key = window.wait_key(["UP", "DOWN", "SPACE"])
    pressed_key = key.key

    if pressed_key == "UP":
        luminance_gain += step_size
    elif pressed_key == "DOWN":
        luminance_gain = max(0.0, luminance_gain - step_size)
    elif pressed_key == "SPACE":
        print(f"Final luminance gain selected: {luminance_gain:.3f}")
        break