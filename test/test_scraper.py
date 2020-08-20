import pytest
from annotator.scraper import get_urls

@pytest.mark.asyncio
async def test_get_urls():
    urls = await get_urls("3d printer spaghetti", limit=3)
    assert len(urls) == 3
