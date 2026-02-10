

import cv2
import pyautogui
from time import time
from math import hypot
import mediapipe as mp
import matplotlib.pyplot as plt
import config  # Configuration settings for booth system

# Instantiate the MediaPipe Pose classification utility.
mediapipe_pose = mp.solutions.pose

# Configure the Pose estimator for processing static images.
static_pose_detector = mediapipe_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, model_complexity=1)

# Configure the Pose estimator for processing video streams.
video_pose_detector = mediapipe_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.7,
                          min_tracking_confidence=0.7)

# Instantiate the MediaPipe drawing utility.
drawing_utils = mp.solutions.drawing_utils


def detect_pose_landmarks(image, pose_detector, show_landmarks=False, display_result=False):
    '''
    This function identifies pose landmarks on the primary subject in an image.
    Args:
        image:           The source image containing the subject to be analyzed.
        pose_detector:   The pose estimation model instance.
        show_landmarks:  Boolean flag to enable drawing landmarks on the output.
        display_result:  Boolean flag to show the original and processed images using matplotlib.
    Returns:
        annotated_image: The source image with landmarks overlay, if requested.
        detection_result: The raw output data containing pose landmarks.
    '''

    # Duplicate the source image to avoid modifying original data.
    annotated_image = image.copy()

    # Transform the input image from BGR to RGB color space.
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Execute the pose detection process.
    detection_result = pose_detector.process(image_rgb)

    # Verify if landmarks were found and drawing is requested.
    if detection_result.pose_landmarks and show_landmarks:
        # Overlay the pose landmarks on the copy of the image.
        drawing_utils.draw_landmarks(image=annotated_image, landmark_list=detection_result.pose_landmarks,
                                  connections=mediapipe_pose.POSE_CONNECTIONS,
                                  landmark_drawing_spec=drawing_utils.DrawingSpec(color=(255, 255, 255),
                                                                               thickness=3, circle_radius=3),
                                  connection_drawing_spec=drawing_utils.DrawingSpec(color=(49, 125, 237),
                                                                                  thickness=2, circle_radius=2))

    # Determine if visual display of the input and output is requested.
    if display_result:

        # Visualize both original and processed images side-by-side.
        plt.figure(figsize=[22, 22])
        plt.subplot(121)
        plt.imshow(image[:, :, ::-1])
        plt.title("Source Image")
        plt.axis('off')
        plt.subplot(122)
        plt.imshow(annotated_image[:, :, ::-1])
        plt.title("Processed Image")
        plt.axis('off')

    # Otherwise return the data.
    else:

        # Return the improved image and the detection data.
        return annotated_image, detection_result


