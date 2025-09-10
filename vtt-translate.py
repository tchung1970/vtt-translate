#!/usr/bin/env python3
"""
vtt-translate.py
by Thomas Chung
on 2025-09-10

VTT Subtitle Translation Script

This script provides an automated solution for translating English VTT (WebVTT) subtitle files 
to Korean using Google's Gemini 2.5 Flash AI model. It offers a complete pipeline from file 
parsing to translation and output generation.

Key Features:
- Parses WebVTT format subtitle files with timestamp preservation
- Batch processing for efficient API usage (processes 10 subtitles per batch)
- Interactive command-line interface with step-by-step progress tracking
- Animated spinner indicators for visual feedback during translation
- Automatic dependency checking and installation guidance
- Environment-based API key management via ~/.env file
- Error handling and fallback mechanisms
- Smart output filename generation (adds "-ko" suffix)

Technical Details:
- Uses Google's Gemini 2.5 Flash model for natural Korean translations
- Maintains original timestamp formatting and cue structure
- Supports subtitle files with or without cue identifiers
- Preserves line breaks and formatting within subtitle text
- Implements thread-safe spinner animations with ANSI color support
- Batch translation reduces API calls while maintaining translation quality

Workflow:
1. Input file selection (defaults to 'subtitles-en.vtt')
2. Environment configuration loading and API key validation
3. VTT file parsing and subtitle extraction
4. Batch translation processing with progress feedback
5. Korean VTT file generation with preserved formatting

Dependencies:
- google-generativeai: For Gemini AI model integration
- python-dotenv: For environment variable management
- Standard Python libraries: os, re, sys, time, threading, pathlib

Usage:
Simply run the script and follow the interactive prompts. Ensure your Gemini API key 
is configured in ~/.env file as GEMINI_API_KEY=your_api_key_here
"""

import os
import re
import sys
import time
import threading
from pathlib import Path

# Check and install dependencies
def check_dependencies():
    """Check for required dependencies and prompt to install if missing"""
    missing_deps = []
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_deps.append("python-dotenv")
    
    try:
        import google.generativeai as genai
    except ImportError:
        missing_deps.append("google-generativeai")
    
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install them using:")
        print(f"pip install {' '.join(missing_deps)}")
        print("\nOr install all requirements:")
        print("pip install -r requirements.txt")
        sys.exit(1)

# Check dependencies first
check_dependencies()

from dotenv import load_dotenv
import google.generativeai as genai

# Spinner frames
_SPINNERS = {
    "dots": ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'],
    "line": ['-', '\\', '|', '/'],
    "triangle": ['◢','◣','◤','◥'],
    "arrow": ['←','↖','↑','↗','→','↘','↓','↙']
}

# ANSI colors
_GREEN = "\033[92m"
_RED   = "\033[91m"
_RESET = "\033[0m"

class Spinner:
    def __init__(self, text="Loading...", spinner="dots", interval=0.08, stream=sys.stdout):
        self.text = text
        self.spinner = spinner
        self.interval = interval
        self.stream = stream

        self._frames = self._get_frames(spinner)
        self._stop = threading.Event()
        self._thread = None
        self._cursor_hidden = False
        self._render_lock = threading.Lock()
        self._last_len = 0

    def _get_frames(self, name):
        if isinstance(name, (list, tuple)) and name:
            return list(name)
        return _SPINNERS.get(str(name), _SPINNERS["dots"])

    def _hide_cursor(self):
        if not self._cursor_hidden:
            self.stream.write("\x1b[?25l")
            self.stream.flush()
            self._cursor_hidden = True

    def _show_cursor(self):
        if self._cursor_hidden:
            self.stream.write("\x1b[?25h")
            self.stream.flush()
            self._cursor_hidden = False

    def _render(self, s: str):
        pad = max(0, self._last_len - len(s))
        self.stream.write("\r" + s + (" " * pad))
        self.stream.flush()
        self._last_len = len(s)

    def _clear_line(self):
        self._render("")
        self.stream.write("\r")
        self.stream.flush()
        self._last_len = 0

    def _loop(self):
        i = 0
        self._hide_cursor()
        while not self._stop.is_set():
            frame = self._frames[i % len(self._frames)]
            line = f"{frame} {self.text}"
            with self._render_lock:
                self._render(line)
            i += 1
            end = time.time() + self.interval
            while time.time() < end:
                if self._stop.is_set():
                    break
                time.sleep(0.01)

    def start(self):
        if self._thread and self._thread.is_alive():
            return self
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join()
        with self._render_lock:
            self._clear_line()
        self._show_cursor()

    def succeed(self, text="Done."):
        self.stop()
        self.stream.write(f"{_GREEN}✔{_RESET} {text}\n")
        self.stream.flush()

    def fail(self, text="Failed."):
        self.stop()
        self.stream.write(f"{_RED}✖{_RESET} {text}\n")
        self.stream.flush()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.fail(str(exc) if str(exc) else "Failed.")
        else:
            self.succeed("Done.")

def load_environment():
    """Load environment variables from ~/.env file"""
    env_path = Path.home() / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in ~/.env")
        print("Please add GEMINI_API_KEY=your_api_key to ~/.env file")
        sys.exit(1)
    
    return api_key

