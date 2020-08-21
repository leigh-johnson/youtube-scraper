import os
import pytest
from annotator.scraper import get_search_result_urls, download_video, video_to_image_frames

# ['https://www.youtube.com/watch?v=aWg1nG2AbA8', 'https://www.youtube.com/watch?v=YS6gH66_7yE', 'https://www.youtube.com/watch?v=X-dQ2r0YI4Y']
@pytest.mark.asyncio
async def test_get_search_result_urls():
    urls = await get_search_result_urls("3d printer spaghetti", limit=3)
    assert len(urls) == 3

def test_download_video():
    url = 'https://www.youtube.com/watch?v=aWg1nG2AbA8'
    metadata = download_video(url)
    assert metadata == { 'video_filename': 'video.mp4', 'path': f'{os.getcwd()}/tmp/aWg1nG2AbA8', 'video_id': 'aWg1nG2AbA8', 'title': '5 3D Printing Mistakes you WILL make - and how to avoid them! 3D Printing 101', 'url': 'https://www.youtube.com/watch?v=aWg1nG2AbA8', 'stream': {'mime_type': 'video/mp4', 'fps': 30, 'video_codec': 'avc1.4d401f', 'resolution': '480p'}}

@pytest.mark.slow
def test_write_video_image_frames():
    metadata_in = { 'video_filename': 'video.mp4', 'path': f'{os.getcwd()}/tmp/aWg1nG2AbA8', 'video_id': 'aWg1nG2AbA8', 'title': '5 3D Printing Mistakes you WILL make - and how to avoid them! 3D Printing 101', 'url': 'https://www.youtube.com/watch?v=aWg1nG2AbA8', 'stream': {'mime_type': 'video/mp4', 'fps': 30, 'video_codec': 'avc1.4d401f', 'resolution': '480p'}}
    success, metadata_out = video_to_image_frames(metadata_in)
    assert success == True
    assert metadata_out == {'video_filename': 'video.mp4', 'path': '/home/leigh/projects/youtube-data-annotator/tmp/aWg1nG2AbA8', 'video_id': 'aWg1nG2AbA8', 'title': '5 3D Printing Mistakes you WILL make - and how to avoid them! 3D Printing 101', 'url': 'https://www.youtube.com/watch?v=aWg1nG2AbA8', 'stream': {'mime_type': 'video/mp4', 'fps': 30, 'video_codec': 'avc1.4d401f', 'resolution': '480p'}, 'frame_count': 15244, 'frame_path': '/home/leigh/projects/youtube-data-annotator/tmp/aWg1nG2AbA8/frames'}

# skip writing frames if metadata already includes frame_count
def test_skip_write_video_image_frames():
    metadata_in = {'video_filename': 'video.mp4', 'path': '/home/leigh/projects/youtube-data-annotator/tmp/aWg1nG2AbA8', 'video_id': 'aWg1nG2AbA8', 'title': '5 3D Printing Mistakes you WILL make - and how to avoid them! 3D Printing 101', 'url': 'https://www.youtube.com/watch?v=aWg1nG2AbA8', 'stream': {'mime_type': 'video/mp4', 'fps': 30, 'video_codec': 'avc1.4d401f', 'resolution': '480p'}, 'frame_count': 15244, 'frame_path': '/home/leigh/projects/youtube-data-annotator/tmp/aWg1nG2AbA8/frames'}
    success, metadata_out = video_to_image_frames(metadata_in)
    assert success == False
    assert metadata_out == {'video_filename': 'video.mp4', 'path': '/home/leigh/projects/youtube-data-annotator/tmp/aWg1nG2AbA8', 'video_id': 'aWg1nG2AbA8', 'title': '5 3D Printing Mistakes you WILL make - and how to avoid them! 3D Printing 101', 'url': 'https://www.youtube.com/watch?v=aWg1nG2AbA8', 'stream': {'mime_type': 'video/mp4', 'fps': 30, 'video_codec': 'avc1.4d401f', 'resolution': '480p'}, 'frame_count': 15244, 'frame_path': '/home/leigh/projects/youtube-data-annotator/tmp/aWg1nG2AbA8/frames'}


