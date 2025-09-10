# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a VTT subtitle translation tool that converts English subtitle files to Korean using Google's Gemini 2.5 Flash AI model.

## Development Setup

### Prerequisites
- Python 3.7 or higher
- Gemini API key from Google AI Studio

### Installation
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `~/.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

### Running the Script
```bash
python vtt-translate.py
```

## Architecture Notes

- `vtt-translate.py`: Main script that handles VTT file parsing, translation via Gemini 2.5 Flash API, and output generation
- Uses `google-generativeai` library for AI translation
- Processes subtitles in batches for efficiency
- Supports standard WebVTT format files
- Output files are named with `-ko` suffix
- Features step-by-step progress display with animated spinners