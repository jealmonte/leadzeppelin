from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
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
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
