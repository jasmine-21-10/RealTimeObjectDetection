# Real-Time Object Detection System

## About the Project
This project is a real-time object detection system built using Python, OpenCV, YOLO, and Flask. It detects objects through a webcam and allows users to upload images for object detection.

## Features
- Real-time webcam object detection
- Image upload and object detection
- Object count
- Detection confidence scores
- Detection history
- Web-based dashboard

## Technologies Used
- Python
- Flask
- OpenCV
- YOLO (Ultralytics)
- HTML
- CSS
- JavaScript

## Project Structure
- `app.py` — Flask application and detection logic
- `templates/` — HTML templates
- `static/css/` — CSS styles
- `static/js/` — JavaScript functionality
- `requirements.txt` — Python dependencies

## Installation and Setup

1. Clone this repository:
   ```bash
   git clone YOUR_REPOSITORY_URL
   ```

2. Open the project folder:
   ```bash
   cd RealTimeObjectDetection
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

## Notes
- A compatible webcam is needed for live detection.
- The YOLO model weights may be downloaded automatically when the application runs for the first time.
- Detection history is stored in memory and is cleared when the server restarts.

## Future Improvements
- Save detection history permanently
- Support video uploads
- Deploy the application online

## Author
Jasmine
