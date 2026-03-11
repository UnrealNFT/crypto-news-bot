"""
FLUX.1 Image Generator
Generates images from text prompts using FLUX.1-schnell model
"""
import os
import time
import torch
from diffusers import FluxPipeline


# Global pipeline instance (load once, reuse)
_flux_pipeline = None


def load_flux_pipeline(device="cpu", logger=None):
    """Load FLUX.1-schnell pipeline (CPU mode)."""
    global _flux_pipeline
    
    if _flux_pipeline is not None:
        return _flux_pipeline
    
    if logger:
        logger.info("Loading FLUX.1-schnell model (this may take a few minutes on first run)...")
    
    try:
        # Load FLUX.1-schnell (fast 4-step model)
        _flux_pipeline = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.float32,  # CPU uses float32
            device_map=device,
        )
        
        # Move to CPU
        _flux_pipeline = _flux_pipeline.to(device)
        
        if logger:
            logger.info(f"✅ FLUX.1 loaded successfully on {device.upper()}")
        
        return _flux_pipeline
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Error loading FLUX.1: {e}")
        raise


def generate_image_with_flux(
    prompt: str,
    output_dir: str = "generated_images",
    device: str = "cpu",
    num_inference_steps: int = 4,
    guidance_scale: float = 0.0,
    width: int = 768,
    height: int = 768,
    logger=None
) -> str:
    """
    Generate image using FLUX.1-schnell model.
    
    Args:
        prompt: Text description for image generation
        output_dir: Directory to save generated images
        device: "cpu" or "cuda" (default: "cpu")
        num_inference_steps: Number of denoising steps (FLUX.1-schnell optimized for 4)
        guidance_scale: Guidance scale (FLUX.1-schnell works best with 0.0)
        width: Image width (default: 768)
        height: Image height (default: 768)
        logger: Logger instance
        
    Returns:
        Path to generated image file
    """
    try:
        start_time = time.time()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load pipeline
        pipeline = load_flux_pipeline(device=device, logger=logger)
        
        if logger:
            logger.info(f"🎨 Generating image: '{prompt[:60]}...'")
            logger.info(f"⚙️  Settings: {width}x{height}, {num_inference_steps} steps, CPU mode")
        
        # Generate image
        with torch.no_grad():
            result = pipeline(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
            )
        
        image = result.images[0]
        
        # Save image
        timestamp = int(time.time())
        filename = f"flux_image_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath)
        
        elapsed_time = time.time() - start_time
        
        if logger:
            logger.info(f"✅ Image generated in {elapsed_time:.1f}s: {filepath}")
        
        return filepath
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Error generating image with FLUX.1: {e}")
        return None


def generate_crypto_image(article: dict, logger=None) -> str:
    """
    Generate crypto-themed image from article.
    
    Args:
        article: Article dict with 'title' and 'description'
        logger: Logger instance
        
    Returns:
        Path to generated image with logo overlay
    """
    try:
        # Build prompt from article
        title = article.get("title", "")
        description = article.get("description", "")[:200]  # Limit description length
        
        # Create crypto-themed prompt
        prompt = f"""Beautiful anime manga illustration in Studio Ghibli style representing: {title}. 
        
Context: {description}

Style: Bright colorful manga art with vibrant colors, clean cartoon aesthetic, cherry blossoms, 
warm color palette with soft pinks and golden yellows. Cheerful anime environment with soft lighting. 
NO logos, NO text, NO symbols. Pure artistic manga scenery."""
        
        # Generate image (CPU mode)
        image_path = generate_image_with_flux(
            prompt=prompt,
            device="cpu",
            num_inference_steps=4,  # Fast mode for schnell
            guidance_scale=0.0,  # Schnell optimized
            width=768,
            height=768,
            logger=logger
        )
        
        return image_path
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Error generating crypto image: {e}")
        return None
