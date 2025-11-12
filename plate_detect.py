import cv2
import numpy as np
import os
import matplotlib.pyplot as plt # For debugging and visualization in python notebooks

# --- Loading the image --- #
def load_image(image_path):
    """function to load an image"""
    image = cv2.imread(image_path)
    return image

# --- Preprocessing the image --- #
def preprocess_image(image):
    """converts to grayscale and applies a bilateral filter"""
    # bilateral filter reduces noise while keeping edges sharp
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17) 
    return bfilter

# --- Image pyramid --- #
def pyramid(image, scale=1.5, min_size=(20, 20)):
    """this is just to generate the image pyramid"""
    yield image  # get the original image first

    while True:
        # this will compute the new dimensions of the image
        new_width = int(image.shape[1] / scale)
        new_height = int(image.shape[0] / scale)

        # this is basically stopping the function if the image is too small
        if new_width < min_size[0] or new_height < min_size[1]:
            break

        # this will resize and get the scaled image
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        yield image # get the next image in the pyramid


# --- Finding the license plate contour --- #
def find_plate_contour(processed_image):
    """this function finds the contour of the license plate since plates are rectangular in shape"""
    try:
        # apply gaussian blur to reduce noise and then canny edge detection to find edges
        blurred = cv2.GaussianBlur(processed_image, (7, 7), 0)
        edged = cv2.Canny(blurred, 50, 200)
        
        """ 
        findContours basically detects boundary points of shapes in the image
        and only keeps the 10 biggest contours which are likely to be the license plate
        """
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        plate_contour = None
        for c in contours:
            """
            this helps identify shapes with 4 sides
            since license plates are rectangular
            """
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * perimeter, True)

            if len(approx) == 4:
                (x, y, w, h) = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h

                # change as needed but these values work for Philippine plates
                if 1.5 < aspect_ratio < 4.5 and w > 30 and h > 15:
                    plate_contour = approx
                    break

        return plate_contour
    except Exception as e:
        print(f"Error in find_plate_contour: {e}")
        return None
    
# --- Cropping the license plate from the image --- #
def crop_plate(image, plate_contour, plate_type="car"):
    """crops and straightens the 4-point contour to a flat, top-down image. Supports car and motorcycle plate sizes"""
    try:
        # this is needed to ensure the points are in the correct order before straightening
        """
        credits to the following github repository for this part:
        https://github.com/snaily16/perspective_transformation/tree/e171b7dd69afe3f3fffd64a2ee77f2afb404127d/perspective_transform.py
        """
        pts = plate_contour.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)] # top-left
        rect[2] = pts[np.argmax(s)] # bottom-right

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)] # top-right
        rect[3] = pts[np.argmax(diff)] # bottom-left

        """
        Philippine License Plate Sizes (based on searching online):
        car plates use 390x140 while motorcycle plates use 235x135
        """        
        if plate_type == "motorcycle":
            target_w = 235
            target_h = 135
        else:  # default to car
            target_w = 390
            target_h = 140

        dst = np.array([
            [0, 0],
            [target_w - 1, 0],
            [target_w - 1, target_h - 1],
            [0, target_h - 1]], dtype="float32")

        """
        getPerspectiveTransform and warpPerspective are the functions that
        straighten the plate by applying a perspective transformation
        """
        M = cv2.getPerspectiveTransform(rect, dst)
        cropped = cv2.warpPerspective(image, M, (target_w, target_h))

        cropped_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        return cropped_gray
    
    except Exception as e:
        print(f"Error in crop_plate: {e}")
        return None
    
# --- Loading the character templates for matching --- #
def load_templates(template_directory="templates"):
    """loads all templates from a directory into a dictionary"""
    templates = {}
    if not os.path.exists(template_directory):
        print(f"Error: Template directory not found at {template_directory}")
        return None

    print(f"Loading templates from {template_directory}...")
    for filename in os.listdir(template_directory):
        if filename.endswith(('.png', '.jpg', '.bmp')):
            char_name = os.path.splitext(filename)[0]
            template_img = cv2.imread(os.path.join(template_directory, filename), 
                                      cv2.IMREAD_GRAYSCALE)
            
            if template_img is None: 
                continue
            
            # use THRESH_BINARY to match the segmented characters (white on black)
            _, template_thresh = cv2.threshold(template_img, 127, 255, cv2.THRESH_BINARY)
            
            # tightly crop the template to remove padding/whitespace
            """
            if not cropped, template matching may not work well due to extra borders
            since the segmented characters will be tightly cropped
            """
            coords = cv2.findNonZero(template_thresh)
            if coords is not None:
                x, y, w, h = cv2.boundingRect(coords)
                template_thresh = template_thresh[y:y+h, x:x+w]
            
            templates[char_name] = template_thresh
    
    print(f"Loaded {len(templates)} templates.")
    print(f"Available characters: {sorted(templates.keys())}")
    return templates

