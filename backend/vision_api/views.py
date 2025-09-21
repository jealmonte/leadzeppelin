from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse, HttpResponse
from .utils import parse_letter_notes_from_url, parse_notes_from_pdf_url, get_pdf_page_images_from_url, get_song_title_from_noobnotes_url, find_and_parse_pdf_from_makingmusicfun
from .gemini_integration import map_notes_to_shapes, generate_lesson_plan, generate_encouragement_feedback, get_note_sequence_for_demo
import io
import cv2
import json
import base64
import numpy as np
from .cv_processor import SquareDetector

# Global detector instance
piano_detector = SquareDetector(instrument_type="piano")
drum_detector = SquareDetector(instrument_type="drums") 
flute_detector = SquareDetector(instrument_type="flute")
detector = SquareDetector()

class PianoStreamView(APIView):
    """Piano-specific video stream"""
    def get(self, request):
        return StreamingHttpResponse(
            self.generate_piano_frames(), 
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    
    def generate_piano_frames(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame, squares, touches, thresh_debug = piano_detector.process_frame(frame)
            
            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


class DrumStreamView(APIView):
    """Drum-specific video stream"""
    def get(self, request):
        return StreamingHttpResponse(
            self.generate_drum_frames(), 
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    
    def generate_drum_frames(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame, squares, touches, thresh_debug = drum_detector.process_frame(frame)
            
            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

class FluteStreamView(APIView):
    """Flute-specific video stream"""
    def get(self, request):
        return StreamingHttpResponse(
            self.generate_flute_frames(), 
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    
    def generate_flute_frames(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame, squares, touches, thresh_debug = flute_detector.process_frame(frame)
            
            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

class VideoStreamView(APIView):
    """Stream video feed with square detection"""
    
    def get(self, request):
        return StreamingHttpResponse(
            self.generate_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    
    def generate_frames(self):
        cap = cv2.VideoCapture(0)  # Use default camera
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame for square detection
            processed_frame, squares, occluded, thresh_debug = detector.process_frame(frame)
            
            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

class SquareDetectionView(APIView):
    """API endpoint for square detection analysis"""
    
    def post(self, request):
        try:
            # Get image data from request
            image_data = request.data.get('image')
            
            if image_data:
                # Decode base64 image
                image_bytes = base64.b64decode(image_data.split(',')[1])
                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Process frame
                processed_frame, squares, occluded = detector.process_frame(frame)
                
                # Prepare response data
                response_data = {
                    'squares_detected': len(squares),
                    'occluded_squares': len(occluded),
                    'squares': [
                        {
                            'id': square['id'],
                            'center': square['center'],
                            'area': square['area'],
                            'bbox': square['bbox']
                        }
                        for square in squares
                    ],
                    'sounds_played': [square['id'] for square in occluded]
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            return Response(
                {'error': 'No image data provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InstrumentConfigView(APIView):
    """Configure different instruments"""
    def post(self, request):
        try:
            instrument_type = request.data.get('instrument', 'piano')
            scale = request.data.get('scale', 'major')
            
            # Configure the appropriate detector
            if instrument_type == 'piano':
                piano_detector.set_custom_scale(scale)
            elif instrument_type == 'drums':
                drum_detector.set_custom_scale(scale)
            elif instrument_type == 'flute':
                flute_detector.set_custom_scale(scale)
            
            return Response({
                'message': f'{instrument_type.title()} configured with {scale} scale',
                'instrument': instrument_type,
                'scale': scale
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get available instruments and their configurations"""
        return Response({
            'available_instruments': [
                {'value': 'piano', 'label': '🎹 Piano', 'description': 'Classic piano with harmonic tones'},
                {'value': 'drums', 'label': '🥁 Drums', 'description': 'Percussion kit with kick, snare, hi-hat, toms'},
                {'value': 'flute', 'label': '🪈 Flute', 'description': 'Woodwind with pure, breathy tones'}
            ],
            'available_scales': ['major', 'pentatonic', 'blues', 'minor', 'fourths', 'simple'],
            'current_configurations': {
                'piano': {'scale': ' '.join(piano_detector.available_notes)},
                'drums': {'scale': ' '.join(drum_detector.available_notes)},
                'flute': {'scale': ' '.join(flute_detector.available_notes)}
            }
        }, status=status.HTTP_200_OK)

class GenerateLessonView(APIView):
    """Generate lesson plans based on parsed notes and shapes"""
    
    def post(self, request):
        url = request.data.get('url')
        song_title = request.data.get('song_title', 'Unknown Song')
        difficulty = request.data.get('difficulty', 'beginner')
        
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Step 1: Parse notes from URL
            parsed_notes = parse_letter_notes_from_url(url)
            
            # Step 2: Generate shapes
            shapes = map_notes_to_shapes(parsed_notes)
            
            # Handle shape generation errors
            if isinstance(shapes, dict) and "error" in shapes:
                return Response({
                    'error': 'Shape generation failed',
                    'details': shapes
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Step 3: Generate lesson plan
            lesson_plan = generate_lesson_plan(parsed_notes, shapes, song_title, difficulty)
            
            # Handle lesson plan generation errors  
            if isinstance(lesson_plan, dict) and "error" in lesson_plan:
                return Response({
                    'error': 'Lesson plan generation failed',
                    'details': lesson_plan
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'song_title': song_title,
                'difficulty': difficulty,
                'parsed_notes': parsed_notes,
                'shapes': shapes,
                'lesson_plan': lesson_plan
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WrongNoteHandlerView(APIView):
    """Handle wrong note feedback and restart functionality"""
    
    def post(self, request):
        expected_note = request.data.get('expected_note')
        played_note = request.data.get('played_note')
        attempt_count = request.data.get('attempt_count', 1)
        
        if not expected_note or not played_note:
            return Response({
                'error': 'Both expected_note and played_note are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .gemini_integration import generate_encouragement_feedback
            feedback = generate_encouragement_feedback(expected_note, played_note, attempt_count)
            
            return Response({
                'expected_note': expected_note,
                'played_note': played_note,
                'attempt_count': attempt_count,
                'feedback': feedback,
                'action': 'restart_available'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DemoModeView(APIView):
    """Generate demo-friendly note sequences for computer vision demonstration"""
    
    def post(self, request):
        url = request.data.get('url')
        song_title = request.data.get('song_title', 'Demo Song')
        
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Parse notes and generate shapes
            parsed_notes = parse_letter_notes_from_url(url)
            shapes = map_notes_to_shapes(parsed_notes)
            
            if isinstance(shapes, dict) and "error" in shapes:
                return Response({
                    'error': 'Shape generation failed', 
                    'details': shapes
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Get clean demo sequence
            from .gemini_integration import get_note_sequence_for_demo
            demo_data = get_note_sequence_for_demo(parsed_notes, shapes)
            
            return Response({
                'song_title': song_title,
                'mode': 'demo',
                'demo_sequence': demo_data.get('demo_sequence', []),
                'instructions': demo_data.get('instructions', 'Play the notes as shown'),
                'shapes': shapes,
                'total_notes': len(demo_data.get('demo_sequence', [])),
                'cv_ready': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgressTrackingView(APIView):
    """Track learner progress and provide adaptive feedback"""
    
    def post(self, request):
        current_note_index = request.data.get('current_note_index', 0)
        sequence = request.data.get('sequence', [])
        played_correctly = request.data.get('played_correctly', True)
        session_data = request.data.get('session_data', {})
        
        try:
            if played_correctly:
                # Move to next note
                next_index = current_note_index + 1
                
                if next_index >= len(sequence):
                    # Sequence completed!
                    return Response({
                        'status': 'completed',
                        'message': 'Congratulations! You completed the sequence!',
                        'progress': 100,
                        'next_action': 'choose_new_song'
                    }, status=status.HTTP_200_OK)
                else:
                    # Continue to next note
                    return Response({
                        'status': 'continue',
                        'current_note_index': next_index,
                        'current_note': sequence[next_index],
                        'progress': round((next_index / len(sequence)) * 100, 1),
                        'encouragement': 'Great job! Keep going!'
                    }, status=status.HTTP_200_OK)
            else:
                # Wrong note played - stay on current note
                return Response({
                    'status': 'retry',
                    'current_note_index': current_note_index,
                    'current_note': sequence[current_note_index] if current_note_index < len(sequence) else None,
                    'progress': round((current_note_index / len(sequence)) * 100, 1),
                    'message': 'Try that note again!'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ParsePdfNotesView(APIView):
    """
    API endpoint to parse sheet music from a PDF URL, generate shapes,
    and create a lesson plan.
    """
    def post(self, request):
        pdf_url = request.data.get('url')
        song_title = request.data.get('song_title', 'PDF Song')

        if not pdf_url:
            return Response({'error': 'PDF URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 1. Parse text from the PDF URL
            pdf_text_pages = parse_notes_from_pdf_url(pdf_url)
            if any("Error:" in page for page in pdf_text_pages):
                return Response({'error': pdf_text_pages[0]}, status=status.HTTP_400_BAD_REQUEST)

            # Combine text from all pages into one block for processing
            full_text = " ".join(pdf_text_pages)

            # 2. Extract note tokens from the text (this is a simplified approach)
            import re
            token_pattern = re.compile(r"\b[A-G](?:#|b)?\b", re.IGNORECASE)
            parsed_notes = [token_pattern.findall(full_text)] # Treat all notes as one sequence

            if not parsed_notes or not parsed_notes[0]:
                return Response({'error': 'No musical notes found in the PDF text.'}, status=status.HTTP_400_BAD_REQUEST)

            # 3. Generate shapes using your existing Gemini function
            shapes = map_notes_to_shapes(parsed_notes)
            if isinstance(shapes, dict) and "error" in shapes:
                return Response({'error': 'Shape generation failed', 'details': shapes}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 4. Generate lesson plan
            lesson_plan = generate_lesson_plan(parsed_notes, shapes, song_title)
            if isinstance(lesson_plan, dict) and "error" in lesson_plan:
                return Response({'error': 'Lesson plan generation failed', 'details': lesson_plan}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'song_title': song_title,
                'parsed_notes': parsed_notes,
                'shapes': shapes,
                'lesson_plan': lesson_plan
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PdfImageView(APIView):
    """
    API endpoint to retrieve a specific page of a PDF as an image.
    """
    def get(self, request):
        pdf_url = request.query_params.get('url')
        page_num = int(request.query_params.get('page', 1)) # Default to first page

        if not pdf_url:
            return Response({'error': 'PDF URL is required as a query parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # On Windows, you might need to specify the Poppler path if not in system PATH
            # poppler_path = r"C:\path\to\poppler\bin"
            # images = get_pdf_page_images_from_url(pdf_url, poppler_path=poppler_path)
            
            images = get_pdf_page_images_from_url(pdf_url)

            if not images or isinstance(images[0], str): # Check for error
                return Response({'error': images[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if page_num > len(images) or page_num < 1:
                return Response({'error': f'Invalid page number. PDF has {len(images)} pages.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the requested page (adjust for 0-based index)
            image = images[page_num - 1]
            
            # Save the image to a memory buffer
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            buffer.seek(0)
            
            # Return the image as an HTTP response
            return HttpResponse(buffer, content_type='image/jpeg')

        except Exception as e:
            return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AutoParsePdfView(APIView):
    """
    Takes a noobnotes.net URL, finds the corresponding sheet music PDF
    on makingmusicfun.net, and processes it into a lesson plan.
    """
    def post(self, request):
        noobnotes_url = request.data.get('url')

        if not noobnotes_url:
            return Response({'error': 'noobnotes.net URL is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Get the song title from the noobnotes URL
            song_title = get_song_title_from_noobnotes_url(noobnotes_url)
            if song_title == "Unknown Song Title":
                return Response({'error': 'Could not extract a valid song title.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. Find and parse the PDF from makingmusicfun.net
            pdf_text_pages = find_and_parse_pdf_from_makingmusicfun(song_title)
            if any("Error:" in page for page in pdf_text_pages):
                return Response({'error': pdf_text_pages[0]}, status=status.HTTP_400_BAD_REQUEST)

            full_text = " ".join(pdf_text_pages)
            
            # 3. Process the extracted text through your existing pipeline
            import re
            token_pattern = re.compile(r"\b[A-G](?:#|b)?\b", re.IGNORECASE)
            parsed_notes = [token_pattern.findall(full_text)]
            
            if not parsed_notes or not parsed_notes[0]:
                return Response({'error': 'No musical notes found in the automatically parsed PDF.'}, status=status.HTTP_400_BAD_REQUEST)

            shapes = map_notes_to_shapes(parsed_notes)
            lesson_plan = generate_lesson_plan(parsed_notes, shapes, song_title)
            
            return Response({
                'source_url': noobnotes_url,
                'found_song_title': song_title,
                'parsed_notes': parsed_notes,
                'shapes': shapes,
                'lesson_plan': lesson_plan
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f"An overall error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ThresholdDebugView(APIView):
    """Stream threshold debug view to help with detection tuning"""
    
    def get(self, request):
        return StreamingHttpResponse(
            self.generate_threshold_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    
    def generate_threshold_frames(self):
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Get threshold debug image
            _, _, _, thresh_debug = detector.process_frame(frame)
            
            # Convert threshold image to 3-channel for JPEG encoding
            thresh_color = cv2.cvtColor(thresh_debug, cv2.COLOR_GRAY2BGR)            
            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', thresh_color)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')