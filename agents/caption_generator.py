from transformers import pipeline
from typing import List
import os

class CaptionGenerator:
    def __init__(self):
        self.image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        self.sentiment_analyzer = pipeline("sentiment-analysis")

    def generate_caption(self, image_path: str) -> str:
        """Generate a caption for a single image."""
        try:
            result = self.image_to_text(image_path)
            caption = result[0]['generated_text']
            return caption
        except Exception as e:
            print(f"Error generating caption for {image_path}: {str(e)}")
            return ""

    def analyze_sentiment(self, text: str) -> str:
        """Analyze the sentiment of the text."""
        try:
            result = self.sentiment_analyzer(text)
            return result[0]['label']
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return "NEUTRAL"

    def create_instagram_caption(self, image_paths: List[str], location: str = "") -> str:
        """Create an engaging Instagram caption for multiple photos."""
        captions = []
        sentiments = []
        
        # Generate captions for each image
        for image_path in image_paths:
            caption = self.generate_caption(image_path)
            if caption:
                captions.append(caption)
                sentiment = self.analyze_sentiment(caption)
                sentiments.append(sentiment)

        # Create the main caption
        main_caption = ""
        
        # Add location if provided
        if location:
            main_caption += f"📍 {location}\n\n"
        
        # Add the best caption
        if captions:
            main_caption += f"{captions[0]}\n\n"
        
        # Add hashtags based on sentiments and content
        hashtags = self._generate_hashtags(captions, sentiments)
        main_caption += hashtags
        
        return main_caption

    def _generate_hashtags(self, captions: List[str], sentiments: List[str]) -> str:
        """Generate relevant hashtags based on captions and sentiments."""
        hashtags = set()
        
        # Add common travel hashtags
        hashtags.update([
            "#travel", "#wanderlust", "#travelgram", "#instatravel",
            "#travelphotography", "#traveltheworld", "#travelblogger"
        ])
        
        # Add sentiment-based hashtags
        for sentiment in sentiments:
            if sentiment == "POSITIVE":
                hashtags.update(["#happy", "#blessed", "#amazing"])
            elif sentiment == "NEUTRAL":
                hashtags.update(["#peaceful", "#serene", "#calm"])
        
        # Convert to string
        return " ".join(sorted(hashtags)) 