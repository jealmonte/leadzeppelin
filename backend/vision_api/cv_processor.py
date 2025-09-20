import cv2
import numpy as np
import pygame
import threading
import time

class SquareDetector:
    def __init__(self):
        self.previous_squares = []
        self.sound_cooldown = {}  # Prevent rapid sound triggering
        
        # Initialize pygame for sound
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.piano_notes = self.load_piano_sounds()
        
    def load_piano_sounds(self):
        """Load piano note sounds - for now we'll generate simple tones"""
        notes = {}
        for i, note in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']):
            # Generate a simple sine wave for each note
            frequency = 261.63 * (2 ** (i / 12))  # C major scale
            notes[note] = self.generate_tone(frequency, 0.5)
        return notes
    
    def generate_tone(self, frequency, duration):
        """Generate a simple sine wave tone"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
        
        arr = (arr * 32767).astype(np.int16)
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def detect_squares(self, frame):
        """Detect square shapes in the frame using adaptive thresholding"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use adaptive thresholding instead of fixed threshold
        # This handles varying lighting conditions much better
        thresh = cv2.adaptiveThreshold(
            blurred, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # or ADAPTIVE_THRESH_MEAN_C
            cv2.THRESH_BINARY_INV,  # INV because we want black lines to be white
            11,  # Block size - should be odd number
            2    # Constant subtracted from mean
        )
        
        # Alternative: Use Otsu's method for automatic threshold selection
        # _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((3,3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        squares = []
        for contour in contours:
            # Calculate area first to filter out noise
            area = cv2.contourArea(contour)
            if area < 500:  # Reduced minimum area for smaller squares
                continue
                
            # Calculate perimeter for approximation
            perimeter = cv2.arcLength(contour, True)
            
            # Approximate the contour to reduce points
            epsilon = 0.02 * perimeter  # 2% of perimeter
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if the shape has 4 points (potential square/rectangle)
            if len(approx) == 4:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Additional checks for square-like properties
                aspect_ratio = float(w) / h
                extent = area / (w * h)  # How much of bounding rect is filled
                solidity = area / cv2.contourArea(cv2.convexHull(contour))
                
                # More lenient criteria for hand-drawn squares
                if (0.5 <= aspect_ratio <= 2.0 and  # Allow some variation in aspect ratio
                    extent > 0.6 and  # At least 60% of bounding rect should be filled
                    solidity > 0.8):   # Shape should be fairly solid
                    
                    square_data = {
                        'contour': contour,
                        'center': (x + w//2, y + h//2),
                        'area': area,
                        'id': f"square_{x}_{y}",
                        'bbox': (x, y, w, h),
                        'aspect_ratio': aspect_ratio,
                        'solidity': solidity
                    }
                    squares.append(square_data)
        
        return squares, thresh  # Return thresh for debugging
    
    def check_occlusion(self, current_squares):
        """Check if squares are occluded compared to previous frame"""
        occluded_squares = []
        
        # Compare current squares with previous ones
        for prev_square in self.previous_squares:
            found_match = False
            prev_center = prev_square['center']
            prev_area = prev_square['area']
            
            for curr_square in current_squares:
                curr_center = curr_square['center']
                curr_area = curr_square['area']
                
                # Check if squares are in similar positions
                distance = np.sqrt((prev_center[0] - curr_center[0])**2 + 
                                 (prev_center[1] - curr_center[1])**2)
                area_diff = abs(prev_area - curr_area) / prev_area if prev_area > 0 else 1
                
                # More lenient matching criteria
                if distance < 80 and area_diff < 0.5:  # Increased tolerance
                    found_match = True
                    break
            
            # If previous square not found in current frame, it might be occluded
            if not found_match:
                occluded_squares.append(prev_square)
        
        return occluded_squares
    
    def play_piano_note(self, square_id):
        """Play a piano note based on square position"""
        current_time = time.time()
        
        # Prevent rapid triggering of same square
        if square_id in self.sound_cooldown:
            if current_time - self.sound_cooldown[square_id] < 0.3:  # Reduced cooldown
                return
        
        # Map square position to piano note
        notes = list(self.piano_notes.keys())
        note_index = hash(square_id) % len(notes)
        note = notes[note_index]
        
        # Play the sound
        self.piano_notes[note].play()
        self.sound_cooldown[square_id] = current_time
        
        print(f"Playing note {note} for square {square_id}")
    
    def process_frame(self, frame):
        """Main processing function"""
        current_squares, thresh_debug = self.detect_squares(frame)
        occluded_squares = self.check_occlusion(current_squares)
        
        # Play sounds for occluded squares
        for square in occluded_squares:
            self.play_piano_note(square['id'])
        
        # Draw detected squares on frame
        result_frame = frame.copy()
        for square in current_squares:
            # Draw contour in green
            cv2.drawContours(result_frame, [square['contour']], -1, (0, 255, 0), 2)
            
            # Draw center point
            center = square['center']
            cv2.circle(result_frame, center, 5, (255, 0, 0), -1)
            
            # Draw bounding box
            x, y, w, h = square['bbox']
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (255, 255, 0), 1)
            
            # Add text with square info
            cv2.putText(result_frame, f"AR:{square['aspect_ratio']:.2f}", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Update previous squares for next iteration
        self.previous_squares = current_squares
        
        return result_frame, current_squares, occluded_squares, thresh_debug

# Test function to help debug
def test_square_detection():
    """Test function to see what's being detected"""
    detector = SquareDetector()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        result_frame, squares, occluded, thresh_debug = detector.process_frame(frame)
        
        # Show both original processed frame and threshold for debugging
        cv2.imshow('Detected Squares', result_frame)
        cv2.imshow('Threshold Debug', thresh_debug)
        
        print(f"Detected {len(squares)} squares")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Uncomment to test
# test_square_detection()
