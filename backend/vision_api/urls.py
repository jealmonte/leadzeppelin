from django.urls import path
from .views import VideoStreamView, SquareDetectionView, InstrumentConfigView, ParseNotesView, GenerateLessonView, WrongNoteHandlerView, DemoModeView, ProgressTrackingView, ThresholdDebugView, ParsePdfNotesView, PdfImageView, AutoParsePdfView

app_name = 'vision_api'

urlpatterns = [
    path('video-stream/', VideoStreamView.as_view(), name='video-stream'),
    path('detect-squares/', SquareDetectionView.as_view(), name='detect-squares'),
    path('instrument-config/', InstrumentConfigView.as_view(), name='instrument-config'),
    path('parse-notes/', ParseNotesView.as_view(), name='parse-notes'),
    path('generate-lesson/', GenerateLessonView.as_view(), name='generate-lesson'),
    path('wrong-note/', WrongNoteHandlerView.as_view(), name='wrong-note'),
    path('demo-mode/', DemoModeView.as_view(), name='demo-mode'),
    path('progress/', ProgressTrackingView.as_view(), name='progress'),
    path('parse-pdf-notes/', ParsePdfNotesView.as_view(), name='parse-pdf-notes'),
    path('pdf-image/', PdfImageView.as_view(), name='pdf-image'),
    path('auto-parse-pdf/', AutoParsePdfView.as_view(), name='auto-parse-pdf'),
    path('threshold-debug/', ThresholdDebugView.as_view(), name='threshold-debug'),
]