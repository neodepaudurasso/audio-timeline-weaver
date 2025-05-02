
# Audio Timeline Weaver

A simple audio editor built with Python and PyQt5 that allows you to import, edit, and export audio files.

## Features

- Import audio files (MP3, WAV, OGG, FLAC)
- Visualize audio waveforms
- Arrange audio clips on a timeline
- Basic editing tools (cut, split, delete)
- Export edited audio (MP3, WAV)

## Prerequisites

- Python 3.8 or higher
- FFmpeg (must be placed in the project directory)

## FFmpeg Setup

1. Download FFmpeg from [the official website](https://ffmpeg.org/download.html) or [FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/) (for Windows)
2. Extract the downloaded package
3. Copy the `ffmpeg.exe` file to the root directory of this project

## Installation

1. Run the `install.bat` file to:
   - Create a Python virtual environment
   - Install required dependencies

```
install.bat
```

## Running the Application

1. Run the `run.bat` file to start the application:

```
run.bat
```

## User Guide

### Importing Audio Files
1. Click the "Import Audio" button
2. Select one or more audio files to import
3. The imported files will appear in the Audio Library panel

### Working with the Timeline
1. Double-click on a file in the library to add it to the timeline
2. Alternatively, right-click on a file and select "Add to Timeline"
3. Audio clips can be arranged on the timeline

### Editing Audio
1. Select a clip or a portion of a clip on the timeline
2. Use the editing tools:
   - Cut: Remove the selected portion
   - Split: Divide the clip at the current position
   - Delete Selection: Remove the selected clip or portion

### Exporting Audio
1. Click the "Export Audio" button
2. Choose a file name and format (MP3 or WAV)
3. Click "Save" to export your edited audio

## Note

This is a simple audio editor for basic editing needs. For advanced audio editing, consider professional software like Audacity, Adobe Audition, or similar applications.
