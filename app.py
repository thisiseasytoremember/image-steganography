import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import io

DELIMITER = "#####"

def encode_image(image: Image.Image, secret_text: str):
    img = image.convert('RGB')
    img_array = np.array(img, dtype=np.uint8)
    full_text = secret_text + DELIMITER
    bits = np.unpackbits(np.frombuffer(full_text.encode('utf-8'), dtype=np.uint8))
    if len(bits) > img_array.size:
        return None, "Error: Message is too large for this image."
    flat_img = img_array.flatten()
    
    # 0xFE safely clears the LSB for uint8 without overflow
    flat_img[:len(bits)] = (flat_img[:len(bits)] & 0xFE) | bits
    return Image.fromarray(flat_img.reshape(img_array.shape)), "Success"

def decode_image(image: Image.Image) -> str:
    img = image.convert('RGB')
    flat_img = np.array(img, dtype=np.uint8).flatten()
    extracted_bytes = np.packbits(flat_img & 1).tobytes()
    delimiter_bytes = DELIMITER.encode('utf-8')
    delimiter_index = extracted_bytes.find(delimiter_bytes)
    if delimiter_index != -1:
        return extracted_bytes[:delimiter_index].decode('utf-8', errors='ignore')
    return ""

def generate_preset_image(preset_name: str) -> Image.Image:
    img = Image.new('RGB', (400, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    if preset_name == "Blue Gradient":
        for i in range(400):
            draw.line([(0, i), (400, i)], fill=(30, 80, (i * 2) % 256))
    elif preset_name == "Sunset Horizon":
        for i in range(400):
            draw.line([(0, i), (400, i)], fill=(255, (i % 256), 40))
    elif preset_name == "Emerald Field":
        for i in range(400):
            draw.line([(i, 0), (i, 400)], fill=(20, 140 - (i % 80), 60))
    elif preset_name == "Geometric Matrix":
        draw.rectangle([0, 0, 400, 400], fill=(220, 220, 220))
        draw.rectangle([50, 50, 350, 350], fill=(40, 40, 120))
        draw.rectangle([100, 100, 300, 300], fill=(200, 60, 60))
    return img

st.set_page_config(page_title="Image Steganography System", page_icon="🔒", layout="centered")
st.title("🔒 Image Steganography System")
st.markdown("A Cryptographic Tool for Concealing Textual Data inside Digital Images using LSB Encoding.")

tab_encode, tab_decode = st.tabs(["🔒 Encode Message", "🔓 Decode Message"])

with tab_encode:
    st.header("Encode Secret Data")
    source_type = st.radio("Select Image Input Method:", ["Upload Custom Image", "Select Preset Sample"], horizontal=True)
    input_img = None
    if source_type == "Upload Custom Image":
        uploaded_file = st.file_uploader("Upload Target Image (PNG recommended):", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            input_img = Image.open(uploaded_file)
    else:
        preset_choice = st.selectbox("Choose a Sample Image:", ["Blue Gradient", "Sunset Horizon", "Emerald Field", "Geometric Matrix"])
        input_img = generate_preset_image(preset_choice)
    if input_img:
        st.image(input_img, caption="Selected Carrier Image", width=350)
        secret_message = st.text_area("Enter Secret Message:", placeholder="Type payload here...")
        if st.button("Generate Stego-Image", type="primary"):
            if not secret_message.strip():
                st.warning("Please enter a message.")
            else:
                stego_image, status = encode_image(input_img, secret_message)
                if stego_image:
                    st.success("Payload embedded successfully!")
                    st.image(stego_image, caption="Generated Stego-Image", width=350)
                    buffer = io.BytesIO()
                    stego_image.save(buffer, format="PNG")
                    st.download_button(label="📥 Download Encoded PNG Image", data=buffer.getvalue(), file_name="stego_image.png", mime="image/png")
                else:
                    st.error(status)

with tab_decode:
    st.header("Decode Secret Data")
    uploaded_stego_file = st.file_uploader("Upload Stego-Image for Extraction:", type=["png"], key="decoder_uploader")
    if uploaded_stego_file:
        stego_input_img = Image.open(uploaded_stego_file)
        st.image(stego_input_img, caption="Uploaded Stego-Image", width=350)
        if st.button("Extract Message", type="primary"):
            extracted_payload = decode_image(stego_input_img)
            if extracted_payload:
                st.success("Extraction Completed Successfully!")
                st.text_area("Extracted Secret Message:", value=extracted_payload, height=150, disabled=True)
            else:
                st.error("No valid hidden payload detected.")
