#!/usr/bin/env python3.5

import asyncio
import time
import aiohttp
import os

POP20_CC = ('CN IN US ID BR PK NG BD RU JP '
            'MX PH VN ET DG DE IR TR CD FR').split()

BASE_URL = 'http://flupy.org/data/flags'

DEST_DIR = '/Users/app/Downloads'


class HTTPStatus:
    ok = 0
    error = 0


def save_flag(content, fn):
    HTTPStatus.ok += 1
    print('{} saving {}'.format(HTTPStatus.ok, fn))
    with open(os.path.join(DEST_DIR, fn), 'wb') as f:
        f.write(content)


async def download_one(cc):
    url = '{}/{cc}/{cc}.gif'.format(BASE_URL, cc=cc.lower())
    resp = await aiohttp.request('GET', url)
    image = await resp.read()
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, save_flag, image, cc.lower()+'.gif')
    return(url)


async def download_coro(cc_list):
    to_do = [download_one(cc) for cc in cc_list]
    to_do_iter = asyncio.as_completed(to_do, timeout=5)
    for future in to_do_iter:
        res = await future

    return(res)


def download_many(cc_list):
    loop = asyncio.get_event_loop()
    coros = download_coro(cc_list)
    results = loop.run_until_complete(coros)
    loop.close()


def main(coro, cc_list):
    t = time.time()
    coro(cc_list)
    print('download finished in {}sec'.format(time.time() - t))


if __name__ == '__main__':
    main(download_many, POP20_CC)
