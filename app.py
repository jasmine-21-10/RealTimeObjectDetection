
from flask import Flask, render_template, Response, jsonify, request
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from datetime import datetime
import cv2
import os
import uuid

app = Flask(__name__)

# ---------------- CONFIGURATION ----------------

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# ---------------- LOAD YOLO MODEL ----------------

model = YOLO("yolo11n.pt")

# ---------------- WEBCAM ----------------

camera = cv2.VideoCapture(0)

# ---------------- LIVE STATISTICS ----------------

stats = {
    "object_count": 0,
    "classes": [],
    "status": "Active"
}

# Store latest 20 upload detections in memory
detection_history = []


# ---------------- LIVE VIDEO DETECTION ----------------

def generate_frames():
    while True:
        success, frame = camera.read()

        if not success:
            break

        results = model(frame, verbose=False)
        result = results[0]

        annotated_frame = result.plot()
        object_count = len(result.boxes)

        detected_classes = []

        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            if class_name not in detected_classes:
                detected_classes.append(class_name)

        stats["object_count"] = object_count
        stats["classes"] = detected_classes

        cv2.putText(
            annotated_frame,
            f"Objects Detected: {object_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        success, buffer = cv2.imencode(
            ".jpg", annotated_frame
        )

        if not success:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


# ---------------- HOME PAGE ----------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------- WEBCAM VIDEO ----------------

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ---------------- LIVE STATISTICS API ----------------

@app.route("/api/stats")
def get_stats():
    return jsonify(stats)


# ---------------- CHECK IMAGE TYPE ----------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ---------------- IMAGE UPLOAD DETECTION ----------------

@app.route("/upload", methods=["POST"])
def upload_image():

    if "image" not in request.files:
        return jsonify({
            "error": "Please select an image"
        }), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "error": "No image selected"
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Upload JPG, PNG, or WEBP images only"
        }), 400

    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({
            "error": "Invalid filename"
        }), 400

    # Use a unique filename to avoid overwriting uploads
    unique_name = uuid.uuid4().hex
    extension = filename.rsplit(".", 1)[1].lower()
    saved_filename = f"{unique_name}.{extension}"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        saved_filename
    )

    file.save(filepath)

    # Read uploaded image
    image = cv2.imread(filepath)

    if image is None:
        os.remove(filepath)
        return jsonify({
            "error": "Invalid image file"
        }), 400

    # Run object detection
    results = model(image, verbose=False)
    result = results[0]

    annotated_image = result.plot()

    # Save annotated result
    output_filename = f"detected_{unique_name}.jpg"

    output_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        output_filename
    )

    saved = cv2.imwrite(output_path, annotated_image)

    if not saved:
        return jsonify({
            "error": "Could not save detection result"
        }), 500

    # Prepare detection details
    detections = []

    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        detections.append({
            "class": model.names[class_id],
            "confidence": round(confidence * 100, 2)
        })

    result_image = "/" + output_path.replace("\\", "/")

    # ---------------- SAVE HISTORY ----------------

    history_item = {
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "image": filename,
        "object_count": len(detections),
        "detections": detections,
        "result_image": result_image
    }

    detection_history.insert(0, history_item)

    # Keep only latest 20 records
    del detection_history[20:]

    # ---------------- SEND RESULT ----------------

    return jsonify({
        "success": True,
        "result_image": result_image,
        "object_count": len(detections),
        "detections": detections
    })


# ---------------- DETECTION HISTORY API ----------------

@app.route("/api/history")
def get_history():
    return jsonify(detection_history)


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    try:
        app.run(
            debug=True,
            use_reloader=False
        )
    finally:
        camera.release()
