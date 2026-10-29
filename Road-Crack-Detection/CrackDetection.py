# Import necessary libraries
import numpy as np
import cv2
import os
import tkinter as tk
from tkinter import filedialog
from matplotlib import pyplot as plt

# Step 1: Select an image from your PC
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

image_path = filedialog.askopenfilename(
    title="Select a Road Image for Crack Detection",
    filetypes=[
        ("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
        ("All files", "*.*")
    ]
)

root.destroy()

if not image_path:
    print("No image selected. Exiting program.")
    exit()

# Step 2: Read the selected image
img = cv2.imread(image_path)

if img is None:
    raise ValueError("Unable to read the selected image.")

print("Selected image:", image_path)

# Step 3: Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Step 4: Apply averaging filter
blur = cv2.blur(gray, (3, 3))

# Step 5: Apply logarithmic transformation
img_float = blur.astype(np.float32)
max_log = np.log1p(np.max(img_float))

if max_log > 0:
    img_log = (
        np.log1p(img_float) / max_log * 255
    ).astype(np.uint8)
else:
    img_log = blur.copy()

# Step 6: Apply bilateral filtering
bilateral = cv2.bilateralFilter(img_log, 5, 75, 75)

# Step 7: Canny edge detection
edges = cv2.Canny(bilateral, 100, 200)

# Step 8: Morphological closing
kernel = np.ones((5, 5), np.uint8)

closing = cv2.morphologyEx(
    edges, cv2.MORPH_CLOSE, kernel
)

# Step 9: Initialize ORB feature detector
orb = cv2.ORB_create(nfeatures=1500)

# Step 10: Detect image features
keypoints, descriptors = orb.detectAndCompute(closing, None)

featuredImg = cv2.drawKeypoints(
    closing,
    keypoints,
    None,
    color=(0, 255, 0)
)

print("Number of keypoints detected:", len(keypoints))

# Step 11: Save output in Output-Set folder
project_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(project_dir, "Output-Set")

os.makedirs(output_dir, exist_ok=True)

base_name = os.path.splitext(os.path.basename(image_path))[0]
output_path = os.path.join(
    output_dir, f"CrackDetected_{base_name}.jpg"
)

success = cv2.imwrite(output_path, featuredImg)

if not success:
    raise IOError("Failed to save the output image.")

print("Output saved at:", output_path)

# Step 12: Display original and processed images
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
output_rgb = cv2.cvtColor(featuredImg, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.imshow(img_rgb)
plt.title("Original Image")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(output_rgb)
plt.title("ORB Feature Detection")
plt.axis("off")

plt.tight_layout()
plt.show()