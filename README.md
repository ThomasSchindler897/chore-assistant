Chore Assistant Project Roadmap
Goal: Build a Raspberry Pi-powered household chore assistant with touchscreen, voice interaction, and AI. Develop first on a PC, then deploy to the Raspberry Pi.

Milestone 1 – Development Environment
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Install Python, VS Code, Git
2. Create GitHub repo and initialize Git
3. Create project folder structure
4. Create virtual environment and install Flask
5. Run first Flask 'Hello World' app

Milestone 2 – Learn Flask
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Routes
2. HTML templates
3. Navigation bar
4. Basic CSS
5. Understand request/response

Milestone 3 – SQLite Database
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Create database
2. Create Chore table
3. Insert chore
4. Display chores
5. Edit/Delete chores

Milestone 4 – Recurring Task Logic
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Daily chores
2. Weekly chores
3. Monthly chores
4. Weekday-specific chores
5. Determine what's due today

Milestone 5 – Completion History
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Completion table
2. Mark complete
3. Show completed today
4. Undo completion
5. Progress calculation

Milestone 6 – Better UI
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Bootstrap
2. Icons
3. Cards
4. Progress bars
5. Dark mode

Milestone 7 – Calendar
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Monthly calendar
2. Highlight chores
3. Upcoming tasks
4. Overdue tasks
5. Weekly view

Milestone 8 – Statistics
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Completion graphs
2. Streaks
3. Completion %
4. Monthly trends
5. Fun stats

Milestone 9 – Raspberry Pi Deployment
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Install Raspberry Pi OS and update the system packages with `sudo apt update && sudo apt upgrade`
2. Enable SSH via `sudo raspi-config` or by creating an empty `ssh` file on the boot partition
3. Find the Pi's IP address and confirm remote access with `ssh pi@<pi-ip>`
4. Clone the repository into the Pi home directory
5. Create a Python 3 virtual environment and activate it: `python3 -m venv venv && source venv/bin/activate`
6. Install dependencies from `requirements.txt` with `pip install -r requirements.txt`
7. Run `python3 app.py` and confirm the app loads at `http://localhost:5000` or `http://<pi-ip>:5000`
8. Create a `systemd` service file for the Flask app like `/etc/systemd/system/chore_assistant.service`
   - Example service file:
     ```ini
     [Unit]
     Description=Chore Assistant Flask App
     After=network.target

     [Service]
     User=pi
     WorkingDirectory=/home/pi/chore_assistant
     Environment="PATH=/home/pi/chore_assistant/venv/bin"
     ExecStart=/home/pi/chore_assistant/venv/bin/python3 /home/pi/chore_assistant/app.py
     Restart=always
     RestartSec=10

     [Install]
     WantedBy=multi-user.target
     ```
9. Enable and start the service: `sudo systemctl daemon-reload && sudo systemctl enable chore_assistant.service && sudo systemctl start chore_assistant.service`
10. Reboot the Pi and confirm the app restarts automatically on boot

Milestone 10 – Touchscreen
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Connect and calibrate the touchscreen hardware using the Pi touchscreen tools
2. Choose a browser kiosk/fullscreen launch command for the app on the Pi
   - Example: `chromium-browser --kiosk http://localhost:5000 --incognito --noerrdialogs --disable-infobars`
3. Increase button, card, and input sizes across the UI for touchability
4. Improve spacing and navigation so controls are easy to tap
5. Add larger controls for calendar navigation, week/month toggles, and task actions
6. Prevent screen blanking on the Pi with `sudo raspi-config` or `xset s off && xset -dpms && xset s noblank`
7. Add the browser launch command and touch settings to Pi autostart if needed
8. Test the app on touchscreen hardware and refine tap targets and layout

Pi Deployment & Touchscreen Checklist
- Install Raspberry Pi OS and enable SSH
- Clone the repo, create a venv, and install `requirements.txt`
- Run `python3 app.py` to verify the app works locally
- Add a `systemd` service to launch the app on boot
- Or use `pm2` / `screen` as an alternative process manager for the app
  - Install `pm2` with `npm install -g pm2`
  - Example: `pm2 start venv/bin/python --name chore_assistant -- app.py`
- Add a Chromium kiosk launch command for the touchscreen
- Disable screen blanking and verify the touchscreen UI

