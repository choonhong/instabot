import os
import argparse
from agents.photo_selector import PhotoSelector
from agents.caption_generator import CaptionGenerator
from agents.post_formatter import PostFormatter

class InstagramPostGenerator:
    def __init__(self, input_dir: str, output_dir: str, location: str = ""):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.location = location
        
        # Initialize agents
        self.photo_selector = PhotoSelector(target_count=4)
        self.caption_generator = CaptionGenerator()
        self.post_formatter = PostFormatter()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def generate_post(self):
        """Generate an Instagram post from the input photos."""
        print("1. Selecting best photos...")
        selected_photos = self.photo_selector.select_best_photos(self.input_dir)
        
        if not selected_photos:
            print("No suitable photos found!")
            return
        
        if not self.photo_selector.verify_selection(selected_photos):
            print("Selected photos don't meet quality standards!")
            return
        
        print(f"Selected {len(selected_photos)} photos")
        
        print("\n2. Generating caption...")
        caption = self.caption_generator.create_instagram_caption(selected_photos, self.location)
        print("Caption generated!")
        
        print("\n3. Formatting images...")
        formatted_images = self.post_formatter.create_carousel(selected_photos, self.output_dir)
        
        if not formatted_images:
            print("Failed to format images!")
            return
        
        if not self.post_formatter.verify_formatted_images(formatted_images):
            print("Formatted images don't meet Instagram requirements!")
            return
        
        print("Images formatted successfully!")
        
        # Save caption to file
        caption_path = os.path.join(self.output_dir, 'caption.txt')
        with open(caption_path, 'w', encoding='utf-8') as f:
            f.write(caption)
        
        print("\nInstagram post ready!")
        print(f"Formatted images: {', '.join(formatted_images)}")
        print(f"Caption saved to: {caption_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate Instagram posts from travel photos')
    parser.add_argument('--input_dir', required=True, help='Directory containing input photos')
    parser.add_argument('--output_dir', required=True, help='Directory for output files')
    parser.add_argument('--location', default='', help='Location of the photos (optional)')
    
    args = parser.parse_args()
    
    generator = InstagramPostGenerator(args.input_dir, args.output_dir, args.location)
    generator.generate_post()

if __name__ == '__main__':
    main() 