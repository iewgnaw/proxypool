import time
import logging

from utility.redis_manager import RedisManager
from config import config
from crawler.crawler import Crawler

logger = logging.getLogger("proxypool")
logger.setLevel(logging.DEBUG)


class ProxyPool(object):

    rd_session = RedisManager.get_instance()

    @classmethod
    def monitor(cls):
        while 1:
            if cls.rd_session.scard(config.redis_set()) == 0:
                logger.debug("START: crawl")
                cls._crawl()
                logger.debug("END: crawl")
            time.sleep(1)

    @classmethod
    def _crawl(cls):
        Crawler().run()

    @classmethod
    def get(cls, block=True, timeout=None):
        if not block:
            return cls.rd_session.srandmember(config.redis_set())
        elif timeout is None:
            proxy = cls.rd_session.srandmember(config.redis_set())
            while proxy is None:
                proxy = cls.rd_session.srandmember(config.redis_set())
            return proxy
        elif timeout < 0:
            raise ValueError("'timeout' must be a non-negative number")
        else:
            endtime = time.time() + timeout
            proxy = cls.rd_session.srandmember(config.redis_set())
            while proxy is None:
                if time() > endtime:
                    return None
                proxy = cls.rd_session.srandmember(config.redis_set())
            return proxy

    @classmethod
    def size(cls):
        return cls.rd_session.scard(config.redis_set())

    @classmethod
    def delete(cls, proxy):
        pass

    @classmethod
    def empty(cls):
        cls.rd_session.delete(config.redis_set())


if __name__ == "__main__":
    ProxyPool.monitor()
