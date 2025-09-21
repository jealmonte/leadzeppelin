from django.urls import path
from .views import VideoStreamView, SquareDetectionView, InstrumentConfigView, ParsePdfNotesView, GenerateLessonView, WrongNoteHandlerView, DemoModeView, ProgressTrackingView, ThresholdDebugView, ParsePdfNotesView, PdfImageView, AutoParsePdfView, PianoStreamView, DrumStreamView, FluteStreamView

app_name = 'visionapi'

urlpatterns = [
    # Original endpoints
    path('video-stream/', VideoStreamView.as_view(), name='video-stream'),
    path('detect-squares/', SquareDetectionView.as_view(), name='detect-squares'),
    path('instrument-config/', InstrumentConfigView.as_view(), name='instrument-config'),
    path('generate-lesson/', GenerateLessonView.as_view(), name='generate-lesson'),
    path('wrong-note/', WrongNoteHandlerView.as_view(), name='wrong-note'),
    path('demo-mode/', DemoModeView.as_view(), name='demo-mode'),
    path('progress/', ProgressTrackingView.as_view(), name='progress'),
    path('parse-pdf-notes/', ParsePdfNotesView.as_view(), name='parse-pdf-notes'),
    path('pdf-image/', PdfImageView.as_view(), name='pdf-image'),
    path('auto-parse-pdf/', AutoParsePdfView.as_view(), name='auto-parse-pdf'),
    path('threshold-debug/', ThresholdDebugView.as_view(), name='threshold-debug'),
    path('piano-stream/', PianoStreamView.as_view(), name='piano-stream'),
    path('drum-stream/', DrumStreamView.as_view(), name='drum-stream'),
    path('flute-stream/', FluteStreamView.as_view(), name='flute-stream'),
]
