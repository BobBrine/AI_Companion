# AI Companion

An AI companion that can move around the screen, understand what is happening on-screen, and help with tasks inside a user-defined area. The goal is to create a desktop assistant that can observe a selected region, interact with it, and offer suggestions while learning user habits to speed up work and study.

## Vision
- A small on-screen companion that can move, animate, and react.
- On-screen understanding inside a selectable region ("see" only what the user allows).
- Task assistance and suggestions based on context.
- Habit learning to personalize workflow help over time.
- Inspired by the idea of a J.A.R.V.I.S.-style assistant.

## Current Status
Early prototype. Basic avatar and UI logic are present, with experimentation around local model usage.

## Planned Features
- Screen region selection and bounding box controls.
- Visual context capture and processing.
- Lightweight local inference for on-screen understanding.
- Interaction layer for task suggestions.
- Personalization and habit learning.
- Configurable behaviors, voice, and visual themes.

## Project Structure
- input_handler.py: Input and event handling.
- main.py: App entry point.
- pet_avatar.py: Avatar rendering and behavior.
- ui.py: UI helpers and layout.
- test_local_model.py: Local model experiments.
- images/: Sprite assets.

## How To Run
1. Ensure Python is installed.
2. Install any required dependencies (add them as they are introduced).
3. Run:
   python main.py

## Notes
- This project is in active development.
- Contributions and feedback are welcome.
