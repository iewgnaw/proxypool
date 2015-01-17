import re
import random
import requests
from gevent import monkey
monkey.patch_all(thread=False)
from gevent.pool import Pool

import sys
sys.path.append('..')
from config import config
from utility.redis_manager import RedisManager

RE_FOR_IP_PORT1 = re.compile(
    r'(?P<ip>(?:\d{1,3}\.){3}\d{1,3})</td>\n?\s*<td.*?>\s*(?P<port>\d{1,4})')
RE_FOR_IP_PORT2 = re.compile(
    r'(?:\d{1,3}\.){1,3}\d{1,3}:\d{1,3}')

SITE_POOL = Pool(5)
PROXY_CHECK_POOL = Pool(30)


class Crawler(object):

    def __init__(self):
        pass

    def run(self):
        proxy_sites = config.proxy_sites()
        random.shuffle(proxy_sites)
        proxies_list = SITE_POOL.map(self.crawl, proxy_sites)
        proxies = [item for sublist in proxies_list for item in sublist]
        avaliable_proxies = PROXY_CHECK_POOL.map(self._check_proxy_avaliable,
                                                 proxies)
        self._save_to_redis(avaliable_proxies)

    def crawl(self, site_url):
        proxies = []
        config.HEADER.update({'Host': site_url.split('/')[2]})
        response = requests.get(site_url, headers=config.HEADER)

        if not response.ok:
            return []
        for match in RE_FOR_IP_PORT1.finditer(response.text):
            ip = match.groupdict()['ip']
            port = match.groupdict()['port']
            proxies.append("%s:%s" % (ip, port))
        for proxy in RE_FOR_IP_PORT2.findall(response.text):
            proxies.append(proxy)
        return proxies

    def _check_proxy_avaliable(self, proxy):
        return proxy

    def _save_to_redis(self, proxies):
        rediss_session = RedisManager.get_instance()
        rediss_session.sadd(config.redis_set(), *proxies)


if __name__ == '__main__':
    Crawler().run()
