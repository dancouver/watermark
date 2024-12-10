import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
import platform

# Create the main window
root = tk.Tk()
root.title("Image Watermarker")
root.geometry("400x200")

# Global variables to store image and path
img = None
img_path = None


# Function to upload an image
def upload_image():
    global img, img_path
    img_path = filedialog.askopenfilename(
        title="Select an Image", filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if img_path:
        img = Image.open(img_path)
        lbl_image_path.config(text="Image Loaded: " + os.path.basename(img_path))


# Function to dynamically adjust font size based on image width
def get_font_for_text(draw, text, img_width, font_path=None):
    # Start with a large font size
    font_size = 100
    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default()

    # Reduce font size until it fits within the image width (with padding)
    while True:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width < img_width * 0.9:  # Text should occupy 90% of the image width
            break
        font_size -= 5
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()

    return font


# Function to add watermark and save the image
def add_watermark():
    watermark_text = entry_watermark.get()
    if not img_path or not watermark_text:
        messagebox.showwarning("Input Error", "Please upload an image and enter watermark text!")
        return

    # Open the image
    image = img.convert("RGBA")  # Ensure the image is in RGBA mode (supports transparency)
    width, height = image.size

    # Create a transparent overlay for the watermark
    txt_overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))  # Fully transparent

    # Create a draw object on the overlay
    draw = ImageDraw.Draw(txt_overlay)

    # Set the font size dynamically based on the image width
    font_path = "arial.ttf"  # Path to your custom font (change if needed)
    font = get_font_for_text(draw, watermark_text, image.width, font_path)

    # Calculate the bounding box and the size of the text
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Calculate position to center the watermark
    position = ((width - text_width) // 2, (height - text_height) // 2)

    # Add the watermark text to the transparent overlay (RGBA color with transparency)
    watermark_color = (255, 255, 255, 100)  # White text with alpha transparency (100 = semi-transparent)
    draw.text(position, watermark_text, font=font, fill=watermark_color)

    # Combine the original image with the overlay
    watermarked_image = Image.alpha_composite(image, txt_overlay)

    # Convert back to RGB before saving (if alpha channel is not needed in the final image)
    final_image = watermarked_image.convert("RGB")

    # Save the watermarked image with '-wm' suffix
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    ext = os.path.splitext(img_path)[1]
    new_image_path = os.path.join(os.path.dirname(img_path), base_name + "-wm" + ext)

    final_image.save(new_image_path)

    messagebox.showinfo("Success", f"Watermarked image saved as {new_image_path}")

    # Automatically open the saved image
    open_file(new_image_path)


# Function to open the saved image file automatically
def open_file(filepath):
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        else:  # Linux
            subprocess.call(["xdg-open", filepath])
    except Exception as e:
        messagebox.showerror("Error", f"Unable to open the file: {e}")


# GUI Components
btn_upload = tk.Button(root, text="Upload Image", command=upload_image)
btn_upload.pack(pady=10)

lbl_image_path = tk.Label(root, text="No image uploaded")
lbl_image_path.pack()

lbl_watermark = tk.Label(root, text="Enter Watermark Text:")
lbl_watermark.pack(pady=5)

entry_watermark = tk.Entry(root, width=30)
entry_watermark.pack(pady=5)

btn_save = tk.Button(root, text="Add Watermark and Save", command=add_watermark)
btn_save.pack(pady=10)

# Start the main loop
root.mainloop()
