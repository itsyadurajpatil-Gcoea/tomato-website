import os
import sys
import uuid

from flask import Flask, render_template, request, url_for

sys.path.append("model")
from model.predict import predict_disease
from remedies import REMEDIES

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED = {"jpg", "jpeg", "png", "webp"}

# --- TWO-TIERED THRESHOLDS ---
REJECT_THRESHOLD = 66.0   # Below 66%: Pure junk (Spider-Man, logos). Reject entirely.
WARNING_THRESHOLD = 75.0  # Between 66% and 75%: Probably a leaf, but low quality. Show warning.

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("photo")

    if not file or file.filename == "":
        return render_template("index.html", error="Please choose a photo first.")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        return render_template("index.html", error="Please upload a JPG, PNG or WEBP image.")

    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    try:
        predicted_class, confidence = predict_disease(path)
        
        # 1. The Hard Reject (Junk Images)
        if confidence < REJECT_THRESHOLD:
            if os.path.exists(path):
                os.remove(path)
            return render_template(
                "index.html", 
                error="We couldn't clearly identify a tomato leaf. Please upload a clear, close-up photo."
            )
            
        # 2. Check if it falls in the "Warning" zone
        is_low_quality = confidence < WARNING_THRESHOLD
            
    except Exception:
        return render_template("index.html", error="Could not read that image. Please try another photo.")

    # 3. Pass the warning variable to the HTML template
    return render_template(
        "result.html",
        image_url=url_for("static", filename=f"uploads/{filename}"),
        uncertain=(predicted_class == "uncertain"),
        info=REMEDIES.get(predicted_class),
        confidence=round(confidence, 1),
        show_warning=is_low_quality  # <-- New variable passed to the frontend
    )

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)