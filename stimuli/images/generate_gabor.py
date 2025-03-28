import numpy as np
import matplotlib.pyplot as plt
from PIL import Image as PILImage

# --- Display setup (adjust based on your actual setup) ---
screen_width_cm = 40  # Physical width of screen in cm
screen_width_px = 1920  # Screen width in pixels
viewing_distance_cm = 60  # Distance from screen to eyes in cm

# Compute pixels per degree (ppd)
def compute_pixels_per_degree(screen_width_cm, screen_width_px, viewing_distance_cm):
    degrees_per_screen = 2 * np.degrees(np.arctan((screen_width_cm / 2) / viewing_distance_cm))
    pixels_per_degree = screen_width_px / degrees_per_screen
    return pixels_per_degree

ppd = compute_pixels_per_degree(screen_width_cm, screen_width_px, viewing_distance_cm)

# --- Define Gabor Parameters ---
size_degrees = 10  # Size of Gabor patch in degrees of visual angle
cpd = 0.7  # Desired cycles per degree

# Convert to pixels
size_pixels = int(size_degrees * ppd)  # Gabor patch size in pixels
frequency_pixels = ppd / cpd  # Spatial frequency in pixels per cycle

print(f"Pixels per degree: {ppd:.2f}")
print(f"Gabor size in pixels: {size_pixels}")
print(f"Frequency in pixels per cycle: {frequency_pixels:.2f}")

# --- Generate Gabor Patch ---
def generate_gabor(size_pixels, frequency_pixels, sigma=None, phase=0, orientation=0):
    """
    Generate a Gabor patch with a given spatial frequency and size in pixels.

    Parameters:
        size_pixels (int): Image size in pixels (square).
        frequency_pixels (float): Number of pixels per cycle.
        sigma (float): Standard deviation of the Gaussian envelope (auto if None).
        phase (float): Phase shift of the sinusoid.
        orientation (float): Orientation of the Gabor patch in degrees.

    Returns:
        PIL.Image: Gabor patch as a PIL image.
    """
    x, y = np.meshgrid(np.linspace(-size_pixels//2, size_pixels//2, size_pixels), 
                       np.linspace(-size_pixels//2, size_pixels//2, size_pixels))

    # Convert orientation to radians
    theta = np.deg2rad(orientation)

    # Rotate x-coordinates
    x_theta = x * np.cos(theta) + y * np.sin(theta)
    
    # Sinusoidal grating
    sinusoid = np.cos(2 * np.pi * x_theta / frequency_pixels + phase)

    # Gaussian envelope (default sigma = 1/4 of size)
    if sigma is None:
        sigma = size_pixels / 4
    gaussian = np.exp(- (x**2 + y**2) / (2 * sigma**2))

    # Multiply sinusoid with Gaussian envelope
    gabor = sinusoid * gaussian

    # Normalize to [0, 255]
    gabor_image = np.uint8((gabor - gabor.min()) / (gabor.max() - gabor.min()) * 255)
    
    # Convert to PIL image
    return PILImage.fromarray(gabor_image)

# Generate and save the Gabor image
gabor_image = generate_gabor(size_pixels=size_pixels, frequency_pixels=frequency_pixels)
gabor_image.save("gabor_patch.png")  # Save for use in Psychos


