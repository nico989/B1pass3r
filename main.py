#! /usr/bin/python3
import argparse
from endpoint import Endpoint
from bypass import Bypass
from logger import log


def main() -> None:
    parser = argparse.ArgumentParser(
        description='403 and 401 Bypasser based on Known Techniques')
    parser.add_argument('-u', '--url',
                        type=str,
                        required=True,
                        help='URL to test',
                        metavar='\b')
    parser.add_argument('-c', '--cookies',
                        type=str,
                        required=False,
                        default=None,
                        help='Session Cookies',
                        metavar='\b')
    args = parser.parse_args()
    url = args.url
    cookies = args.cookies

    endpoint = Endpoint(url, cookies)
    if endpoint.checkUrl() and endpoint.makeRequest():
        log.info(f'URL provided {endpoint.url} is Valid!')
        bypass = Bypass(endpoint)
        bypass.bypass()
    else:
        log.critical(f'URL provided {endpoint.url} is NOT Valid!')


if __name__ == '__main__':
    main()
