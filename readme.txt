# Palm Authentication GUI (PyQt5)

This project is a **PyQt5-based GUI** for a palm authentication system designed to work with a Raspberry Pi backend.

## Features
- Single-window PyQt5 GUI
- Home screen with Register / Match / Stop
- Instruction screen with:
  - Live instruction text
  - Color-coded guidance
  - Distance display
  - Tilt guidance (LEFT / STRAIGHT / RIGHT)
  - Mode indicator (Registration / Matching)
  - Progress bar
  - Result and confidence display
- Dummy demo mode for testing without hardware
- Backend-ready (WebSocket + HTTP architecture)

## Demo Mode
Currently, the GUI runs in a **dummy demo mode** that simulates backend messages such as:
- "Move palm closer"
- "Tilt left / straight / right"
- MATCH / NO MATCH results

This allows UI testing without Raspberry Pi hardware.

## Tech Stack
- Python 3
- PyQt5
- Git / GitHub

## Future Work
- Connect to real Raspberry Pi backend
- Replace dummy demo with WebSocket updates
- Add camera preview
- Improve UI styling

---
