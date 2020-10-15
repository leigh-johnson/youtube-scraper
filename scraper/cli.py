import click
import asyncio
import logging
import os
from functools import wraps

from main import (
    get_search_result_urls_v2,
    download_video_async,
    video_to_image_frames_async,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# https://github.com/pallets/click/issues/85
def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    pass


@cli.command()
@click.argument("query")
@click.option(
    "--limit",
    default=20,
    help="Limit number of search results. Use with offset to page through query results.",
)
@click.option("--out", default=f"{os.getcwd()}/tmp/")
@coro
async def video(query, limit, out):
    logging.info(f"Begin downloading videos {limit} matching query {query}")
    urls = await get_search_result_urls_v2(query, limit=limit)
    logging.info(f"Found {len(urls)} results")
    logging.info(f"Downloading videos {urls}")
    download_tasks = [
        asyncio.create_task(download_video_async(url, path=out, retry=0))
        for url in urls
    ]
    results = await asyncio.gather(*download_tasks, return_exceptions=True)
    successful = list(filter(lambda x: not isinstance(x, Exception), results))
    logging.info(
        f"Suceeded downloading {len(successful)}/{limit} matching query {query}"
    )


@cli.command()
@click.argument("query")
@click.option(
    "--limit",
    default=10,
    help="Limit number of search results. Use with offset to page through query results.",
)
@click.option("--out", default=f"{os.getcwd()}/tmp/")
@click.option("--start-percent", default=0.15)
@click.option("--end-percent", default=0.85)
@coro
async def frames(query, limit, out, start_percent, end_percent):
    logging.info(f"Begin downloading videos {limit} matching query {query}")
    urls = await get_search_result_urls_v2(query, limit=limit)
    logging.info(f"Found {len(urls)} results")
    logging.info(f"Downloading videos {urls}")
    download_tasks = [
        asyncio.create_task(download_video_async(url, path=out, retry=0))
        for url in urls
    ]
    results = await asyncio.gather(*download_tasks, return_exceptions=True)
    successful = list(filter(lambda x: not isinstance(x, Exception), results))
    frame_tasks = [
        video_to_image_frames_async(
            m, start_frame_percent=start_percent, end_frame_percent=end_percent
        )
        for m in successful
    ]
    await asyncio.gather(*frame_tasks)


if __name__ == "__main__":
    cli()