def parse_vtt_file(file_path):
    """Parse VTT file and extract subtitle entries"""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split content into blocks
    blocks = re.split(r'\n\s*\n', content.strip())
    
    subtitles = []
    header = blocks[0] if blocks and blocks[0].startswith('WEBVTT') else 'WEBVTT'
    
    for block in blocks[1:] if blocks[0].startswith('WEBVTT') else blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) >= 2:
            # Check if first line is a timestamp
            if '-->' in lines[0]:
                timestamp = lines[0]
                text = '\n'.join(lines[1:])
            elif len(lines) >= 3 and '-->' in lines[1]:
                # First line might be a cue identifier
                timestamp = lines[1]
                text = '\n'.join(lines[2:])
            else:
                continue
            
            subtitles.append({
                'timestamp': timestamp,
                'text': text
            })
    
    return header, subtitles

def translate_text_batch(texts, model, spinner=None):
    """Translate a batch of texts to Korean"""
    if not texts:
        return []
    
    # Create a prompt for batch translation
    prompt = """Translate the following English subtitle texts to Korean. 
Keep the translations natural and appropriate for subtitles.
Maintain the same number of lines as the input.
Return only the translated texts, one per line, in the same order:

"""
    
    for i, text in enumerate(texts):
        prompt += f"{i+1}. {text}\n"
    
    try:
        if spinner:
            spinner.text = "Translating batch with Gemini AI..."
        response = model.generate_content(prompt)
        translated_lines = response.text.strip().split('\n')
        
        # Clean up the translations (remove numbering if present)
        cleaned_translations = []
        for line in translated_lines:
            # Remove leading numbers and dots if present
            cleaned = re.sub(r'^\d+\.\s*', '', line.strip())
            if cleaned:
                cleaned_translations.append(cleaned)
        
        return cleaned_translations[:len(texts)]  # Ensure we don't have more translations than inputs
    
    except Exception as e:
        if spinner:
            spinner.fail(f"Translation error: {e}")
        else:
            print(f"Translation error: {e}")
        return texts  # Return original texts if translation fails

def translate_subtitles(subtitles, api_key):
    """Translate all subtitles using Gemini AI"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print(f"Translating {len(subtitles)} subtitle entries...")
    
    # Batch process subtitles for efficiency
    batch_size = 10
    translated_subtitles = []
    total_batches = (len(subtitles) + batch_size - 1) // batch_size
    
    for i in range(0, len(subtitles), batch_size):
        batch = subtitles[i:i + batch_size]
        texts = [sub['text'] for sub in batch]
        
        batch_num = i // batch_size + 1
        spinner_text = f"Batch {batch_num}/{total_batches}: Translating {len(texts)} subtitles"
        
        spinner = Spinner(text=spinner_text).start()
        try:
            translated_texts = translate_text_batch(texts, model, spinner)
            spinner.succeed(f"Batch {batch_num}/{total_batches}: Translated {len(texts)} subtitles")
        except Exception as e:
            spinner.fail(f"Batch {batch_num}/{total_batches}: Failed - {e}")
            raise
        
        for j, sub in enumerate(batch):
            translated_sub = {
                'timestamp': sub['timestamp'],
                'text': translated_texts[j] if j < len(translated_texts) else sub['text']
            }
            translated_subtitles.append(translated_sub)
    
    return translated_subtitles

def write_vtt_file(header, subtitles, output_path):
    """Write translated subtitles to VTT file"""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(header + '\n\n')
        
        for subtitle in subtitles:
            file.write(f"{subtitle['timestamp']}\n")
            file.write(f"{subtitle['text']}\n\n")
    
    print(f"Korean subtitles saved to: {output_path}")

def main():
    """Main function"""
    title = "VTT Subtitle Translation Tool"
    subtitle = "Powered by Gemini 2.5 Flash AI Model"
    print(title)
    print("=" * len(title))
    print(subtitle)
    
    # Step 1: Get input file
    print("\nStep 1: Input file selection")
    default_file = "subtitles-en.vtt"
    input_file = input(f"Enter VTT file path (default: {default_file}, type 'exit' to quit): ").strip()
    if input_file.lower() == 'exit':
        print("Goodbye!")
        sys.exit(0)
    if not input_file:
        input_file = default_file
    
    # Step 2: Load environment and API key
    print("\nStep 2: Loading API configuration")
    api_key = load_environment()
    print("✓ Gemini API key loaded successfully")
    
    # Step 3: Parse VTT file
    print(f"\nStep 3: Parsing VTT file")
    print(f"Reading file: {input_file}")
    header, subtitles = parse_vtt_file(input_file)
    print(f"✓ Detected English VTT file with {len(subtitles)} subtitle entries")
    
    if not subtitles:
        print("✗ No subtitles found in the file")
        sys.exit(1)
    
    # Step 4: Translate subtitles
    print(f"\nStep 4: Translating subtitles to Korean")
    translated_subtitles = translate_subtitles(subtitles, api_key)
    
    # Step 5: Generate output filename
    print(f"\nStep 5: Saving Korean VTT file")
    input_path = Path(input_file)
    output_file = input_path.stem.replace('-en', '') + "-ko.vtt"
    
    # Write Korean VTT file
    write_vtt_file(header, translated_subtitles, output_file)
    
    print(f"✓ Translation completed successfully!")
    print(f"✓ Korean subtitles saved as: {output_file}")

if __name__ == "__main__":
    main()