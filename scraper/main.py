import logging
from functools import wraps
import json
from typing import List
from bs4 import BeautifulSoup
from pytube import YouTube
import cv2
import os
import urllib
from pyppeteer import launch
from urllib.error import HTTPError
from youtube_search import YoutubeSearch

import aiohttp
import asyncio

logger = logging.getLogger(__name__)
pytube_logger = logging.getLogger("pytube.__main__")
pytube_logger.setLevel(logging.WARNING)
logger.setLevel(logging.INFO)


def run_in_executor(f):
    wraps(f)

    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return inner


async def get_search_result_urls_v1(
    search: str, limit: int = 25, offset: int = 0
) -> List[str]:
    browser = await launch({"headless": True})
    query = urllib.parse.quote(search)
    url = "https://www.youtube.com/results?search_query=" + query
    page = await browser.newPage()
    results = await page.goto(url)
    elements = await page.querySelectorAll("#video-title")
    results = []
    for el in elements[offset:]:
        result = await page.evaluate("(element) => element.href", el)

        if result is not None:
            results.append(result)
        if len(results) == limit:
            break

    await browser.close()
    return results


async def get_search_result_urls_v2(
    search: str, limit: int = 20, base_url="https://www.youtube.com"
) -> List[str]:
    results = YoutubeSearch(search, max_results=limit).to_dict()
    # {'id': '6ihNMNTBdjk', 'thumbnails': ['https://i.ytimg.com/vi/6ihNMNTBdjk/hq720.jpg?sqp=-oaymwEjCOgCEMoBSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLD2zz0J3YZRO3gMm5H_vOWK3wF_nQ', 'https://i.ytimg.com/vi/6ihNMNTBdjk/hq720.jpg?sqp=-oaymwEXCNAFEJQDSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLDlsInsAwu6g4F9Sv1om0O_AZobyg'], 'title': 'How to improve your search terms', 'long_desc': 'How to improve your ', 'channel': 'Brock University Library', 'duration': '3:05', 'views': '11,574 views', 'url_suffix': '/watch?v=6ihNMNTBdjk'}
    urls = [base_url + r["url_suffix"] for r in results]
    return urls


@run_in_executor
def download_video(url: str, path: str = f"{os.getcwd()}/tmp/", callback=None) -> str:
    yt = YouTube(url)

    if callback:
        yt.register_on_complete_callback(callback)

    out = yt.streams.filter(
        type="video", subtype="mp4", res="720p", adaptive=True
    ).first()

    video_id = yt.video_id

    out_path = path + video_id

    out_file = out.download(out_path, filename="video")

    metadata_file = f"{out_path}/metadata.json"
    metadata = {
        "video_filename": "video.mp4",
        "path": out_path,
        "video_id": video_id,
        "title": yt.title,
        "url": url,
        "stream": {
            "mime_type": out.mime_type,
            "fps": out.fps,
            "video_codec": out.video_codec,
            "resolution": out.resolution,
        },
    }
    with open(metadata_file, "w+") as f:
        json.dump(metadata, f, indent=2)

    logging.info(f"Finished download {out_file} from {url}")
    return metadata


async def download_video_async(
    url: str, path: str = f"{os.getcwd()}/tmp/", callback=None, backoff=6, retry=3
):
    try:
        return await download_video(url, path, callback)
    except HTTPError as e:
        if retry > 0:
            logging.warning(f"Retrying url {url}")
            await asyncio.sleep(backoff)
            return await download_video_async(
                url, path, callback, backoff * 2, retry - 1
            )
        else:
            logging.error(f"FAILED download {url}")
            raise e


@run_in_executor
def video_to_image_frames(
    metadata: dict, start_frame_percent: float = 0.0, end_frame_percent: float = 1.0, downsample_fps=2
):
    logger.info(f"Extracting frames from {metadata}")
    metadata_file = os.path.join(metadata["path"], "metadata.json")

    if metadata.get("frame_count") is not None:
        logger.warning(f'Skipping {metadata["path"]} - frames already extracted')
        return False, metadata

    video_path = os.path.join(metadata["path"], metadata["video_filename"])
    vidcap = cv2.VideoCapture(video_path)

    total_frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)

    start_frame = round(total_frames * start_frame_percent)
    end_frame = round(total_frames * end_frame_percent) - start_frame

    vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    success, image = vidcap.read()
    count = 0

    out_path = metadata["path"] + "/frames"
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    
    stream_fps = metadata['stream']['fps']
    while success and count < end_frame:
        if count%(stream_fps/downsample_fps) == 0:
            cv2.imwrite(f"{out_path}/{count}.jpg", image)
        success, image = vidcap.read()
        logger.debug(f"Read a new frame: {count} success: {success}")
        count += 1

    metadata["frame_count"] = count
    metadata["frame_path"] = out_path
    with open(metadata_file, "w+") as f:
        json.dump(metadata, f, indent=2)

    logging.info(f"Finished extracting frames {metadata_file}")
    return True, metadata


async def video_to_image_frames_async(*args, **kwargs):
    return await video_to_image_frames(*args, **kwargs)
