
import logging
from typing import List
from bs4 import BeautifulSoup
#from pytube import YouTube
#import cv2
import os
import urllib
from pyppeteer import launch

import aiohttp
import asyncio

async def get_urls(search: str, limit: int = 10 ) -> List[str]:
    browser = await launch({'headless': True})
    query = urllib.parse.quote(search)
    url = "https://www.youtube.com/results?search_query=" + query
    page = await browser.newPage()
    results = await page.goto(url)
    elements = await page.querySelectorAll('#video-title')
    results = []
    for i, el in enumerate( elements ):
        if i < limit:
            result = await page.evaluate('(element) => element.href', el)
            results.append(result)
        else:
            break
    await browser.close()
    return results

# async def fetch(session, url):
#     async with session.get(url) as response:
#         return await response.text()

# async def main():
#     async with aiohttp.ClientSession() as session:
#         html = await fetch(session, 'http://python.org')
#         print(html)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())




# def download_video(url, path=None, max_duration=10):
#       try:
#         yt = YouTube(url)
#         duration = int(yt.player_config_args['player_response']['streamingData']['formats'][0]['approxDurationMs'])
#         if duration < max_duration*60*1000:
#             yt = yt.streams.filter(file_extension='mp4').first()
#             out_file = yt.download(path)
#             file_name = out_file.split("\\")[-1]
#             print(f"Downloaded {file_name} correctly!")
#         else:
#             print(f"Video {url} too long")
#     except Exception as exc:
#         print(f"Download of {url} did not work because of {exc}...")


# def extract_images_from_video(video, folder=None, delay=30, name="file", max_images=20, silent=False):    
#     vidcap = cv2.VideoCapture(video)
#     count = 0
#     num_images = 0
#     if not folder:
#         folder = os.getcwd()
#     label = max_label(name, folder)
#     success = True
#     fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    
#     while success and num_images < max_images:
#         success, image = vidcap.read()
#         num_images += 1
#         label += 1
#         file_name = name + "_" + str(label) + ".jpg"
#         path = os.path.join(folder, file_name)
#         cv2.imwrite(path, image)
#         if cv2.imread(path) is None:
#             os.remove(path)
#         else:
#             if not silent:
#                 print(f'Image successfully written at {path}')
#         count += delay*fps
#         vidcap.set(1, count)


# def extract_images_from_video(video, folder=None, delay=30, name="file", max_images=20, silent=False):    
#     vidcap = cv2.VideoCapture(video)
#     count = 0
#     num_images = 0
#     if not folder:
#         folder = os.getcwd()
#     label = max_label(name, folder)
#     success = True
#     fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    
#     while success and num_images < max_images:
#         success, image = vidcap.read()
#         num_images += 1
#         label += 1
#         file_name = name + "_" + str(label) + ".jpg"
#         path = os.path.join(folder, file_name)
#         cv2.imwrite(path, image)
#         if cv2.imread(path) is None:
#             os.remove(path)
#         else:
#             if not silent:
#                 print(f'Image successfully written at {path}')
#         count += delay*fps
#         vidcap.set(1, count)