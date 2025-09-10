# VTT Subtitle Translation Tool

A Python script that automatically translates English VTT (WebVTT) subtitle files to Korean using Google's Gemini 2.5 Flash AI model.

## Features

- **Smart VTT Parsing**: Handles WebVTT format files with timestamp preservation
- **AI-Powered Translation**: Uses Google's Gemini 2.5 Flash for natural Korean translations
- **Batch Processing**: Efficient API usage by processing subtitles in batches of 10
- **Interactive Interface**: Step-by-step progress with animated spinner indicators
- **Error Handling**: Automatic dependency checking and graceful error recovery
- **Environment Management**: Secure API key storage via `.env` file
- **Smart Output**: Automatically generates output files with `-ko` suffix

## Prerequisites

- Python 3.7 or higher
- Gemini API key from [Google AI Studio](https://aistudio.google.com/)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/vtt-translate.git
cd vtt-translate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
Create a `~/.env` file in your home directory with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Run the script:
```bash
python vtt-translate.py
```

2. Follow the interactive prompts:
   - Enter the path to your English VTT file
   - The script will automatically translate and save the Korean version

3. Find your translated file:
   - Input files get `-ko` suffix added before the extension

## Example

```bash
$ python vtt-translate.py

VTT Subtitle Translation Tool
=============================
Powered by Gemini 2.5 Flash AI Model

Step 1: Input file selection
Enter VTT file path (type 'exit' to quit): 

Step 2: Loading API configuration
✓ Gemini API key loaded successfully

Step 3: Parsing VTT file
Reading file: [your-file.vtt]
✓ Detected English VTT file with subtitle entries

Step 4: Translating subtitles to Korean
Translating 125 subtitle entries...
✔ Batch 1/13: Translated 10 subtitles
✔ Batch 2/13: Translated 10 subtitles
...

Step 5: Saving Korean VTT file
Korean subtitles saved to: [your-file-ko.vtt]
✓ Translation completed successfully!
```

## Technical Details

### Workflow
1. **Input Validation**: Checks file existence and format
2. **Environment Setup**: Loads API key from `~/.env`
3. **VTT Parsing**: Extracts timestamps and text while preserving structure
4. **Batch Translation**: Groups subtitles for efficient API calls
5. **Output Generation**: Creates Korean VTT file with original formatting

### Supported Features
- WebVTT files with or without cue identifiers
- Multi-line subtitle text preservation
- Timestamp format maintenance
- Batch processing for API efficiency
- Progress tracking with visual feedback

### Dependencies
- `google-generativeai>=0.8.0` - Gemini AI integration
- `python-dotenv>=1.0.0` - Environment variable management

## File Structure

```
vtt-translate/
├── vtt-translate.py      # Main translation script
├── requirements.txt      # Python dependencies
├── CLAUDE.md            # Development documentation
└── README.md            # This file
```

## Error Handling

The script includes comprehensive error handling for:
- Missing dependencies (with installation guidance)
- Invalid or missing API keys
- Malformed VTT files
- Network/API errors during translation
- File I/O issues

## API Usage

The tool uses Google's Gemini 2.5 Flash model with batch processing to minimize API calls while maintaining translation quality. Each batch processes up to 10 subtitle entries simultaneously.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

**Thomas Chung**  
Created: September 10, 2025

## License

This project is open source and available under the MIT [LICENSE](LICENSE).

## Acknowledgments

- Google AI team for the Gemini 2.5 Flash model
- WebVTT specification contributors
- Open source Python community