# --- Segmenting characters from the license plate --- #
def segment_characters(straightened_plate):
    """finds, straigthens, and sorts character contours"""
    try:
        # threshold the plate image
        """
        we used otsu's thresholding to get a binary image for better contour detection
        since the characters are usually darker on a lighter background
        """
        thresh = cv2.threshold(straightened_plate, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        character_data = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = w / float(h)
            if 0.1 < aspect_ratio < 1.0 and h > 20 and w > 5:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.float32(box)

                # order points: top-left, top-right, bottom-right, bottom-left
                s = box.sum(axis=1)
                diff = np.diff(box, axis=1)
                ordered_pts = np.array([
                    box[np.argmin(s)],
                    box[np.argmin(diff)],
                    box[np.argmax(s)],
                    box[np.argmax(diff)]
                ], dtype="float32")

                # standardize character size to be same as templates
                target_w, target_h = 40, 80
                dst = np.array([
                    [0, 0],
                    [target_w - 1, 0],
                    [target_w - 1, target_h - 1],
                    [0, target_h - 1]
                ], dtype="float32")

                M = cv2.getPerspectiveTransform(ordered_pts, dst)
                deskewed_char = cv2.warpPerspective(thresh, M, (target_w, target_h))
                character_data.append((x, deskewed_char))

        if not character_data:
            return None, None, None

        # sort by x-coordinate
        character_data.sort(key=lambda item: item[0])
        sorted_characters = [img for _, img in character_data]
        sorted_rois = [None] * len(sorted_characters)  # placeholder if ROIs needed, when removed, the program breaks :>

        return sorted_characters, sorted_rois, thresh

    except Exception as e:
        print(f"Error in segment_characters: {e}")
        return None, None, None

# --- Recognizing characters using template matching --- #
def recognize_characters_template_matching(character_images, templates):
    """identifies characters using cv2.matchTemplate."""
    if not templates:
        return "Template DB not loaded"
    if not character_images:
        return ""

    plate_text = ""
    
    # standardized size for matching
    TARGET_W = 40 
    TARGET_H = 80 

    for char_img in character_images:
        best_match_score = -1
        best_match_char = "?"

        # resize character to standard size
        char_resized = cv2.resize(char_img, (TARGET_W, TARGET_H), interpolation=cv2.INTER_AREA)

        for char_name, template in templates.items():
            # resize template to standard size
            template_resized = cv2.resize(template, (TARGET_W, TARGET_H), interpolation=cv2.INTER_AREA)

            # perform template matching and get the best match score
            result = cv2.matchTemplate(char_resized, template_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val > best_match_score:
                best_match_score = max_val
                best_match_char = char_name

        # confidence threshold for accepting a match (change as needed)
        if best_match_score > 0.4: 
            plate_text += best_match_char
        else:
            plate_text += "?"

    return plate_text

# --- Function to summarize the entire process --- #
def recognize_license_plate(image_path, template_directory="templates"):
    """Full process to recognize license plate from image."""
    image = load_image(image_path)
    preprocessed = preprocess_image(image)

    plate_contour = None
    for img in pyramid(preprocessed):
        plate_contour = find_plate_contour(img)
        if plate_contour is not None:
            break

    if plate_contour is None:
        return "License plate contour not found"

    cropped_plate = crop_plate(image, plate_contour)
    if cropped_plate is None:
        return "Failed to crop license plate"

    templates = load_templates(template_directory)
    segmented_chars, _, _ = segment_characters(cropped_plate)
    if segmented_chars is None:
        return "No characters segmented"

    recognized_text = recognize_characters_template_matching(segmented_chars, templates)
    return recognized_text

# --- For running the program as is --- #
if __name__ == "__main__":
    image_path = "test_images/img2.jpg" # change to actual test image path
    template_directory = "templates" # change to where templates directory is saved
    result = recognize_license_plate(image_path, template_directory)
    print(f"Recognized License Plate: {result}")