# Instagram Travel Post Generator

This project implements a multi-agent system that automatically prepares Instagram posts from travel photos. The system selects the best photos and generates engaging captions.

## Features

- Automatic photo selection from a collection of travel photos
- Image quality assessment
- Caption generation
- Instagram post formatting

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys (if needed)

3. Run the main script:
```bash
python main.py --input_dir /path/to/photos
```

## Project Structure

- `main.py`: Main orchestration script
- `agents/`: Directory containing different agent modules
  - `photo_selector.py`: Agent for selecting the best photos
  - `caption_generator.py`: Agent for generating captions
  - `post_formatter.py`: Agent for formatting the final post
- `utils/`: Utility functions and helpers 