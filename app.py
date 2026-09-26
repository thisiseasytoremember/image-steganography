import gradio as gr
from PIL import Image
import numpy as np

DELIMITER = "#####"

def encode(img, secret_text):
    if img is None or not secret_text:
        return None, "Please provide both an image and text."
    img_array = np.array(img.convert('RGB'), dtype=np.uint8)
    bits = np.unpackbits(np.frombuffer((secret_text + DELIMITER).encode('utf-8'), dtype=np.uint8))
    if len(bits) > img_array.size:
        return None, "Message is too large for this image."
    flat = img_array.flatten()
    flat[:len(bits)] = (flat[:len(bits)] & ~1) | bits
    return Image.fromarray(flat.reshape(img_array.shape)), "Successfully Encoded!"

def decode(img):
    if img is None:
        return "Please upload an image."
    flat = np.array(img.convert('RGB'), dtype=np.uint8).flatten()
    extracted = np.packbits(flat & 1).tobytes()
    idx = extracted.find(DELIMITER.encode('utf-8'))
    if idx != -1:
        return extracted[:idx].decode('utf-8', errors='ignore')
    return "No hidden message found."

# UI Construction
with gr.Blocks(title="Image Steganography System") as app:
    gr.Markdown("# 🔒 Image Steganography System")
    
    with gr.Tab("Encode Message"):
        img_in = gr.Image(type="pil", label="Upload Carrier Image")
        msg_in = gr.Textbox(label="Secret Message", placeholder="Type here...")
        btn_enc = gr.Button("Encode Message", variant="primary")
        img_out = gr.Image(type="pil", label="Encoded Stego-Image")
        status_out = gr.Textbox(label="Status")
        btn_enc.click(encode, inputs=[img_in, msg_in], outputs=[img_out, status_out])

    with gr.Tab("Decode Message"):
        stego_in = gr.Image(type="pil", label="Upload Stego-Image")
        btn_dec = gr.Button("Extract Message", variant="primary")
        msg_out = gr.Textbox(label="Extracted Message")
        btn_dec.click(decode, inputs=[stego_in], outputs=msg_out)

app.launch()