def analyze_hand_gesture(image, detection_result, show_status=False, display_result=False):
    '''
    This function determines if the subject is clasping their hands together.
    Args:
        image:            The source image to evaluate.
        detection_result: The pose landmarks data from the detection phase.
        show_status:      Boolean flag to annotate the status on the image.
        display_result:   Boolean flag to show the final image using matplotlib.
    Returns:
        annotated_image:  The source image with status annotation, if requested.
        gesture_status:   String indicating if "Hands Joined" or "Hands Not Joined".
    '''

    # Retrieve image dimensions.
    img_height, img_width, _ = image.shape

    # Duplicate the image for annotation purposes.
    annotated_image = image.copy()

    # Extract coordinates for the left wrist landmark.
    left_wrist_coords = (detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.LEFT_WRIST].x * img_width,
                           detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.LEFT_WRIST].y * img_height)

    # Extract coordinates for the right wrist landmark.
    right_wrist_coords = (detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.RIGHT_WRIST].x * img_width,
                            detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.RIGHT_WRIST].y * img_height)

    # Compute the Euclidean distance between the wrists.
    wrist_distance = int(hypot(left_wrist_coords[0] - right_wrist_coords[0],
                                   left_wrist_coords[1] - right_wrist_coords[1]))

    # Evaluate distance against threshold to determine if hands are joined.
    if wrist_distance < 130:

        # Mark status as joined.
        gesture_status = 'Hands Joined'

        # Use green color for positive status.
        status_color = (0, 255, 0)

    # Otherwise assume hands are separate.
    else:

        # Mark status as not joined.
        gesture_status = 'Hands Not Joined'

        # Use red color for negative status.
        status_color = (0, 0, 255)

    # If annotation is requested, add text to the image.
    if show_status:
        # Add the gesture status label.
        cv2.putText(annotated_image, gesture_status, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, status_color, 3)

        # Add the calculated distance value.
        cv2.putText(annotated_image, f'Distance: {wrist_distance}', (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 2, status_color, 3)

    # If display is requested, show the plot.
    if display_result:

        # Show the annotated image.
        plt.figure(figsize=[10, 10])
        plt.imshow(annotated_image[:, :, ::-1])
        plt.title("Processed Image")
        plt.axis('off')

    # Otherwise return the results.
    else:

        # Return the annotated image and the status string.
        return annotated_image, gesture_status


def get_horizontal_movement(image, detection_result, show_position=False, display_result=False):
    '''
    This function calculates the horizontal alignment (left, center, right) of the subject.
    Args:
        image:            The source image to analyze.
        detection_result: The pose landmarks data.
        show_position:    Boolean flag to annotate the position on the image.
        display_result:   Boolean flag to show the final image using matplotlib.
    Returns:
        annotated_image:  The source image with position annotation.
        move_direction:   The determined direction ('Left', 'Center', 'Right').
    '''

    # Initialize variable for horizontal direction.
    move_direction = None

    # Get image dimensions.
    img_height, img_width, _ = image.shape

    # Duplicate current image for annotation.
    annotated_image = image.copy()

    # Get the x-coordinate for the right pinky (representing one side).
    # Note: Logic seems to use opposite landmarks for checking sides based on camera mirroring.
    left_side_x = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.RIGHT_PINKY].x * img_width)

    # Get the x-coordinate for the left pinky.
    right_side_x = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.LEFT_PINKY].x * img_width)

    # Retrieve shoulder x-coordinates for reference.
    right_shoulder_x_coord = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.RIGHT_SHOULDER].x * img_width)
    left_shoulder_x_coord = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.LEFT_SHOULDER].x * img_width)
    
    # Determine if subject is on the Left side.
    # Condition: If either hand moves significantly to one side relative to shoulder.
    if (right_side_x <= right_shoulder_x_coord or left_side_x <= right_shoulder_x_coord):
        # Update direction to Left.
        move_direction = 'Left'

    # Determine if subject is on the Right side.
    elif (right_side_x >= left_shoulder_x_coord or left_side_x >= left_shoulder_x_coord):

        # Update direction to Right.
        move_direction = 'Right'

    # Otherwise, assume Center position.
    else:
        # Update direction to Center.
        move_direction = 'Center'

    # If annotation enabled, draw the result.
    if show_position:
        # Display the direction text.
        cv2.putText(annotated_image, move_direction, (5, img_height - 10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

        # Draw a vertical reference line at the center.
        cv2.line(annotated_image, (img_width // 2, 0), (img_width // 2, img_height), (255, 255, 255), 2)

    # If display enabled, show the plot.
    if display_result:

        # Show the processed image.
        plt.figure(figsize=[10, 10])
        plt.imshow(annotated_image[:, :, ::-1])
        plt.title("Processed Image")
        plt.axis('off')

    # Otherwise return values.
    else:

        # Return the annotated image and direction string.
        return annotated_image, move_direction


def assess_vertical_posture(image, detection_result, initial_shoulder_y=300, show_posture=False, display_result=False):
    '''
    This function evaluates if the subject is Standing, Jumping, or Crouching.
    Args:
        image:              The source image.
        detection_result:   Pose landmarks data.
        initial_shoulder_y: unique reference Y-coordinate for standing height (calibration).
        show_posture:       Boolean flag to annotate the posture.
        display_result:     Boolean flag to show the image using matplotlib.
    Returns:
        annotated_image:    The image with posture status.
        body_state:         String indicating 'Jumping', 'Crouching', or 'Standing'.
    '''

    # Get image dimensions.
    img_height, img_width, _ = image.shape

    # Clone the image for drawing.
    annotated_image = image.copy()

    # Get shoulder Y-coordinates.
    left_shoulder_y = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.RIGHT_SHOULDER].y * img_height)
    right_shoulder_y = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.LEFT_SHOULDER].y * img_height)

    # Compute average shoulder Y-coordinate (current height level).
    current_shoulder_mid_y = abs(right_shoulder_y + left_shoulder_y) // 2

    # Get elbow Y-coordinates.
    left_elbow_y = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.RIGHT_ELBOW].y * img_height)
    right_elbow_y = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.LEFT_ELBOW].y * img_height)
    elbow_mid_y = (left_elbow_y + right_elbow_y) / 2

    # Get pinky finger Y-coordinates (hands level).
    left_pinky_y = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.RIGHT_PINKY].y * img_height)
    right_pinky_y = int(detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.LEFT_PINKY].y * img_height)
    pinky_mid_y = (left_pinky_y + right_pinky_y) / 2

    # Logic to determine posture:
    
    # Check for Jumping: Hands raised high (above shoulders).
    if pinky_mid_y < current_shoulder_mid_y:

        # Status is Jumping.
        body_state = 'Jumping'

    # Check for Crouching: Hands lowered (below elbows).
    elif pinky_mid_y > elbow_mid_y:

        # Status is Crouching.
        body_state = 'Crouching'

    # Otherwise, normal Standing.
    else:

        # Status is Standing.
        body_state = 'Standing'

    # Annotate if requested.
    if show_posture:
        # Draw the status text.
        cv2.putText(annotated_image, body_state, (5, img_height - 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

        # Draw the calibration line.
        cv2.line(annotated_image, (0, initial_shoulder_y), (img_width, initial_shoulder_y), (255, 255, 255), 2)

    # Display using matplotlib if requested.
    if display_result:

        # Show the annotated image.
        plt.figure(figsize=[10, 10])
        plt.imshow(annotated_image[:, :, ::-1])
        plt.title("Processed Image")
        plt.axis('off')

    # Otherwise return data.
    else:

        # Return the annotated image and posture state.
        return annotated_image, body_state


def start_game_interface(user_data=None, max_tries=3, score_tracker=None):
    # Setup video capture from default webcam.
    webcam_feed = cv2.VideoCapture(0)
    webcam_feed.set(3, 1280)
    webcam_feed.set(4, 960)

    # Establish a resizable window for the application.
    cv2.namedWindow('Subway Surfers with Pose Detection', cv2.WINDOW_NORMAL)

    # Variable to track timestamp of the last processed frame.
    last_frame_time = 0

    # Flag to indicate if the game session is active.
    is_playing = False

    # Track currently active lane (0=Left, 1=Center, 2=Right).
    lane_index = 1

    # Track current vertical state (0=Crouch, 1=Stand, 2=Jump).
    jump_crouch_index = 1

    # Store initial shoulder height for calibration.
    initial_shoulder_y = None

    # Counter for consecutive validation frames.
    frames_counter = 0

    # Threshold for required consecutive frames to trigger start.
    required_consecutive_frames = 10
    
    # Session management
    current_try = 0
    session_scores = []
    session_active = True


    # Main loop while webcam is active.
    while webcam_feed.isOpened() and session_active:

        # Capture a single frame.
        success, current_frame = webcam_feed.read()

        # If frame read failed, skip to next iteration.
        if not success:
            continue

        # Mirror the frame horizontally for intuitive interaction.
        current_frame = cv2.flip(current_frame, 1)

        # Get frame dimensions.
        frame_h, frame_w, _ = current_frame.shape

        # Run pose detection on current frame.
        current_frame, detection_result = detect_pose_landmarks(current_frame, video_pose_detector, show_landmarks=is_playing)

        # Proceed if landmarks were successfully detected.
        if detection_result.pose_landmarks:

            # Logic loop when game is active.
            if is_playing:
                # Display session info
                if user_data:
                    cv2.putText(current_frame, f"Player: {user_data['name']}", 
                               (10, frame_h - 90), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
                
                cv2.putText(current_frame, f"Try: {current_try}/{max_tries}", 
                           (10, frame_h - 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 3)
                
                if session_scores:
                    best_score = max(session_scores)
                    cv2.putText(current_frame, f"Best: {best_score}", 
                               (frame_w - 200, frame_h - 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
                
                # Check if game over detected by score tracker
                if score_tracker and score_tracker.is_game_over():
                    # Record the score
                    final_score = score_tracker.get_final_score()
                    
                    # If using manual entry mode OR OCR returned 0, ask for manual input
                    if hasattr(config, 'USE_MANUAL_SCORE_ENTRY') and config.USE_MANUAL_SCORE_ENTRY:
                        try:
                            from manual_score_entry import get_manual_score
                            player_name = user_data['name'] if user_data else "Player"
                            final_score = get_manual_score(current_try, player_name)
                            print(f"\n✓ Manual score entered: {final_score}")
                        except Exception as e:
                            print(f"⚠️ Could not get manual score: {e}")
                            # Keep OCR score (even if 0)
                    
                    session_scores.append(final_score)
                    print(f"\nTry {current_try} completed! Score: {final_score}")
                    
                    # Stop monitoring
                    score_tracker.stop_monitoring()
                    
                    # Check if session is complete
                    if current_try >= max_tries:
                        session_active = False
                        break
                    
                    # Reset for next try
                    is_playing = False
                    score_tracker.reset()
                    lane_index = 1
                    jump_crouch_index = 1

                # --- Horizontal Control Logic ---

                # Determine horizontal movement request from pose.
                current_frame, move_direction = get_horizontal_movement(current_frame, detection_result, show_position=True)
                print(move_direction, lane_index)
                
                # Check for Left movement.
                if (move_direction == 'Left' and lane_index != 0):
                    
                    # Simulate Left Arrow key press.
                    pyautogui.press('left')

                    # Decrement lane index.
                    lane_index -= 1

                # Check for Right movement.
                elif (move_direction == 'Right' and lane_index != 2):

                    # Simulate Right Arrow key press.
                    pyautogui.press('right')

                    # Increment lane index.
                    lane_index += 1
                elif move_direction == 'Center':
                    lane_index = 1
                # -------------------------------

            # Logic loop when waiting to start.
            else:
                # Display session info even when not playing
                if user_data:
                    cv2.putText(current_frame, f"Player: {user_data['name']}", 
                               (10, frame_h - 130), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
                
                # Show current try and instruction
                if current_try < max_tries:
                    next_try = current_try + 1
                    cv2.putText(current_frame, f'TRY {next_try}/{max_tries} - JOIN HANDS TO START', 
                               (5, frame_h - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
                else:
                    cv2.putText(current_frame, 'SESSION COMPLETE!', 
                               (5, frame_h - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 3)

            # --- Game Control & Start Logic ---

            # Check if hands are joined to initiate or resume.
            if analyze_hand_gesture(current_frame, detection_result)[1] == 'Hands Joined' and not is_playing:

                # Increment valid frame counter.
                frames_counter += 1

                # If threshold reached, take action.
                if frames_counter == required_consecutive_frames:

                    # --- Game Start Logic ---

                    # Check if we haven't exceeded max tries
                    if current_try < max_tries:
                        # Set game state to active.
                        is_playing = True
                        current_try += 1
                        
                        print(f"\n=== Starting Try {current_try}/{max_tries} ===")

                        # Calibrate shoulder height on first try
                        if initial_shoulder_y is None:
                            left_sh_y = int(
                                detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.RIGHT_SHOULDER].y * frame_h)

                            right_sh_y = int(
                                detection_result.pose_landmarks.landmark[mediapipe_pose.PoseLandmark.LEFT_SHOULDER].y * frame_h)

                            # Set the baseline Y-coordinate.
                            initial_shoulder_y = abs(right_sh_y + left_sh_y) // 2

                        # Click to start/resume game
                        if current_try == 1:
                            # First try - click to start
                            pyautogui.click(x=1300, y=800, button='left')
                        else:
                            # Subsequent tries - press space
                            pyautogui.press('space')
                        
                        # Start score monitoring
                        if score_tracker:
                            score_tracker.start_monitoring()

                    # --------------------------

                    # Reset frame counter.
                    frames_counter = 0

            # If hands are not joined, reset counter.
            else:

                # Reset counter.
                frames_counter = 0

            # ----------------------------------

            # --- Vertical Control Logic ---

            # Ensure we have calibration data.
            if initial_shoulder_y:

                # Check current posture relative to calibration.
                current_frame, body_state = assess_vertical_posture(current_frame, detection_result, initial_shoulder_y, show_posture=True)

                # Handle Jumping.
                if body_state == 'Jumping' and jump_crouch_index == 1:

                    # Simulate Up Arrow key.
                    pyautogui.press('up')

                    # Update state to Jumping.
                    jump_crouch_index += 1

                # Handle Crouching.
                elif body_state == 'Crouching' and jump_crouch_index == 1:

                    # Simulate Down Arrow key.
                    pyautogui.press('down')

                    # Update state to Crouching.
                    jump_crouch_index -= 1

                # Handle Return to Standing.
                elif body_state == 'Standing' and jump_crouch_index != 1:

                    # Reset state to Standing.
                    jump_crouch_index = 1

            # ------------------------------


        # Fallback if no landmarks detected.
        else:

            # Reset activation counter.
            frames_counter = 0

        # --- FPS Calculation ---

        # Record current time.
        current_frame_time = time()

        # Compute FPS if time difference is valid.
        if (current_frame_time - last_frame_time) > 0:
            # Calculate frames per second.
            fps_val = 1.0 / (current_frame_time - last_frame_time)

            # Display FPS on screen.
            cv2.putText(current_frame, 'FPS: {}'.format(int(fps_val)), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2,
                        (0, 255, 0), 3)

        # Update previous time for next iteration.
        last_frame_time = current_frame_time

        # -----------------------

        # Refresh the window with the new frame.
        cv2.imshow('Subway Surfers with Pose Detection', current_frame)

        # Check for key press (1ms wait).
        key_press = cv2.waitKey(1) & 0xFF

        # Exit if 'ESC' key (ASCII 27) is pressed.
        if (key_press == 27):
            break
        
        # Manual game over (SPACE key = ASCII 32) - triggers score entry
        elif (key_press == 32) and is_playing and score_tracker:
            print("\n⚠️ Manual game-over signal (SPACE pressed)")
            score_tracker.signal_manual_game_over()

    # Release webcam resources and close window.
    webcam_feed.release()
    cv2.destroyAllWindows()
    
    # Return the session scores
    return session_scores


if __name__ == '__main__':
    # Standalone mode (no session management)
    print("Running in standalone mode (no session management)")
    print("For full booth experience, run main.py instead")
    start_game_interface()