from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
from .utils import parse_letter_notes_from_url
from .gemini_integration import map_notes_to_shapes, generate_lesson_plan, generate_encouragement_feedback, get_note_sequence_for_demo
import cv2
import json
import base64
import numpy as np
from .cv_processor import SquareDetector

# Global detector instance
detector = SquareDetector()

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
    """Configure instrument mappings for shapes"""
    
    def post(self, request):
        try:
            config_data = request.data
            # Here you would save configuration to database
            # For now, just return success
            
            return Response({
                'message': 'Instrument configuration saved',
                'config': config_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        # Return current instrument configuration
        default_config = {
            'square': {
                'instrument': 'piano',
                'notes': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
                'sound_enabled': True
            }
        }
        
        return Response(default_config, status=status.HTTP_200_OK)

class ParseNotesView(APIView):
    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            parsed_notes = parse_letter_notes_from_url(url)
            shapes = map_notes_to_shapes(parsed_notes)
            
            return Response({
                'parsed_notes': parsed_notes,
                'shapes': shapes
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
