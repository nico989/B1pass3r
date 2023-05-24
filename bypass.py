import os
import threading
import ipaddress
from waybackpy import WaybackMachineAvailabilityAPI, exceptions
from endpoint import Endpoint
from logger import log


class Bypass:
    _protocolVersions = ['HTTP/1.0', 'HTTP/2']
    _headersPath = ['X-Original-URL', 'X-Rewrite-URL', 'X-Override-URL']
    _hosts = ['', 'localhost', 'google.com', 'fake.org']
    _verbs = ['POST', 'PUT', 'PATCH', 'DELETE',
              'HEAD', 'OPTIONS', 'TRACE',
              'CONNECT', 'FAKE', 'GET']
    _agents = ['Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36',
               'Mozilla/5.0 (iPhone14,6; U; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19E241 Safari/602.1',
               'Mozilla/5.0 (Linux; Android 12; SM-X906C Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
               'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
               'Mozilla/5.0 (PlayStation; PlayStation 5/2.26) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15',
               'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
               'Fake User Agent']
    _headers = ['X-Originating-IP', 'X-Forwarded-For', 'X-Forwarded', 'Forwarded-For',
                'X-Forwarded-Host', 'X-Remote-IP', 'X-Remote-Addr', 'X-ProxyUser-Ip',
                'X-Original-URL', 'Client-IP', 'X-Client-IP', 'X-Host',
                'True-Client-IP', 'Cluster-Client-IP', 'X-ProxyUser-Ip', 'X-Custom-IP-Authorization']
    _commonLANs = ['10.64.8.0/23', '192.168.0.0/24']

    def __init__(self, endpoint: Endpoint) -> None:
        self._endpoint = endpoint

    @property
    def endpoint(self) -> Endpoint:
        return self._endpoint

    @endpoint.setter
    def method(self, endpoint: Endpoint) -> None:
        self._endpoint = endpoint

    def _testHTTPOrHTTPS(self) -> None:
        log.info('Start HTTP or HTTPS Testing')
        if self._endpoint.getSchema() == "https":
            newUrl = self._endpoint.url.replace("https", "http")
        else:
            newUrl = self._endpoint.url.replace("http", "https")
        log.info(f'GET request to New URL {newUrl}')
        self._endpoint.makeRequest(url=newUrl, timeout=1)
        log.info('End HTTP or HTTPS Testing')

    def _protocolFuzzing(self) -> None:
        log.info('Start Protocol Fuzzing')
        for protocolVersion in self._protocolVersions:
            self._endpoint.makeRequest(protocolVersion=protocolVersion)
        log.info('End Protocol Fuzzing')

    def _testIPAndCNAME(self) -> None:
        log.info('Start IP or CNAME Testing')
        try:
            ip = f'{self._endpoint.getSchema()}://{self._endpoint.getIP()}'
            url = f'{ip}/{self._endpoint.getPath()}'
            log.info(f'Requesting via IP {url}')
            self._endpoint.makeRequest(url=url)
        except Exception as e:
            log.warning(
                f'[-] Exception {e} generated by IP {url}')
        try:
            cname = f'{self._endpoint.getSchema()}://{self._endpoint.getDomain()}'
            url = f'{cname}/{self._endpoint.getPath()}'
            log.info(f'Requesting via CNAME {url}')
            self._endpoint.makeRequest(url=url)
        except Exception as e:
            log.warning(
                f'[-] Exception {e} generated by CNAME {url}')
        log.info('End IP or CNAME Testing')

    def _headersFuzzingPath(self) -> None:
        path = self._endpoint.getPath()
        log.info(f'Start Headers Fuzzing with Path {self._endpoint.getPath()}')
        for header in self._headersPath:
            self._endpoint.makeRequest(headers={header: path})
        log.info(f'End Headers Fuzzing with Path {path}')

    def _hostHeaderFuzzing(self) -> None:
        log.info('Start Host Header Fuzzing')
        for host in self._hosts:
            self._endpoint.makeRequest(headers={'Host': host})
        log.info('End Host Header Fuzzing')

    def _verbFuzzing(self) -> None:
        log.info('Start Verb Fuzzing')
        for verb in self._verbs:
            self._endpoint.makeRequest(method=verb)
        log.info('Start Verb Fuzzing with X-HTTP-Method-Override Header')
        for verb in self._verbs:
            self._endpoint.makeRequest(
                headers={'X-HTTP-Method-Override': verb})
        log.info('End Verb Fuzzing')

    def _userAgentFuzzing(self) -> None:
        log.info('Start User Agent Fuzzing')
        for agent in self._agents:
            self._endpoint.makeRequest(
                headers={'User-Agent': agent})
        log.info('End User Agent Fuzzing')

    def _headersIPFuzzing(self, ip: str = '127.0.0.1') -> None:
        log.info(f'Start Headers Fuzzing with IP {ip}')
        for header in self._headers:
            self._endpoint.makeRequest(headers={header: ip})
        log.info(f'End HTTP Headers Fuzzing with IP {ip}')

    def _pathFuzzing(self) -> None:
        log.info('Start Path Fuzzing')
        pathVariants = [f'{self._endpoint.getMainUrl()}/%2e/{self._endpoint.getPath()}',
                        f'{self._endpoint.getMainUrl()}/%252e/{self._endpoint.getPath()}',
                        f'{self._endpoint.getMainUrl()}/{self._endpoint.getPath().upper()}',
                        f'{self._endpoint.url}/',
                        f'{self._endpoint.url}/.',
                        f'{self._endpoint.url}//',
                        f'{self._endpoint.getMainUrl()}//{self._endpoint.getPath()}',
                        f'{self._endpoint.getMainUrl()}//{self._endpoint.getPath()}//',
                        f'{self._endpoint.getMainUrl()}/./{self._endpoint.getPath()}/..',
                        f'{self._endpoint.getMainUrl()}/;/{self._endpoint.getPath()}',
                        f'{self._endpoint.getMainUrl()}/,;/{self._endpoint.getPath()}',
                        f'{self._endpoint.getMainUrl()}//;//{self._endpoint.getPath()}',
                        f'{self._endpoint.url}.json',
                        f'{self._endpoint.url}..;/',
                        f'{self._endpoint.getMainUrl()}/../{self._endpoint.getPath()}',
                        f'{self._endpoint.getMainUrl()}/..;/{self._endpoint.getPath()}',
                        f'{self._endpoint.url}%20/',
                        f'{self._endpoint.getMainUrl()}/%20{self._endpoint.getPath()}%20/',
                        f'{self._endpoint.url};/',
                        f'{self._endpoint.url}/~',
                        f'{self._endpoint.getMainUrl()}/./{self._endpoint.getPath()}/./',
                        f'{self._endpoint.url}?param',
                        f'{self._endpoint.url}#']
        for pathVariant in pathVariants:
            self._endpoint.makeRequest(url=pathVariant)
        log.info('End Path Fuzzing')

    def _verbsHeadersIPFuzzing(self, ip: str = '127.0.0.1') -> None:
        log.info('Start Verbs and Headers IP Fuzzing')
        for verb in self._verbs:
            for header in self._headers:
                self._endpoint.makeRequest(
                    method=verb, headers={header: ip})
        log.info('End Verbs and Headers IP Fuzzing')

    def _getWaybackMachine(self) -> None:
        log.info('Start Wayback Machine Testing')
        try:
            wayback = WaybackMachineAvailabilityAPI(
                url=self._endpoint.getDomain())
            log.info(
                f'[+] Found something on Wayback Machine, oldest archive {wayback.newest()}')
        except exceptions.ArchiveNotInAvailabilityAPIResponse:
            log.warning('[-] Nothing on Wayback Machine!')
        except:
            log.error('[-] General Connection Error for Wayback Machine!')
        log.info('End Wayback Machine Testing')

    def _localIPFuzzing(self) -> None:
        log.info('Start Local IP Fuzzing')
        for commonLAN in self._commonLANs:
            threads = []
            network = ipaddress.ip_network(commonLAN)
            hosts = list(network.hosts())
            for host in hosts:
                t = threading.Thread(target=self._headersIPFuzzing,
                                     args=(str(host),))
                threads.append(t)
                t.start()
            for thread in threads:
                thread.join()
        log.info('End Local IP Fuzzing')

    def _pathUnicodeFuzzing(self) -> None:
        log.info('Start Path Unicode Fuzzing')
        unicodes = []
        with open(f'{os.path.dirname(__file__)}/unicode.txt', 'r') as file:
            unicodes = file.readlines()
        threads = []
        for unicode in unicodes:
            url = f'{self._endpoint.getMainUrl()}/{unicode}/{self._endpoint.getPath()}'.replace('\n', '')
            t = threading.Thread(target=self._endpoint.makeRequest,
                                 args=(url,))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()
        log.info('End Path Unicode Fuzzing')

    def _getStressTest(self) -> None:
        log.info('Start Get Stress Test')
        threads = []
        for index in range(300):
            t = threading.Thread(target=self._endpoint.makeRequest,
                                 args=(index,))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()
        log.info('End Get Stress Test')

    def bypass(self) -> None:
        self._testHTTPOrHTTPS()
        self._protocolFuzzing()
        self._testIPAndCNAME()
        self._headersFuzzingPath()
        self._hostHeaderFuzzing()
        self._verbFuzzing()
        self._userAgentFuzzing()
        self._headersIPFuzzing()
        self._pathFuzzing()
        self._verbsHeadersIPFuzzing()
        self._getWaybackMachine()
        self._getStressTest()
        self._pathUnicodeFuzzing()
        self._localIPFuzzing()

    def __str__(self) -> str:
        return f'Bypass endpoint:{self._endpoint}'
