import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

# Load the model once
MODEL_PATH = r"C:\Users\abdhe\OneDrive\Documents\GitHub\BloodMark\model\model.h5"
model = load_model(MODEL_PATH)

st.title("Blood Group Detection from Fingerprint")

uploaded_file = st.file_uploader("Upload fingerprint image", type=["png", "jpg", "jpeg","BMP"])

if uploaded_file is not None:
    # Show uploaded image
    st.image(uploaded_file, caption='Uploaded Fingerprint', use_column_width=True)

    # Preprocess image and predict
    img = load_img(uploaded_file, target_size=(64, 64))
    img_array = np.expand_dims(img_to_array(img) / 255.0, axis=0)

    prediction = model.predict(img_array)
    blood_group_index = int(np.argmax(prediction))
    blood_groups = ["A", "B", "AB", "O", "-A", "-B", "-AB", "-O"]

    st.success(f"Predicted Blood Group: {blood_groups[blood_group_index]}")
