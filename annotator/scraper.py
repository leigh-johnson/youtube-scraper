import logging
import json
from typing import List
from bs4 import BeautifulSoup
from pytube import YouTube
import cv2
import os
import urllib
from pyppeteer import launch

import aiohttp
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def get_search_result_urls(
    search: str, limit: int = 10, offset: int = 0
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


def download_video(url: str, path: str = f"{os.getcwd()}/tmp/") -> str:
    yt = YouTube(url)

    out = yt.streams.filter(adaptive=True, res="480p").first()

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
        json.dump(metadata, f)

    logging.info(f"Finished download {out_file} from {url}")
    return metadata


def video_to_image_frames(metadata: dict, folder: str = f"{os.getcwd()}/tmp/images"):

    metadata_file = os.path.join(metadata["path"], "metadata.json")

    if metadata.get("frame_count") is not None:
        logger.warning(f'Skipping {metadata["path"]} - frames already extracted')
        return False, metadata

    video_path = os.path.join(metadata["path"], metadata["video_filename"])
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    out_path = metadata["path"] + "/frames"
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    while success:
        cv2.imwrite(f"{out_path}/{count}.jpg", image)
        success, image = vidcap.read()
        logger.info(f"Read a new frame: {count} success: {success}")
        count += 1

    metadata["frame_count"] = count
    metadata["frame_path"] = out_path
    with open(metadata_file, "w+") as f:
        json.dump(metadata, f, indent=2)

    return True, metadata


# async def fetch(session, url):
#     async with session.get(url) as response:
#         return await response.text()

# async def main():
#     async with aiohttp.ClientSession() as session:
#         html = await fetch(session, 'http://python.org')
#         print(html)
