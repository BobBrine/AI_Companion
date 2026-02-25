# AI Companion

## Overview
This project is an experimental AI companion designed to explore how autonomous software agents can visually interact with a desktop environment. The companion is intended to move around the screen, observe a user-defined region, and provide assistance based on on-screen context.

The main goal of this project is to learn about interactive system design, basic AI decision-making, and real-time visual interaction, inspired by the concept of a J.A.R.V.I.S.-style desktop assistant.

## Current Progress
- Draggable desktop avatar with always-on-top transparent window
- Smooth eye tracking that follows the cursor
- Right-click context menu (Settings / Close Pet)
- Local AI chat integration through Ollama (background-threaded requests)
- Interactive chat UI with typing indicator and timed response bubble
- Rich text input editing (selection, copy/paste, cut, undo/redo, word/all select)
- Drag-and-drop support for files and text into the input field
- Selectable response text with Ctrl+C copy from the output bubble

## What's New
- **Asynchronous AI replies:** model calls run in a worker thread so the UI stays responsive.
- **Typing feedback UI:** animated typing indicator appears while waiting for model output.
- **Advanced text input editing:** supports Ctrl+A/C/X/V, undo/redo, cursor navigation, and selection.
- **Selectable output text:** you can highlight assistant replies and copy them to clipboard.
- **Improved avatar behavior:** eye tracking smoothness and two-eye mode are integrated.

## Planned Features
- User-selected screen regions and bounding box controls
- Visual context capture and basic on-screen analysis
- Lightweight local inference for contextual understanding
- Interaction layer for suggestions and assistance
- Simple personalization and habit-learning experiments
- Configurable avatar behavior and visual themes

![AI](screenshot/Screenshot1.png)
![AI Avatar](screenshot/Screenshot2.png)

## Project Structure
- `main.py` — Application entry point and main loop
- `ai_core.py` — Ollama model communication helpers
- `pet_avatar.py` — Avatar rendering and behavior logic
- `input_handler.py` — Input and event handling
- `ui.py` — UI components and layout helpers
- `images/` — Sprite and visual assets

## What I Learned
- Structuring a real-time Python application
- Managing rendering loops and input handling
- Designing modular components for future expansion
- Experimenting with early-stage AI integration
- Translating high-level ideas into incremental technical steps

## Future Development
This project is still in active development. Future work will focus on improving contextual understanding, refining interaction logic, and experimenting with simple personalization techniques to better support user workflows.

## How to Run
1. Ensure Python 3.10+ is installed.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Optional: Local Model Setup
The app uses Ollama for local model responses and requires additional setup.

1. Install Ollama from https://ollama.com
2. Pull a model (example):
   ```bash
   ollama pull llama3.2
   ```
3. Run the app after model setup:
   ```bash
   python main.py
   ```

## Notes
- Windows only (uses Win32 APIs).
- Make sure the images folder is present (the app loads sprite assets from images/).
This project is a personal learning initiative and serves as a sandbox for exploring AI-driven interactive systems.
