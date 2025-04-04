import cv2
import numpy as np
from PIL import Image
import os
from typing import List, Tuple

class PhotoSelector:
    def __init__(self, target_count: int = 10):
        self.target_count = target_count

    def analyze_image(self, image_path: str) -> float:
        """Analyze image quality and return a score."""
        img = cv2.imread(image_path)
        if img is None:
            return 0.0

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate various quality metrics
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Normalize scores
        blur_score = min(blur_score / 500.0, 1.0)  # Normalize blur score
        brightness_score = 1.0 - abs(brightness - 127) / 127  # Penalize too dark/bright
        contrast_score = min(contrast / 50.0, 1.0)  # Normalize contrast
        
        # Combine scores (you can adjust weights)
        final_score = (blur_score * 0.4 + brightness_score * 0.3 + contrast_score * 0.3)
        return final_score

    def select_best_photos(self, input_dir: str) -> List[str]:
        """Select the best photos from the input directory."""
        image_scores = []
        
        # Get all image files
        valid_extensions = {'.jpg', '.jpeg', '.png'}
        for filename in os.listdir(input_dir):
            if os.path.splitext(filename)[1].lower() in valid_extensions:
                image_path = os.path.join(input_dir, filename)
                score = self.analyze_image(image_path)
                image_scores.append((image_path, score))
        
        # Sort by score and select top N
        image_scores.sort(key=lambda x: x[1], reverse=True)
        selected_photos = [path for path, _ in image_scores[:self.target_count]]
        
        return selected_photos

    def verify_selection(self, selected_photos: List[str]) -> bool:
        """Verify that the selected photos meet minimum quality standards."""
        if not selected_photos:
            return False
            
        min_quality_threshold = 0.3
        for photo in selected_photos:
            if self.analyze_image(photo) < min_quality_threshold:
                return False
        return True 