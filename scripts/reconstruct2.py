import cv2
import numpy as np
import glob

# Load the template for the "plus" sign
regular_mark_template = cv2.imread("./scripts/template.png", cv2.IMREAD_GRAYSCALE)
unique_mark_template = cv2.imread("./scripts/top_left_template.png", cv2.IMREAD_GRAYSCALE)

scale = 2
output_width = 1920*scale
output_height = 1080*scale

# Initialize ORB detector
orb = cv2.ORB_create(nfeatures=500)

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
    ratio_thresh = 0.5  # Adjust as needed
    for m, n in matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)

    img3 = cv2.drawMatchesKnn(unique_mark_template,kp_unique,image,kp_image,[[m] for m in good_matches],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imshow('name', img3)
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

    cv2.imshow('asd',aligned_image)
    cv2.waitKey(0)
    return aligned_image, H

def find_registration_marks(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_height, img_width = gray.shape
    
    # Detect and compute descriptors in the target image
    kp_image, des_image = sift.detectAndCompute(gray, None)

    # Match features for the unique mark
    matches_unique = bf.knnMatch(des_unique, des_image, k=2)

    good = []
    for m,n in matches_unique:
        if m.distance < 0.5*n.distance:
            good.append(m)

    img3 = cv2.drawMatchesKnn(unique_mark_template,kp_unique,image,kp_image,[[m] for m in good],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imshow('name', img3)
    cv2.waitKey(0)

    # Get the matching keypoints in both the template and the image
    src_pts = np.float32([kp_unique[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_image[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    # Compute the homography to align the unique mark to the top-left
    matrix, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

    # Apply the homography to warp the image
    aligned_image = cv2.warpPerspective(image, matrix, (image.shape[1]*2, image.shape[0]*2))
    cv2.imshow('warped', aligned_image)
    cv2.waitKey(0)

    # Filter matches to get the best ones for the unique mark
    unique_threshold = 2000  # Adjust as needed
    best_unique_matches = [m for m in matches_unique if m.distance < unique_threshold]
    
    if len(best_unique_matches) == 0:
        raise ValueError("Unique mark not found with sufficient confidence")
    
    # Estimate the position of the unique mark by averaging matched points
    unique_mark = np.mean([kp_image[m.trainIdx].pt for m in best_unique_matches], axis=0)
    unique_mark = tuple(map(int, unique_mark))  # Convert to integer coordinates

    new_img = cv2.circle(image, unique_mark, 20, (0,0,255), 5)
    cv2.imshow('test', new_img)
    cv2.waitKey(0)
    # Match features for the regular mark
    matches_regular = bf.match(des_regular, des_image)
    matches_regular = sorted(matches_regular, key=lambda x: x.distance)
    
    # Filter matches for the regular marks
    regular_threshold = 50  # Adjust as needed
    best_regular_matches = [m for m in matches_regular if m.distance < regular_threshold]

    # Define expected regions near corners
    corner_radius = 100  # Adjust based on image size
    corner_regions = {
        "top_right": (img_width - corner_radius, 0, img_width, corner_radius),
        "bottom_right": (img_width - corner_radius, img_height - corner_radius, img_width, img_height),
        "bottom_left": (0, img_height - corner_radius, corner_radius, img_height)
    }
    
    # Filter matches for regular marks by proximity to corners
    regular_marks = {}
    for m in best_regular_matches:
        pt = kp_image[m.trainIdx].pt
        mark_center = (int(pt[0]), int(pt[1]))
        print(mark_center)
        for corner_name, (x_min, y_min, x_max, y_max) in corner_regions.items():
            if x_min <= mark_center[0] <= x_max and y_min <= mark_center[1] <= y_max:
                if corner_name not in regular_marks or np.linalg.norm(np.array(mark_center) - np.array(regular_marks[corner_name])) > 10:
                    regular_marks[corner_name] = mark_center
                break

    print(regular_marks)
    if len(regular_marks) != 3:
        raise ValueError("Could not find exactly three regular marks near the corners")

    # Combine unique mark and regular marks
    all_marks = [unique_mark] + list(regular_marks.values())
    
    # Sort marks by relative position to ensure consistent order
    x_coords, y_coords = zip(*all_marks)
    center_x, center_y = np.mean(x_coords), np.mean(y_coords)
    
    sorted_marks = sorted(all_marks, key=lambda p: np.arctan2(p[1] - center_y, p[0] - center_x))

    # Reorder based on orientation with unique mark as top-left
    if unique_mark == sorted_marks[0]:  # Unique mark is top-left
        ordered_points = [sorted_marks[0], sorted_marks[1], sorted_marks[2], sorted_marks[3]]
    elif unique_mark == sorted_marks[1]:  # Unique mark is top-right
        ordered_points = [sorted_marks[1], sorted_marks[2], sorted_marks[3], sorted_marks[0]]
    elif unique_mark == sorted_marks[2]:  # Unique mark is bottom-right
        ordered_points = [sorted_marks[2], sorted_marks[3], sorted_marks[0], sorted_marks[1]]
    elif unique_mark == sorted_marks[3]:  # Unique mark is bottom-left
        ordered_points = [sorted_marks[3], sorted_marks[0], sorted_marks[1], sorted_marks[2]]

    return ordered_points
def orient_image(image, points, output_size=(output_width, output_height)):
    # Identify the unique top-left mark
    # Assume `find_registration_marks` returns the points but not ordered
    unique_mark = points[0]  # Assume first point in `points` list is unique for this example

    # Determine orientation by finding where the unique mark is located
    # Sort points based on their position relative to the unique mark
    sorted_points = sorted(points, key=lambda p: (p != unique_mark, np.arctan2(p[1] - unique_mark[1], p[0] - unique_mark[0])))

    # Rearrange sorted_points to enforce consistent order: top-left, top-right, bottom-right, bottom-left
    top_left, top_right, bottom_right, bottom_left = sorted_points

    # Define the target points (output corners) for a rectangle of fixed dimensions
    dst_points = np.array([
        [0, 0],
        [output_size[0] - 1, 0],
        [output_size[0] - 1, output_size[1] - 1],
        [0, output_size[1] - 1]
    ], dtype="float32")

    # Calculate the perspective transform
    src_points = np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Warp the image to align the region and orient it correctly
    oriented_image = cv2.warpPerspective(image, matrix, output_size)
    cv2.imshow('image', oriented_image)
    cv2.waitKey(0)
    return oriented_image

def extract_aligned_region(image, points, output_size=(output_width, output_height)):
    # Define the target points (output corners) for a rectangle of fixed dimensions
    dst_points = np.array([
        [0, 0],
        [output_width - 1, 0],
        [output_width - 1, output_height - 1],
        [0, output_height - 1]
    ], dtype="float32")

    # Compute the perspective transform matrix from the registration points to the output points
    src_points = np.array(points, dtype="float32")
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Apply the perspective warp
    warped_image = cv2.warpPerspective(image, matrix, output_size)
    warped_image = cv2.flip(warped_image, 0)
    return warped_image


image_paths = glob.glob("Scans/output/*.tif")  # Replace with your directory
output_path = './output/'

# choose codec according to format needed
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('video.avi', fourcc, 24.0, (output_width, output_height))

for i in range(len(image_paths)):
    print(i)
    path = image_paths[i]
    image = cv2.imread(path)
    #marks = find_registration_marks(image)
    align_image_to_unique_mark(image)
    warped_image = orient_image(image, marks)
    filename = f'{output_path}frame-{i+1}.png'

    cv2.imwrite(filename, warped_image)
    video.write(warped_image)

cv2.destroyAllWindows()
video.release()
