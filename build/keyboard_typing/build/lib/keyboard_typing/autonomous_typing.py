import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from constants import IMAGE_TOPIC, QOS
from geometry_msgs.msg import PoseStamped
import cv2
from cv_bridge import CvBridge
import numpy as np
import os
from ament_index_python.packages import get_package_share_directory
from keyboard_typing.template_matching import TemplateMatching
from keyboard_typing.corner_detection import CornerDetection
from keyboard_typing.aruco_alignment import ArucoAlignment
from keyboard_typing.typing_state import TypingState
from keyboard_typing.sift_detection import SiftDetection


class AutonomousTyping(Node):
    def __init__(self):
        super().__init__("autonomous_typing")

        #set typing state to aruco alignment
        self.state = TypingState.ARUCO_ALIGN

        #initialize a counter to count the number of times an alignment is consistently a success (within margin of error)
        self.stability_counter = 0
        self.STABILITY_THRESHOLD = 10

        self.bridge = CvBridge()

        #allows for you to have access to template image
        package_share_dir = get_package_share_directory("keyboard_typing")
        self.FULL_KEYBOARD_IMAGE_PATH = os.path.join(package_share_dir, "resource", "full_keyboard_template_image.jpg")
        self.TEMPLATE_IMAGE_PATH = os.path.join(package_share_dir, "resource", "template_image.jpg")

        #load template image
        #use imread so that is loads in grayscale already. --> might need to change if corner detection?
        self.sift_template = cv2.imread(self.FULL_KEYBOARD_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)

        if self.sift_template is None:
            self.get_logger().error(f"Failed to load template image: {self.FULL_KEYBOARD_IMAGE_PATH}")
            exit(1)

        #creates an instance for aruco alignment
        self.aruco_detector = ArucoAlignment(bridge=self.bridge)
        if self.aruco_detector is not None:
            self.get_logger().info("Aruco detector has been initialized")

        #creates an instance for template matching
        self.template_matcher = TemplateMatching(self.TEMPLATE_IMAGE_PATH, self.FULL_KEYBOARD_IMAGE_PATH)
        if self.template_matcher is not None:
            self.get_logger().info("Template matcher has been initialized")

        #creates an instance for corner detection
        #self.corner_detector = CornerDetection(image=cv_image)
        #if self.corner_detector is not None:
        #    self.get_logger().info("Corner detector has been initialized")

        #creates an instance for sift detection
        self.sift_detector = SiftDetection(self.sift_template)
        if self.sift_detector is not None:
            self.get_logger().info("Sift detector has been initialized")

        #expected outputs
        self.aruco_pose = None
        self.template_score = None
        self.xy_offset = None


        #subscribes to IMAGE_TOPIC
        #self.create_subscription(Image, IMAGE_TOPIC, self.image_callback, QOS)
        self.create_subscription(Image, "/camera_node/depth/image_raw", self.depth_callback, 10)
        self.create_subscription(Image, "/camera_node/rgb/image_raw", self.rgb_callback, 10)
        #publishes PoseStamped message??
        self.publisher = self.create_publisher(PoseStamped, "autonomous_typing/pose", 10)

        #will decide if current stage has been completed/successful in control loop and will move to next stage
        self.create_timer(0.1, self.control_loop)

        self.get_logger().info("AutonomousTyping running")

    def rgb_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            #use Aruco Detection to make robot parallel to keyboard
            if self.state == TypingState.ARUCO_ALIGN:
                self.aruco_pose = self.aruco_detector.get_keyboard_pose(msg)
            #use Template Matching to confirm distance from keyboard
            elif self.state == TypingState.DISTANCE_CHECK:
                self.template_score = self.template_matcher.template_match(gray)
            #use SIFT/Corner Detection to align XY position
            elif self.state == TypingState.XY_ALIGN:
                self.xy_offset = (0.0, 0.0) #self.corner_detector.compute_offset(cv_image)
                #self.xy_offset = self.sift_detector.compute_offset(cv_image)

            #Aruco Detection --> make so parallel to keyboard
            #pose = self.aruco_detector.get_keyboard_pose(msg)
            #if pose is not None:
            #    self.publisher.publish(pose)
            #    self.get_logger().info(f"Published keyboard pose: {pose}")
            
            #Use template matching to confirm correct distance
            #cv_image_gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            #template_matching_output = TemplateMatching(self.TEMPLATE_IMAGE_PATH, image=cv_image_gray)
            #result = template_matching_output.template_match()
            #self.get_logger().info(f"Template Matching Done")

            #Use corner/sift detection to fix xy position
            #corner_detection_output = CornerDetection(image=cv_image)
            #corner_detection_output.corner_detect()
            #self.get_logger().info(f"Corner Detection Done")

            #keypoints = self.sift_detector(cv_image)  # Pass current frame for keypoint detection


        except Exception as e:
            self.get_logger().error(f"Something broke in rgb_callback: {e}")
        #return None

    def depth_callback(self, msg):
        try:
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

        except Exception as e:
            self.get_logger().info(f"Something broke in depth_callback: {e}")
        return None

    def control_loop(self):
        try:
            #____ARUCO ALIGNMENT STAGE____
            if self.state == TypingState.ARUCO_ALIGN:
                if self.aruco_pose is None:
                    #wait for result
                    return
                
                #IMPLEMENT THIS
                #yaw_error = extract_yaw(self.aruco_pose)
                #if abs(yaw_error) < 1.0:
                #    self.stability_counter += 1
                #else:
                #    self.stability_counter = 0
                    #IMPLEMENT THIS
                #    self.rotate_arm(yaw_error)

                self.get_logger().info("Aruco pose recieved")
                self.stability_counter +=1

                #if stable for a certain number of subsequent checks, move to next stage
                if self.stability_counter > self.STABILITY_THRESHOLD: 
                    self.get_logger().info("Aruco alignment successful")
                    self.state = TypingState.DISTANCE_CHECK
                    self.stability_counter = 0
            
            #____DISTANCE CHECKING STAGE____ (Template Matching)
            elif self.state == TypingState.DISTANCE_CHECK:
                if self.template_score is None:
                    #wait for result
                    return 
                
                #distance threshold for correlation score (higher the better)
                #DISTANCE_THRESHOLD = 0.8
                #if self.template_score >=DISTANCE_THRESHOLD:
                #    self.stability_counter += 1
                #    self.get_logger().info(f"Distance stable: {self.stability_counter}/{self.STABILITY_THRESHOLD}")
                #else:
                #    self.stability_counter = 0
                #    #IMPLEMENT THIS
                #    self.adjust_distance(self.template_score)

                self.get_logger().info("Template score recieved")
                self.stability_counter +=1

                #if stable for a certain number of subsequent checks, move to next stage
                if self.stability_counter >= self.STABILITY_THRESHOLD: 
                    self.get_logger().info("Distance check successful")
                    self.state = TypingState.XY_ALIGN
                    self.stability_counter = 0

            #____XY ALIGNMENT STAGE____ (Corner Detection/SIFT Detection)
            elif self.state == TypingState.XY_ALIGN:
                if self.xy_offset is None:
                    #wait for result
                    return 
                #dx, dy = self.xy_offset
                #tolerance in meters? --> cm?
                #XY_THRESHOLD = 0.005
                #if abs(dx) < XY_THRESHOLD and abs(dy) < XY_THRESHOLD:
                #    self.stability_counter += 1
                #    self.get_logger().info(f"XY stable: {self.stability_counter}/{self.STABILITY_THRESHOLD}")
                #else:
                #    self.stability_counter = 0
                #    #IMPLEMENT THIS
                #    self.adjust_xy(dx, dy)
                
                self.get_logger().info("XY offset recieved")
                self.stability_counter +=1
                
                #if stable for a certain number of subsequent checks, move to next stage
                if self.stability_counter >= self.STABILITY_THRESHOLD: 
                    self.get_logger().info("XY alignment successful")
                    self.state = TypingState.ALIGNED
                    self.stability_counter = 0

            #____KEYBOARD TYPING STAGE____
            elif self.state == TypingState.ALIGNED:
                #IMPLEMENT THIS
                pass

        except Exception as e:
            self.get_logger().error(f"Error in control loop: {e}")

    def extract_yaw(self, pose_stamped):
        return
    
    def rotate_arm(self, yaw_error):
        self.get_logger().info(f"Rotate arm by {yaw_error:.2f} degrees")
        return
    
    def adjust_distance(self, score):
        self.get_logger().info(f"Adjusting distance based on template score: {score:.2f}")

    def adjust_xy(self, dx, dy):
        self.get_logger().info(f"Adjust XY: dx={dx:.3f}, dy={dy:.3f}")

def main(args=None):
    rclpy.init(args=args)
    node = AutonomousTyping()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down autonomous typing")


if __name__ == "__main__":
    main()
