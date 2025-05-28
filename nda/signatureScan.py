import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from skimage import measure, morphology
from skimage.measure import regionprops
from skimage.color import label2rgb
import matplotlib.pyplot as plt
import os

# --- Step 1: Extract last page of PDF and save as image ---
def pdf_last_page_to_image(pdf_path: str, image_path, dpi: int = 200) -> str:
    doc = fitz.open(pdf_path)
    page = doc[-1]  # last page
    pix = page.get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(image_path)
    return image_path

# --- Step 2: Crop and paste on white background ---
def prepare_white_background_crop(image_path: str, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    image = cv2.imread(image_path, 0)  # grayscale
    cropped_gray = image[y1:y2, x1:x2]
    cropped = cv2.cvtColor(cropped_gray, cv2.COLOR_GRAY2BGR)

    height, width = image.shape[:2]
    white_bg = 255 * np.ones((height, width, 3), dtype=np.uint8)
    white_bg[y1:y1 + cropped.shape[0], x1:x1 + cropped.shape[1]] = cropped
    
    cv2.imwrite(image_path, white_bg)
    return image_path

# --- Step 3: Signature extraction ---
def extract_signature_from_image(path):
    
    img = cv2.imread(path, 0)
    _, img = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY)

    # read the input image
    img = cv2.threshold(img, 160, 255, cv2.THRESH_BINARY)[1]  # ensure binary

    # connected component analysis by scikit-learn framework
    blobs = img > img.mean()
    blobs_labels = measure.label(blobs, background=1)

    a4_small_size_outliar_constant = 70
    a4_big_size_outliar_constant = 9000
    
    if blobs_labels.max() <= 1:
        return None

    # remove the connected pixels are smaller than a4_small_size_outliar_constant
    pre_version = morphology.remove_small_objects(blobs_labels, a4_small_size_outliar_constant)
    # remove the connected pixels are bigger than threshold a4_big_size_outliar_constant 
    # to get rid of undesired connected pixels such as table headers and etc.
    component_sizes = np.bincount(pre_version.ravel())
    too_small = component_sizes > (a4_big_size_outliar_constant)
    too_small_mask = too_small[pre_version]
    pre_version[too_small_mask] = 0

    plt.imsave(path, pre_version)

    # read the pre-version
    img = cv2.imread(path, 0)
    # ensure binary
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # save the the result
    cv2.imwrite(path, img)
    return img

def is_there_signature(pdf_path, img_path):
    x1, y1, x2, y2 = 260, 277, 700, 360

    image_path = pdf_last_page_to_image(pdf_path, image_path=img_path)
    cropped_path = prepare_white_background_crop(image_path, x1, y1, x2, y2)
    signature_image = extract_signature_from_image(cropped_path)
    
    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Load in grayscale

    # Threshold the image to binary (black = 0, white = 255)
    _, binary = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)

    # Count the number of black pixels (non-zero pixels in the binary image)
    black_pixels = cv2.countNonZero(binary)
    
    os.remove(img_path)
    
    if black_pixels > 50 and black_pixels < 10000:
        return True
    return False

# --- Main Pipeline ---
if __name__ == "__main__":
    signature_exists = is_there_signature(pdf_path="nda.pdf", img_path="signature.png")