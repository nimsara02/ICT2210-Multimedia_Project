from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np


class ImageProcessor:
    """
    Handles all image processing logic using the PIL library.
    It separates the backend processing from the UI.
    """

    def __init__(self):
        """Initializes the image processor with a placeholder for the image."""
        self.original_image = None
        self.current_image = None

    def set_image(self, image):
        """Sets the image to be processed."""
        if image is not None:
            self.original_image = image.copy()
            self.current_image = image.copy()
        else:
            self.original_image = None
            self.current_image = None

    def apply_adjustments(self, brightness_val, contrast_val, saturation_val, warmth_val, grayscale_val, blur_val):
        """
        Applies all adjustments in the correct order to the original image.
        This is a critical step to ensure filters do not interfere with each other.
        """
        if self.original_image is None:
            return None

        # Always start from the original image to avoid stacking effects
        processed_image = self.original_image.copy()

        # Step 1: Apply brightness.
        if brightness_val != 0:
            enhancer = ImageEnhance.Brightness(processed_image)
            # Brightness factor: 1.0 is original, >1.0 is brighter, <1.0 is darker
            processed_image = enhancer.enhance(1 + brightness_val / 100.0)

        # Step 2: Apply contrast.
        if contrast_val != 0:
            enhancer = ImageEnhance.Contrast(processed_image)
            # Contrast factor: 1.0 is original, >1.0 increases contrast, <1.0 decreases contrast
            processed_image = enhancer.enhance(1 + contrast_val / 100.0)

        # Step 3: Apply saturation (color).
        if saturation_val != 100:
            enhancer = ImageEnhance.Color(processed_image)
            processed_image = enhancer.enhance(saturation_val / 100.0)

        # Step 4: Apply warmth/color balance. This is a manual R/G/B adjustment.
        if warmth_val != 0:
            processed_image = processed_image.convert('RGB')
            r, g, b = processed_image.split()
            r = r.point(lambda p: p * (1 + warmth_val / 100.0))
            b = b.point(lambda p: p * (1 - warmth_val / 100.0))
            processed_image = Image.merge('RGB', (r, g, b))

        # Step 5: Apply blur.
        if blur_val > 0:
            processed_image = processed_image.filter(ImageFilter.GaussianBlur(radius=blur_val))

        # Step 6: Apply grayscale filter last, as a percentage.
        if grayscale_val > 0:
            grayscale_image = ImageOps.grayscale(processed_image)
            processed_image = Image.blend(processed_image, grayscale_image.convert("RGB"), grayscale_val / 100.0)

        self.current_image = processed_image
        return self.current_image

    def rotate_image(self):
        """Rotates the image by 90 degrees clockwise."""
        if self.current_image:
            self.current_image = self.current_image.rotate(-90, expand=True)
        return self.current_image

    def sharpen_image(self):
        """Applies a sharpening filter to the image."""
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
        return self.current_image

    def apply_vignette(self):
        """Applies a vignette effect to the image."""
        if self.current_image is None:
            return None

        img_copy = self.current_image.copy()
        width, height = img_copy.size

        # Create a radial gradient mask
        center_x, center_y = width / 2, height / 2
        radius = min(width, height) / 1.5

        y_coords, x_coords = np.mgrid[:height, :width]

        distance_from_center = np.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)

        vignette_mask = 1 - (distance_from_center / radius)
        vignette_mask[vignette_mask < 0] = 0
        vignette_mask = np.clip(vignette_mask * 1.5, 0, 1)  # Adjust intensity

        # Convert mask to an image and blend
        vignette_mask_image = Image.fromarray((vignette_mask * 255).astype(np.uint8)).convert('L')

        img_copy = Image.composite(img_copy, Image.new('RGB', img_copy.size, 'black'), vignette_mask_image)
        self.current_image = img_copy
        return self.current_image
