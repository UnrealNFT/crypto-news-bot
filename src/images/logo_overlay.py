"""
Logo overlay module
Adds logo watermark to generated images
"""
import os
from PIL import Image


def add_logo_overlay(
    image_path: str,
    logo_path: str = None,
    position: str = "top-left",
    logo_size: int = 200,
    margin: int = 15,
    logger=None
) -> str:
    """
    Add logo overlay to image.
    
    Args:
        image_path: Path to base image
        logo_path: Path to logo file (default: assets/Logofr.PNG)
        position: Logo position ("top-left", "top-right", "bottom-left", "bottom-right")
        logo_size: Logo size in pixels (square)
        margin: Margin from edges in pixels
        logger: Logger instance
        
    Returns:
        Path to image with logo overlay
    """
    try:
        # Find logo path
        if logo_path is None:
            # Try common locations
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            possible_paths = [
                os.path.join(script_dir, "assets", "Logofr.PNG"),
                os.path.join(script_dir, "Logofr.PNG"),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    break
        
        if not logo_path or not os.path.exists(logo_path):
            if logger:
                logger.warning(f"⚠️  Logo not found, skipping overlay")
            return image_path
        
        if logger:
            logger.info(f"🖼️  Adding logo overlay: {logo_path}")
        
        # Open images
        base_image = Image.open(image_path)
        logo = Image.open(logo_path)
        
        # Resize logo
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Calculate position
        if position == "top-left":
            x_pos = margin
            y_pos = margin
        elif position == "top-right":
            x_pos = base_image.width - logo_size - margin
            y_pos = margin
        elif position == "bottom-left":
            x_pos = margin
            y_pos = base_image.height - logo_size - margin
        elif position == "bottom-right":
            x_pos = base_image.width - logo_size - margin
            y_pos = base_image.height - logo_size - margin
        else:
            x_pos = margin
            y_pos = margin
        
        # Apply logo with transparency
        if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
            # Logo has transparency
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Ensure base image supports alpha
            if base_image.mode != 'RGBA':
                base_image = base_image.convert('RGBA')
            
            base_image.paste(logo, (x_pos, y_pos), logo)
            
            if logger:
                logger.info(f"✅ Logo applied at {position} with transparency")
        else:
            # Logo without transparency
            if logo.mode != 'RGB':
                logo = logo.convert('RGB')
            if base_image.mode != 'RGB':
                base_image = base_image.convert('RGB')
                
            base_image.paste(logo, (x_pos, y_pos))
            
            if logger:
                logger.info(f"✅ Logo applied at {position} without transparency")
        
        # Save with logo
        output_path = image_path.replace(".png", "_with_logo.png")
        base_image.save(output_path)
        
        if logger:
            logger.info(f"✅ Image with logo saved: {output_path}")
        
        return output_path
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Error adding logo overlay: {e}")
        return image_path  # Return original on error
