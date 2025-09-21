import cv2
import numpy as np
import pygame
import threading
import time


class SquareDetector:
    def __init__(self, instrument_type="piano"):
        self.sound_cooldown = {}
        self.registered_square_positions = {}
        self.finger_in_square = {}
        self.frame_count = 0
        
        # Instrument configuration
        self.instrument_type = instrument_type
        
        # Square-to-note mapping
        self.square_note_assignments = {}
        self.available_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        
        # Initialize pygame for sound
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.instrument_sounds = self.load_instrument_sounds()
        
    def load_instrument_sounds(self):
        """Load sounds based on instrument type"""
        if self.instrument_type == "piano":
            return self.load_piano_sounds()
        elif self.instrument_type == "drums":
            return self.load_drum_sounds()
        elif self.instrument_type == "flute":
            return self.load_flute_sounds()
        else:
            return self.load_piano_sounds()  # Default fallback
    
    def load_piano_sounds(self):
        """Load piano note sounds"""
        notes = {}
        note_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        base_frequency = 261.63  # C4
        
        for i, note in enumerate(note_names):
            frequency = base_frequency * (2 ** (i / 12))
            notes[note] = self.generate_piano_tone(frequency, 0.8)
        
        return notes
    
    def load_drum_sounds(self):
        """Load drum sounds - different percussion for each 'note'"""
        drums = {}
        # Map musical notes to drum sounds with different frequencies and characteristics
        drum_mapping = {
            'C': {'freq': 80, 'type': 'kick'},      # Kick drum
            'D': {'freq': 120, 'type': 'snare'},    # Snare
            'E': {'freq': 200, 'type': 'hihat'},    # Hi-hat
            'F': {'freq': 150, 'type': 'tom1'},     # Tom 1
            'G': {'freq': 100, 'type': 'tom2'},     # Tom 2
            'A': {'freq': 250, 'type': 'crash'},    # Crash
            'B': {'freq': 220, 'type': 'ride'},     # Ride
            'Db': {'freq': 80, 'type': 'kick'},     # Alternative kick
            'Eb': {'freq': 140, 'type': 'snare'},   # Alternative snare
            'Gb': {'freq': 180, 'type': 'tom3'},    # Tom 3
            'Ab': {'freq': 220, 'type': 'hihat'},   # Open hi-hat
            'Bb': {'freq': 280, 'type': 'crash'}    # Splash
        }
        
        for note, drum_info in drum_mapping.items():
            drums[note] = self.generate_drum_sound(drum_info['freq'], drum_info['type'])
        
        return drums
    
    def load_flute_sounds(self):
        """Load flute sounds - pure sine waves with harmonic overtones"""
        notes = {}
        note_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        base_frequency = 523.25  # C5 (higher octave for flute)
        
        for i, note in enumerate(note_names):
            frequency = base_frequency * (2 ** (i / 12))
            notes[note] = self.generate_flute_tone(frequency, 1.0)
        
        return notes
    
    def generate_piano_tone(self, frequency, duration):
        """Generate piano-like tone with attack and decay"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            # Piano has complex harmonics
            fundamental = np.sin(2 * np.pi * frequency * i / sample_rate)
            second_harmonic = 0.5 * np.sin(2 * np.pi * frequency * 2 * i / sample_rate)
            third_harmonic = 0.25 * np.sin(2 * np.pi * frequency * 3 * i / sample_rate)
            
            # Apply envelope (attack and decay)
            envelope = np.exp(-3 * i / frames)  # Exponential decay
            if i < frames * 0.1:  # Attack phase
                envelope *= (i / (frames * 0.1))
            
            arr[i] = (fundamental + second_harmonic + third_harmonic) * envelope
        
        arr = (arr * 16383).astype(np.int16)  # Reduced volume
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def generate_drum_sound(self, frequency, drum_type):
        """Generate drum sounds with different characteristics"""
        sample_rate = 22050
        duration = 0.3  # Shorter duration for drums
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        if drum_type == 'kick':
            # Low frequency with quick decay
            for i in range(frames):
                envelope = np.exp(-8 * i / frames)
                arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate) * envelope
        
        elif drum_type == 'snare':
            # Mix of tone and noise
            for i in range(frames):
                envelope = np.exp(-5 * i / frames)
                tone = np.sin(2 * np.pi * frequency * i / sample_rate)
                noise = np.random.normal(0, 0.3)
                arr[i] = (0.3 * tone + 0.7 * noise) * envelope
        
        elif drum_type == 'hihat':
            # High frequency noise
            for i in range(frames):
                envelope = np.exp(-10 * i / frames)
                noise = np.random.normal(0, 0.5)
                high_freq = np.sin(2 * np.pi * frequency * i / sample_rate)
                arr[i] = (0.2 * high_freq + 0.8 * noise) * envelope
        
        else:  # toms, crash, ride
            # Metallic sound with overtones
            for i in range(frames):
                envelope = np.exp(-4 * i / frames)
                fundamental = np.sin(2 * np.pi * frequency * i / sample_rate)
                overtone = 0.3 * np.sin(2 * np.pi * frequency * 1.6 * i / sample_rate)
                arr[i] = (fundamental + overtone) * envelope
        
        arr = (arr * 20000).astype(np.int16)  # Higher volume for drums
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def generate_flute_tone(self, frequency, duration):
        """Generate flute-like tone - pure and airy"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            # Flute is mostly fundamental with some second harmonic
            fundamental = np.sin(2 * np.pi * frequency * i / sample_rate)
            second_harmonic = 0.2 * np.sin(2 * np.pi * frequency * 2 * i / sample_rate)
            
            # Add slight breathiness (noise)
            breath = np.random.normal(0, 0.05)
            
            # Gentle attack and sustain
            if i < frames * 0.15:  # Attack
                envelope = i / (frames * 0.15)
            elif i > frames * 0.8:  # Release
                envelope = (frames - i) / (frames * 0.2)
            else:  # Sustain
                envelope = 1.0
            
            arr[i] = (fundamental + second_harmonic + breath) * envelope
        
        arr = (arr * 12000).astype(np.int16)  # Moderate volume
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def get_instrument_display_name(self):
        """Get display name for the instrument"""
        display_names = {
            "piano": "🎹 Piano",
            "drums": "🥁 Drums", 
            "flute": "🪈 Flute"
        }
        return display_names.get(self.instrument_type, f"🎵 {self.instrument_type.title()}")
    
    
    def detect_duplicate_notes(self):
        """Check for duplicate note assignments and return True if found"""
        assignments = list(self.square_note_assignments.values())
        unique_assignments = set(assignments)
        
        if len(assignments) != len(unique_assignments):
            print(f"🚨 DUPLICATE NOTES DETECTED: {assignments}")
            return True
        return False
    
    def force_scale_based_assignment(self, stable_squares):
        """Force assignment based on current scale - squares always get sequential scale notes"""
        print(f"🎼 SCALE ASSIGNMENT: Assigning notes from {self.available_notes} scale...")
        
        # Clear all current assignments
        self.square_note_assignments.clear()
        
        # Sort squares by position for consistent assignment (left-to-right, top-to-bottom)
        sorted_squares = sorted(stable_squares, key=lambda sq: (sq['center'][1] // 100, sq['center'][0]))
        
        # Assign notes in scale sequence
        for i, square in enumerate(sorted_squares):
            square_id = square['id']
            note_index = i % len(self.available_notes)
            assigned_note = self.available_notes[note_index]
            self.square_note_assignments[square_id] = assigned_note
            print(f"🎼 SCALE: Square {i+1} → {assigned_note} (position {square['center']})")
        
        print(f"✅ SCALE ASSIGNMENT COMPLETE: {len(stable_squares)} squares mapped to scale")
        
        # Show the final mapping
        final_notes = [self.square_note_assignments[sq['id']] for sq in sorted_squares]
        print(f"🎵 Final scale mapping: {' → '.join(final_notes)}")
    
    def assign_notes_to_squares(self, stable_squares):
        """Assign notes to squares - always uses current scale sequence"""
        if not stable_squares:
            return
        
        # Sort squares by position (left-to-right, then top-to-bottom)
        sorted_squares = sorted(stable_squares, key=lambda sq: (sq['center'][1] // 100, sq['center'][0]))
        
        # Check if we have the right number of assignments
        current_assignments = len(self.square_note_assignments)
        stable_count = len(stable_squares)
        
        # If number of squares changed or we have duplicates, reassign everything
        if current_assignments != stable_count or self.detect_duplicate_notes():
            print(f"🔄 REASSIGNMENT NEEDED: {current_assignments} assignments vs {stable_count} squares")
            self.force_scale_based_assignment(stable_squares)
            return
        
        # Check if any square doesn't have an assignment
        missing_assignments = []
        for square in sorted_squares:
            if square['id'] not in self.square_note_assignments:
                missing_assignments.append(square)
        
        if missing_assignments:
            print(f"🔄 MISSING ASSIGNMENTS: {len(missing_assignments)} squares need notes")
            self.force_scale_based_assignment(stable_squares)
            return
        
        # Clean up assignments for squares that no longer exist
        existing_square_ids = [sq['id'] for sq in stable_squares]
        assignments_to_remove = []
        for square_id in self.square_note_assignments:
            if square_id not in existing_square_ids:
                assignments_to_remove.append(square_id)
        
        if assignments_to_remove:
            print(f"🗑️ CLEANING UP: {len(assignments_to_remove)} old assignments")
            for square_id in assignments_to_remove:
                del self.square_note_assignments[square_id]
            # After cleanup, reassign to ensure proper scale sequence
            self.force_scale_based_assignment(stable_squares)
            return
        
        # If we get here, everything is properly assigned
        assignments = [self.square_note_assignments.get(sq['id'], 'None') for sq in sorted_squares]
        print(f"🎵 Current scale assignments: {' | '.join([f'{i+1}:{note}' for i, note in enumerate(assignments)])}")

    def get_note_for_square(self, square_id):
        """Get the assigned note for a specific square"""
        return self.square_note_assignments.get(square_id, 'C')  # Default to C if not assigned

    def configure_note_sequence(self, notes):
        """Configure which notes to use and in what order"""
        self.available_notes = notes
        print(f"🎼 Note sequence configured: {' → '.join(notes)}")
        
        # Get current stable squares
        stable_squares = []
        for square_id, square_info in self.registered_square_positions.items():
            if square_info['stable']:
                stabilized_square = square_info['square_data'].copy()
                stabilized_square['center'] = square_info['averaged_center']
                stabilized_square['bbox'] = square_info['averaged_bbox']
                stable_squares.append(stabilized_square)
        
        # Force reassignment with new scale
        if stable_squares:
            print(f"🔄 SCALE CHANGE: Reassigning {len(stable_squares)} squares to new scale")
            self.force_scale_based_assignment(stable_squares)
        else:
            print("🔄 SCALE CHANGE: No squares to reassign yet")

    def set_custom_scale(self, scale_name):
        """Set predefined musical scales"""
        scales = {
            'major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
            'pentatonic': ['C', 'D', 'E', 'G', 'A'],
            'blues': ['C', 'Eb', 'F', 'Gb', 'G', 'Bb'],
            'minor': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb'],
            'fourths': ['C', 'F', 'G', 'D'],
            'simple': ['C', 'E', 'G', 'C'],  # Just C major chord
            'chord': ['C', 'E', 'G', 'B'],   # C major 7th chord
            'octave': ['C', 'C', 'C', 'C']   # All same note (for rhythm)
        }
        
        if scale_name in scales:
            self.configure_note_sequence(scales[scale_name])
            return True
        else:
            print(f"❌ Scale '{scale_name}' not found. Available: {list(scales.keys())}")
            return False
    
    def detect_small_squares_only(self, frame):
        """Detect only small drawn squares, ignore large hand shapes"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Light blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Simple threshold
        _, thresh = cv2.threshold(blurred, 110, 255, cv2.THRESH_BINARY_INV)
        
        # Light morphological operations
        kernel = np.ones((3,3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_squares = []
        frame_height, frame_width = frame.shape[:2]
        
        print(f"Simple detection: Processing {len(contours)} contours")
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # KEY: Very strict size limits to exclude hands
            if not (1500 <= area <= 8000):  # Small squares only!
                print(f"  Contour {i}: REJECTED - area {area:.0f} outside [1500-8000] (hands are bigger)")
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            
            # Skip edges
            if x < 40 or y < 40 or x + w > frame_width - 40 or y + h > frame_height - 40:
                print(f"  Contour {i}: REJECTED - too close to edges")
                continue
            
            # KEY: Strict size limits for width/height
            if not (30 <= w <= 120 and 30 <= h <= 120):  # Small squares only!
                print(f"  Contour {i}: REJECTED - size {w}x{h} outside [30-120] (hands are bigger)")
                continue
            
            # Reasonable aspect ratio
            aspect_ratio = float(w) / h
            if not (0.7 <= aspect_ratio <= 1.4):
                print(f"  Contour {i}: REJECTED - aspect ratio {aspect_ratio:.2f}")
                continue
            
            # Check if it has reasonable corners
            perimeter = cv2.arcLength(contour, True)
            epsilon = 0.04 * perimeter
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if not (4 <= len(approx) <= 6):
                print(f"  Contour {i}: REJECTED - {len(approx)} corners")
                continue
            
            # If we get here, it's a small square-like shape
            square_id = f"small_square_{x//50}_{y//50}"
            square_data = {
                'id': square_id,
                'center': (x + w//2, y + h//2),
                'bbox': (x, y, w, h),
                'area': area,
                'contour': contour,
                'aspect_ratio': aspect_ratio
            }
            valid_squares.append(square_data)
            print(f"  ✓ Contour {i}: ACCEPTED - area={area:.0f}, size={w}x{h}, AR={aspect_ratio:.2f}")
        
        print(f"Small square detection found {len(valid_squares)} squares\n")
        return valid_squares, thresh
    
    def register_stable_squares(self, detected_squares):
        """Register squares that appear consistently"""
        current_square_ids = [sq['id'] for sq in detected_squares]
        
        for square in detected_squares:
            square_id = square['id']
            current_center = square['center']
            current_bbox = square['bbox']
            
            if square_id not in self.registered_square_positions:
                self.registered_square_positions[square_id] = {
                    'square_data': square,
                    'seen_count': 1,
                    'stable': False,
                    'first_seen_frame': self.frame_count,
                    'position_history': [current_center],
                    'averaged_center': current_center,
                    'averaged_bbox': current_bbox
                }
            else:
                square_info = self.registered_square_positions[square_id]
                square_info['seen_count'] += 1
                square_info['square_data'] = square
                
                square_info['position_history'].append(current_center)
                if len(square_info['position_history']) > 5:
                    square_info['position_history'].pop(0)
                
                # Average position for stability
                positions = square_info['position_history']
                avg_x = int(np.mean([pos[0] for pos in positions]))
                avg_y = int(np.mean([pos[1] for pos in positions]))
                square_info['averaged_center'] = (avg_x, avg_y)
                square_info['averaged_bbox'] = current_bbox
                
                # Mark as stable quickly
                if square_info['seen_count'] >= 2:  # Very fast registration
                    square_info['stable'] = True
        
        # Clean up old squares
        squares_to_remove = []
        for square_id in self.registered_square_positions:
            if square_id not in current_square_ids:
                self.registered_square_positions[square_id]['seen_count'] -= 2
                if self.registered_square_positions[square_id]['seen_count'] <= -2:
                    squares_to_remove.append(square_id)
        
        for square_id in squares_to_remove:
            del self.registered_square_positions[square_id]
            if square_id in self.finger_in_square:
                del self.finger_in_square[square_id]
        
        # Return stable squares
        stable_squares = []
        for square_id, square_info in self.registered_square_positions.items():
            if square_info['stable']:
                stabilized_square = square_info['square_data'].copy()
                stabilized_square['center'] = square_info['averaged_center']
                stabilized_square['bbox'] = square_info['averaged_bbox']
                stable_squares.append(stabilized_square)
        
        return stable_squares
    
    def detect_finger_touches(self, frame, stable_squares):
        """Detect finger touches on stable squares"""
        if not hasattr(self, 'background_frame'):
            self.background_frame = frame.copy()
            return []
        
        # Update background slowly
        alpha = 0.1  # Faster adaptation
        self.background_frame = cv2.addWeighted(frame, alpha, self.background_frame, 1 - alpha, 0)
        
        # Calculate motion
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bg_gray = cv2.cvtColor(self.background_frame, cv2.COLOR_BGR2GRAY)
        
        diff = cv2.absdiff(gray, bg_gray)
        _, motion_mask = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)  # Lower threshold
        
        # Dilate motion
        kernel = np.ones((7,7), np.uint8)
        motion_mask = cv2.dilate(motion_mask, kernel, iterations=2)
        
        finger_touches = []
        
        for square in stable_squares:
            square_id = square['id']
            x, y, w, h = square['bbox']
            
            # Check motion in square area
            if y + h <= motion_mask.shape[0] and x + w <= motion_mask.shape[1]:
                square_motion = motion_mask[y:y+h, x:x+w]
                motion_pixels = np.sum(square_motion > 0)
                motion_percentage = motion_pixels / (w * h) if (w * h) > 0 else 0
                
                is_touched = motion_percentage > 0.2  # Lower threshold for easier triggering
                was_touched = square_id in self.finger_in_square
                
                if is_touched and not was_touched:
                    self.finger_in_square[square_id] = time.time()
                    finger_touches.append({
                        'type': 'touch_start',
                        'square_id': square_id,
                        'square': square
                    })
                elif not is_touched and was_touched:
                    del self.finger_in_square[square_id]
        
        return finger_touches
    
    def play_piano_note(self, square_id):
        """Play the specifically assigned note for this square"""
        current_time = time.time()
        
        if square_id in self.sound_cooldown:
            if current_time - self.sound_cooldown[square_id] < 0.4:
                return
        
        # Get the assigned note for this square
        note = self.get_note_for_square(square_id)
        
        # Play the assigned note
        if note in self.piano_notes:
            self.piano_notes[note].play()
            self.sound_cooldown[square_id] = current_time
            
            print(f"🎵 Playing assigned note {note} for square {square_id}")
        else:
            print(f"⚠️ Note {note} not found in piano_notes")


    def play_instrument_note(self, square_id):
        """Play the specifically assigned note for this square using current instrument"""
        current_time = time.time()
        
        if square_id in self.sound_cooldown:
            if current_time - self.sound_cooldown[square_id] < 0.4:
                return
        
        # Get the assigned note for this square
        note = self.get_note_for_square(square_id)
        
        # Play the assigned note with current instrument
        if note in self.instrument_sounds:
            self.instrument_sounds[note].play()
            self.sound_cooldown[square_id] = current_time
            
            instrument_name = self.get_instrument_display_name()
            print(f"🎵 Playing {instrument_name} note {note} for square {square_id}")
        else:
            print(f"⚠️ Note {note} not found in {self.instrument_type} sounds")
    
    def process_frame(self, frame):
        """Main processing function - same logic, different sounds"""
        self.frame_count += 1
        
        if self.frame_count < 3:
            return frame, [], [], np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
        
        # All the existing square detection logic remains the same
        detected_squares, thresh = self.detect_small_squares_only(frame)
        stable_squares = self.register_stable_squares(detected_squares)
        self.assign_notes_to_squares(stable_squares)
        
        # Safety check every 20 frames
        if self.frame_count % 20 == 0 and stable_squares:
            if self.detect_duplicate_notes():
                self.force_scale_based_assignment(stable_squares)
        
        # Detect finger touches
        finger_touches = self.detect_finger_touches(frame, stable_squares)
        
        # Play sounds with current instrument
        for touch in finger_touches:
            if touch['type'] == 'touch_start':
                self.play_instrument_note(touch['square_id'])  # Changed method name
        
        # Enhanced visualization with instrument info
        result_frame = frame.copy()
        
        # Draw detected squares (yellow)
        for square in detected_squares:
            cv2.drawContours(result_frame, [square['contour']], -1, (0, 255, 255), 2)
            x, y = square['center']
            cv2.putText(result_frame, "DETECTED", (x-30, y-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # Draw stable squares with instrument-specific info
        for square in stable_squares:
            x, y, w, h = square['bbox']
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            
            assigned_note = self.get_note_for_square(square['id'])
            cv2.putText(result_frame, f"NOTE: {assigned_note}", (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            square_info = self.registered_square_positions[square['id']]
            seen_count = square_info['seen_count']
            cv2.putText(result_frame, f"READY:{seen_count}", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            if square['id'] in self.finger_in_square:
                cv2.rectangle(result_frame, (x-5, y-5), (x + w + 5, y + h + 5), (0, 0, 255), 4)
                cv2.putText(result_frame, f"PLAYING {assigned_note}!", (x-15, y + h + 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Display instrument and scale info
        instrument_display = self.get_instrument_display_name()
        cv2.putText(result_frame, f"Instrument: {instrument_display} | Squares: {len(stable_squares)} | Scale: {' '.join(self.available_notes)}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return result_frame, detected_squares, finger_touches, thresh


# Test function for standalone testing
def test_square_detection():
    """Test function to see what's being detected"""
    detector = SquareDetector()
    
    # You can configure scale here for testing
    detector.set_custom_scale('major')  # Try different scales: major, pentatonic, blues, etc.
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        result_frame, squares, touches, thresh = detector.process_frame(frame)
        
        cv2.imshow('Lead Zeppelin - Scale-Based Assignment', result_frame)
        cv2.imshow('Threshold Debug', thresh)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            detector.set_custom_scale('major')
            print("Switched to major scale")
        elif key == ord('2'):
            detector.set_custom_scale('pentatonic')
            print("Switched to pentatonic scale")
        elif key == ord('3'):
            detector.set_custom_scale('blues')
            print("Switched to blues scale")
        elif key == ord('4'):
            detector.set_custom_scale('simple')
            print("Switched to simple chord")
        
    cap.release()
    cv2.destroyAllWindows()

# Uncomment to test standalone
# test_square_detection()