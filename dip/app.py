from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

app = Flask(__name__)

def apply_nonlinear_filter(image):
    # Apply the non-linear filter (median filter)
    filtered_image = cv2.medianBlur(image, 3)
    return filtered_image

def morphological_pyramid_decomposition(image):
    # Apply morphological pyramid decomposition to each color channel
    decomposition = []
    for channel in cv2.split(image):
        pyramid = []
        pyramid.append(channel)  # Adding the original channel as the base of the pyramid

        for i in range(3):  # Number of pyramid levels
            channel = cv2.erode(channel, None, iterations=1)
            pyramid.append(channel)

        decomposition.append(pyramid)

    return decomposition

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, the browser also submits an empty part without filename
        if file.filename == '':
            return redirect(request.url)

        # Check if the file is allowed and has the right extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            # Read the image
            image = Image.open(BytesIO(file.read())).convert("RGB")
            image_array = np.array(image)

            # Apply the non-linear filter
            filtered_image_array = apply_nonlinear_filter(image_array)

            # Morphological pyramid decomposition
            decomposition = morphological_pyramid_decomposition(filtered_image_array)

            # Convert NumPy arrays back to PIL images for display
            decomposed_images = [
                [Image.fromarray(channel) for channel in pyramid]
                for pyramid in decomposition
            ]

            # Save the decomposed images
            decomposed_image_paths = []
            for i, pyramid_images in enumerate(decomposed_images):
                pyramid_paths = []
                for j, channel_image in enumerate(pyramid_images):
                    path = f"static/decomposed_image_{i}_{j}.png"
                    channel_image.save(path)
                    pyramid_paths.append(path)
                decomposed_image_paths.append(pyramid_paths)

            return render_template("index.html", original_image=image, decomposed_image_paths=decomposed_image_paths)

    return render_template("index.html", original_image=None, decomposed_image_paths=None)

# ... (remaining code)
if __name__ == "__main__":
    app.run(debug=True)