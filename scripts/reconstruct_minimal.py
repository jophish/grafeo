import cv2
import numpy as np
import glob

# Load the template for the "plus" sign
regular_mark_template = cv2.imread("./scripts/template.png", cv2.IMREAD_GRAYSCALE)
unique_mark_template = cv2.imread("./scripts/top_left_template.png", cv2.IMREAD_GRAYSCALE)

scale = 2
output_width = 1920*scale
output_height = 1080*scale

sift = cv2.SIFT_create()

# Detect and compute descriptors for the unique and regular templates
kp_unique, des_unique = sift.detectAndCompute(unique_mark_template, None)
kp_regular, des_regular = sift.detectAndCompute(regular_mark_template, None)


# Set up FLANN-based matcher parameters
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=10)
search_params = dict(checks=100)  # Adjust for speed vs. accuracy

# Initialize FLANN-based matcher
flann = cv2.FlannBasedMatcher(index_params, search_params)

WINDOW_NAME = 'window'
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
cv2.startWindowThread()

def align_image_to_unique_mark(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect and compute descriptors in the target image
    kp_image, des_image = sift.detectAndCompute(gray, None)
    
    # Match features between the unique template and the image using KNN
    matches = flann.knnMatch(des_unique, des_image, k=2)
    matches = sorted(matches, key=lambda x: x[0].distance)

    # Filter matches using Lowe's ratio test
    good_matches = []
    ratio_thresh = 0.7  # Adjust as needed
    for m, n in matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)

    good_matches = good_matches[:4]
    img3 = cv2.drawMatchesKnn(unique_mark_template,kp_unique,image,kp_image,[[m] for m in good_matches],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imshow(WINDOW_NAME, img3)
    cv2.waitKey(0)

    # Ensure we have enough good matches to compute homography
    if len(good_matches) < 4:
        raise ValueError("Not enough matches found to determine orientation.")
    
    # Extract matched points
    pts_unique = np.float32([kp_unique[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    pts_image = np.float32([kp_image[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    
    # Compute the homography matrix
    H, mask = cv2.findHomography(pts_unique, pts_image, cv2.RANSAC, 5.0)
    
    # Define the output size for the transformed image
    h, w = image.shape[:2]
    
    # Warp the image to align the unique mark to the top-left
    aligned_image = cv2.warpPerspective(image, H, (w, h))

    cv2.imshow(WINDOW_NAME, aligned_image)
    cv2.waitKey(0)
    return aligned_image, H

image_paths = glob.glob("scripts/assets/single_images/*.tif")

for i in range(len(image_paths)):
    path = image_paths[i]
    image = cv2.imread(path)
    align_image_to_unique_mark(image)

cv2.destroyAllWindows()

