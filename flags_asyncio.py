#!/usr/bin/env python3.5

import collections
import asyncio
import aiohttp
from aiohttp import web
import time
import tqdm

from flags import BASE_URL, save_flag, show, main
import flags

POP20_CC = ('CN IN US ID BR PK NG BD RU JP '
            'MX PH VN ET DG DE IR TR CD FR').split()
BASE_URL = 'http://flupy.org/data/flags'
Result = collections.namedtuple('Result', 'status cc')


class HTTPStatus:
    ok = 'ok'
    not_found = 'not found'
    error = 'error'


class FetchError(Exception):
    def __init__(self, country_code):
        self.country_code = country_code


async def get_flag(cc):
    url = '{}/{cc}/{cc}.gif'.format(BASE_URL, cc=cc.lower())
    resp = await aiohttp.request('GET', url)
    if resp.status == 200:
        image = await resp.read()
        return(image)
    elif resp.status == 404:
        raise web.HTTPNotFound()
    else:
        raise aiohttp.HttpProcessingError(
            code=resp.status, message=resp.reason,
            header=resp.headers)


async def download_one(cc, base_url, semaphore, verbose):
    try:
        with (await semaphore):
            image = await get_flag(cc)
    except web.HTTPNotFound:
        status = HTTPStatus.not_found
        msg = 'not found'
    except Exception as exc:
        raise FetchError(cc) from exc
    else:
        save_flag(image, cc.lower() + '.gif')
        status = HTTPStatus.ok
        msg = 'OK'

    if verbose and msg:
        print(cc, msg)

    return(Result(status, cc))


async def downloader_coro(cc_list, base_url, verbose, concur_req):
    counter = collections.Counter()
    semaphore = asyncio.Semaphore(concur_req)
    to_do = [download_one(cc, base_url, semaphore, verbose)
             for cc in cc_list]
    to_do_iter = asyncio.as_completed(to_do)
    if not verbose:
        to_do_iter = tqdm.tqdm(to_do_iter, total=len(cc_list))
    for future in to_do_iter:
        try:
            res = await future
        except FetchError as exc:
            country_code = exc.country_code
            try:
                error_msg = exc.__cause__.args[0]
            except IndexError:
                error_msg = exc.__cause__.__class__.__name__
            if verbose and error_msg:
                msg = '*** Error for {}: {}'
                print(msg.format(country_code, error_msg))
            status = HTTPStatus.error
        else:
            status = res.status
        counter[status] += 1
    return(counter)


def download_many(cc_list, base_url, verbose, concur_req):
    loop = asyncio.get_event_loop()
    coro = downloader_coro(cc_list, base_url, verbose, concur_req)
    counts = loop.run_until_complete(coro)
    loop.close()

    return(counts)


def main(download_many, default_concur_req, concur_req):
    t0 = time.time()
    count = download_many(POP20_CC, BASE_URL, False, concur_req)
    elapsed = time.time() - t0
    msg = '\n{} flags download in {:.2f}s'
    print(msg.format(count, elapsed))


if __name__ == '__main__':
    DEFAULT_CONCUR_REQ = 5
    MAX_CONCUR_REQ = 1000
    main(download_many, DEFAULT_CONCUR_REQ, MAX_CONCUR_REQ)
