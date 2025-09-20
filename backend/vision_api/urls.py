from django.urls import path
from .views import VideoStreamView, SquareDetectionView, InstrumentConfigView

urlpatterns = [
    path('video-stream/', VideoStreamView.as_view(), name='video-stream'),
    path('detect-squares/', SquareDetectionView.as_view(), name='detect-squares'),
    path('instrument-config/', InstrumentConfigView.as_view(), name='instrument-config'),
]
