import os
import json
import numpy as np
from PIL import Image
import tensorflow as tf

# Folder this file lives in — makes the paths below work no matter
# where the calling code is running from
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

model = tf.keras.models.load_model(os.path.join(MODEL_DIR, "tomato_cnn.keras"))

with open(os.path.join(MODEL_DIR, "class_indices.json")) as f:
    meta = json.load(f)

IMG_SIZE = meta["img_size"]
KEYS_BY_INDEX = meta["keys_by_index"]


def predict_disease(image_path):
    """Takes a path to a leaf photo, returns (predicted_class, confidence_percent)."""
    img = Image.open(image_path).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr = np.expand_dims(np.array(img, dtype="float32"), axis=0)

    probabilities = model.predict(arr, verbose=0)[0]
    best_index = np.argmax(probabilities)

    predicted_class = KEYS_BY_INDEX[best_index]
    confidence = float(probabilities[best_index]) * 100

    return predicted_class, confidence
