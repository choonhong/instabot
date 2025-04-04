from PIL import Image
import os
from typing import List
import numpy as np

class PostFormatter:
    def __init__(self, target_size: tuple = (1080, 1080)):
        self.target_size = target_size

    def resize_image(self, image_path: str, output_path: str) -> bool:
        """Resize an image to the target size while maintaining aspect ratio."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate new dimensions
                width, height = img.size
                ratio = min(self.target_size[0] / width, self.target_size[1] / height)
                new_size = (int(width * ratio), int(height * ratio))
                
                # Resize image
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Create new image with white background
                new_img = Image.new('RGB', self.target_size, (255, 255, 255))
                
                # Paste resized image in center
                offset = ((self.target_size[0] - new_size[0]) // 2,
                         (self.target_size[1] - new_size[1]) // 2)
                new_img.paste(resized_img, offset)
                
                # Save the formatted image
                new_img.save(output_path, 'JPEG', quality=95)
                return True
        except Exception as e:
            print(f"Error formatting image {image_path}: {str(e)}")
            return False

    def create_carousel(self, image_paths: List[str], output_dir: str) -> List[str]:
        """Create a carousel of formatted images."""
        formatted_paths = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Format each image
        for i, image_path in enumerate(image_paths):
            output_path = os.path.join(output_dir, f'formatted_{i+1}.jpg')
            if self.resize_image(image_path, output_path):
                formatted_paths.append(output_path)
        
        return formatted_paths

    def verify_formatted_images(self, formatted_paths: List[str]) -> bool:
        """Verify that all formatted images meet Instagram's requirements."""
        for path in formatted_paths:
            try:
                with Image.open(path) as img:
                    # Check dimensions
                    if img.size != self.target_size:
                        return False
                    
                    # Check file size (Instagram limit is 8MB)
                    if os.path.getsize(path) > 8 * 1024 * 1024:
                        return False
                    
                    # Check format
                    if img.format != 'JPEG':
                        return False
            except Exception:
                return False
        return True 