Milestone 11 – Voice Assistant
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Choose a speech-to-text engine and install its Python integration
2. Add a microphone input flow and voice capture button to the UI
3. Add text-to-speech output so the app can speak responses
4. Implement voice command parsing for chores and navigation
5. Let users ask "What are today's chores?" and receive spoken results
6. Allow voice completion and undo of chore items
7. Add a wake word or button-based voice trigger for safer always-listening
8. Provide spoken confirmation and error feedback
9. Test the voice assistant with multiple chore scenarios
10. Document the voice setup steps for Pi deployment

Implementation Notes:
- Start with a simple button-triggered voice flow before adding always-listening behavior.
- Keep voice parsing limited to chore-related commands to reduce false positives.
- Use local or offline speech tools on the Pi whenever possible to minimize latency.

Priority: start with capture and feedback, then add command parsing, then add wake-word behavior.

Milestone 12 – AI Integration
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Choose an AI/LLM provider or local model that matches the project scope
2. Add an API wrapper or integration layer for the selected AI service
3. Build prompt templates for chore recommendations and status summaries
4. Add session memory for user preferences, past actions, and recurring tasks
5. Use AI reasoning to suggest which chore to do next or how to batch chores
6. Surface AI-generated suggestions in the app UI
7. Build a conversational flow that reads current chores and answers questions
8. Add fallback behavior for offline or service unavailable cases
9. Test prompt templates and tune them using real examples
10. Document how the AI integration works and any required API keys

Implementation Notes:
- Keep the first AI feature lightweight: ask for chore suggestions and summaries.
- Store only the minimal context needed for better responses, not full conversation logs.
- Include a clear offline fallback so the app still works without AI access.

Priority: integrate basic suggestions first, then memory, then richer conversational flows.

Milestone 13 – Household Features
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Add support for multiple user profiles and household members
2. Create user registration or profile selection in the UI
3. Enable assigning chores to specific people
4. Add reminders and notifications for assigned chores
5. Add shared chore groups and family task views
6. Add a shared shopping or supplies list with add/edit/remove actions
7. Show user-specific stats and completion progress
8. Add basic user roles or permissions if needed
9. Test multi-user assignment workflows and shared lists
10. Document how household teams and assignments work

Implementation Notes:
- Start with simple profile selection rather than a full account system.
- Keep shared chores and shopping lists in the same database schema for reuse.
- Make it easy to switch active user in the UI for family use.

Priority: build user profiles first, then chore assignments, then shared household flows.

Milestone 14 – Smart Home
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Choose simple smart home integrations: motion sensors, lights, plugs, door sensors
2. Add a dashboard section for sensor status and home state
3. Integrate smart light or plug control with API or MQTT if available
4. Add door/window sensor awareness and alerting
5. Display weather information and home conditions in the UI
6. Trigger reminders or chore suggestions from sensor inputs
7. Add actionable smart home buttons for lights and home modes
8. Test sensor-triggered flows and notifications
9. Keep the smart home integration optional for users without hardware
10. Document the integration steps and supported hardware

Implementation Notes:
- Build smart home features as optional add-ons, not required core functionality.
- Use simulated sensor data locally before wiring real devices.
- Prioritize simple controls like lights and alerts over complex automation.

Priority: connect status and display first, then add controls, then automation/triggers.

Milestone 15 – Polish
Objective: Complete these mini-projects in 15–30 minute sessions.

1. Add backups and restore options for app data
2. Add logging, error handling, and crash reporting notes
3. Add a settings page and personalization options
4. Improve UI polish and accessibility across screens
5. Package the app for easy deployment with Docker or similar
6. Add automatic update or maintenance workflow notes
7. Add a release checklist for testing and deployment
8. Add tests for new features and automation where possible
9. Optimize performance and reduce unnecessary page load time
10. Document the final deployment and maintenance process

Implementation Notes:
- Focus on reliability: backups, logs, and clear recovery steps.
- Add a simple settings page for display, sound, and notification preferences.
- Use Docker as a packaging option, but keep a non-containerized Pi workflow too.

Priority: stabilize backups/logging first, then polish UI/settings, then package and automate.

Development Philosophy
- Every coding session ends with a working feature.
- Commit to Git after each mini-project.
- Focus on learning concepts, not copying code.
- Build on your computer first; deploy to the Raspberry Pi later.