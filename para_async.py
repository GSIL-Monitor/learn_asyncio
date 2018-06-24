#!/usr/bin/env python3.5

import asyncio
import itertools

import aiohttp


async def download(url, parts):
    async def get_partial_content(u, i, start, end):
        print(i, start, end)
        headers = {'Range': 'bytes={}-{}'.format(start, end-1 if end else '')}
        async with aiohttp.get(u, headers=headers) as _resp:
            return(i, await _resp.read())

    async with aiohttp.head(url) as resp:
        size = int(resp.headers['content-length'])
    print('size: {}'.format(size))

    ranges = list(range(0, size, size // parts))

    res, _ = await asyncio.wait(
        [get_partial_content(url, i, start, end) for i, (start, end) in
         enumerate(itertools.zip_longest(ranges, ranges[1:], fillvalue=''))])

    sorted_result = sorted(task.result() for task in res)

    result_data = b''.join(data for _, data in sorted_result)

    with open('{}'.format(url.split('/')[-1]), 'wb') as f:
        f.write(result_data)


if __name__ == '__main__':
    urls = ['http://pic1.win4000.com/wallpaper/7/53bb814e13a63.jpg',
            'http://pic1.win4000.com/wallpaper/0/540ec117e8f01.jpg',
            'http://pic1.win4000.com/wallpaper/0/540ec110ba06b.jpg']
    loop = asyncio.get_event_loop()
    bs = loop.run_until_complete(
        asyncio.wait([download(url, 16) for url in urls]))
