
# Step 1: Import necessary libraries
import numpy as np
import cv2
import os
import tkinter as tk
from tkinter import filedialog
from matplotlib import pyplot as plt


# Step 2: Select an image from your PC
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
    raise SystemExit

# Step 3: Read the selected image
img = cv2.imread(image_path)

if img is None:
    raise ValueError("Unable to read the selected image.")

print("Selected image:", image_path)

# Find project directory
project_dir = os.path.dirname(os.path.abspath(__file__))

# Create folders for processed and output images
processed_dir = os.path.join(project_dir, "Processed-Set")
output_dir = os.path.join(project_dir, "Output-Set")

os.makedirs(processed_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Create output filenames from the input image name
base_name = os.path.splitext(os.path.basename(image_path))[0]


 
# STEP 4: CONVERT IMAGE TO GRAYSCALE
 

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

print("Step 1 completed: Grayscale conversion")

cv2.imwrite(
    os.path.join(processed_dir, f"gray-{base_name}.jpg"),
    gray
)


 
# STEP 5: APPLY AVERAGING FILTER
 

blur = cv2.blur(gray, (3, 3))

print("Step 2 completed: Averaging filter")

cv2.imwrite(
    os.path.join(processed_dir, f"blur-{base_name}.jpg"),
    blur
)


 
# STEP 6: APPLY LOGARITHMIC TRANSFORMATION
 

img_float = blur.astype(np.float32)
max_log = np.log1p(np.max(img_float))

if max_log > 0:
    img_log = (
        np.log1p(img_float) / max_log * 255
    ).astype(np.uint8)
else:
    img_log = blur.copy()

print("Step 3 completed: Logarithmic transformation")

cv2.imwrite(
    os.path.join(processed_dir, f"img_log-{base_name}.jpg"),
    img_log
)


 
# STEP 7: APPLY BILATERAL FILTER
 

bilateral = cv2.bilateralFilter(
    img_log,
    5,
    75,
    75
)

print("Step 4 completed: Bilateral filtering")

cv2.imwrite(
    os.path.join(processed_dir, f"bilateral-{base_name}.jpg"),
    bilateral
)


 
# STEP 8: CANNY EDGE DETECTION
 

edges = cv2.Canny(
    bilateral,
    100,
    200
)

print("Step 5 completed: Canny edge detection")

cv2.imwrite(
    os.path.join(processed_dir, f"edges-{base_name}.jpg"),
    edges
)


 
# STEP 9: MORPHOLOGICAL CLOSING
 

kernel = np.ones((5, 5), np.uint8)

closing = cv2.morphologyEx(
    edges,
    cv2.MORPH_CLOSE,
    kernel
)

print("Step 6 completed: Morphological closing")

cv2.imwrite(
    os.path.join(processed_dir, f"closing-{base_name}.jpg"),
    closing
)


 
# STEP 10: ORB FEATURE DETECTION
 

orb = cv2.ORB_create(nfeatures=1500)

keypoints, descriptors = orb.detectAndCompute(
    closing,
    None
)

featuredImg = cv2.drawKeypoints(
    closing,
    keypoints,
    None,
    color=(0, 255, 0),
    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
)

print("Step 7 completed: ORB feature detection")
print("Number of keypoints detected:", len(keypoints))


 
# STEP 11: SAVE FINAL OUTPUT IMAGE
 

output_path = os.path.join(
    output_dir,
    f"CrackDetected-{base_name}.jpg"
)

success = cv2.imwrite(output_path, featuredImg)

if not success:
    raise IOError("Failed to save the final output image.")

print("Final output saved at:", output_path)


 
# STEP 12: DISPLAY ALL PROCESSED IMAGES IN VS CODE
 

# Convert BGR images to RGB for correct Matplotlib colours
original_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
featured_rgb = cv2.cvtColor(featuredImg, cv2.COLOR_BGR2RGB)

# Prepare all processing stages
images = [
    ("1. Original Image", original_rgb, None),
    ("2. Grayscale", gray, "gray"),
    ("3. Averaging Filter", blur, "gray"),
    ("4. Log Transformation", img_log, "gray"),
    ("5. Bilateral Filter", bilateral, "gray"),
    ("6. Canny Edge Detection", edges, "gray"),
    ("7. Morphological Closing", closing, "gray"),
    ("8. ORB Feature Detection", featured_rgb, None)
]

# Show all images in a 3 x 3 grid
fig, axes = plt.subplots(3, 3, figsize=(18, 13))

axes = axes.flatten()

for i, (title, image, cmap) in enumerate(images):
    if cmap:
        axes[i].imshow(image, cmap=cmap, vmin=0, vmax=255)
    else:
        axes[i].imshow(image)

    axes[i].set_title(title, fontsize=11)
    axes[i].axis("off")

# Hide the unused ninth subplot
axes[8].axis("off")

fig.suptitle(
    f"Road Crack Detection Pipeline: {base_name}",
    fontsize=16
)

plt.tight_layout()
plt.show()


 
# STEP 13: DISPLAY SUMMARY
 

print("\n========== PROCESSING SUMMARY ==========")
print("Input image:", image_path)
print("Grayscale image:", os.path.join(
    processed_dir, f"gray-{base_name}.jpg"
))
print("Blurred image:", os.path.join(
    processed_dir, f"blur-{base_name}.jpg"
))
print("Log transformed image:", os.path.join(
    processed_dir, f"img_log-{base_name}.jpg"
))
print("Bilateral image:", os.path.join(
    processed_dir, f"bilateral-{base_name}.jpg"
))
print("Canny edges:", os.path.join(
    processed_dir, f"edges-{base_name}.jpg"
))
print("Morphological closing:", os.path.join(
    processed_dir, f"closing-{base_name}.jpg"
))
print("Final output:", output_path)
print("ORB keypoints:", len(keypoints))
print("========================================")
