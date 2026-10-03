import cv2

class SiftDetection():  ##############Note: should use sift.detectAndCompute instead of sift.detect()
    def __init__(self, template_image_gray):
        #store template
        self.sift_template = template_image_gray

        #initialize sift detector
        self.sift = cv2.SIFT_create()

        #precompute template keypoints
        #TEMPLATE:
        #find keypoints of template image (grayed out version) --> can put a mask
        template_keypoints = self.sift.detect(self.sift_template, None)
        print(f"Number of Template Keypoints: {len(template_keypoints)}")
        #draw those keypoints --> use flags for better keypoints
        self.template_image_keypoints = cv2.drawKeypoints(self.sift_template, template_keypoints, None)
        #make a new image with the keypoints on it
        cv2.imwrite('sift_keypoints_template_image.jpg', self.template_image_keypoints)

    def sift_detect(self, cv_image):
        #convert frame to gray
        gray_frame = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        #FRAME:
        #do the same
        frame_keypoints = self.sift.detect(gray_frame, None)
        print(f"Number of Frame Keypoints: {len(frame_keypoints)}")
        frame_image_keypoints = cv2.drawKeypoints(gray_frame, frame_keypoints, None)
        cv2.imwrite('sift_frame_image_keypoints.jpg', frame_image_keypoints)

        return self.template_image_keypoints#, frame_image_keypoints
    
