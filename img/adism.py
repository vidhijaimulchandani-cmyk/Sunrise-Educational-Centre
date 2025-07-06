from PIL import Image
import numpy as np
import os
from rembg import remove

# Automatically find yash.jpg in the img folder
img_folder = 'img'
default_filename = 'yash.jpg'
input_path = os.path.join(img_folder, default_filename)
output_path = input_path  # Always overwrite in img folder

if not os.path.isfile(input_path):
    print(f"Error: File '{input_path}' does not exist.")
    exit(1)

# Desired background color (R, G, B)
new_bg_color = (255, 248, 225)  # #fff8e1

# Open the image and remove background
img = Image.open(input_path).convert('RGBA')
img_no_bg = remove(img)

# Create a new background image
bg = Image.new('RGBA', img_no_bg.size, new_bg_color + (255,))
# Composite the character onto the new background
final_img = Image.alpha_composite(bg, img_no_bg)

# Save as JPG (convert to RGB)
final_img = final_img.convert('RGB')
final_img.save(output_path)

print(f"Saved edited image as {output_path}") 