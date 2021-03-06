# -*- coding:utf-8 -*-
import redis
import config


class RedisManager(object):

    rdb = None

    @staticmethod
    def get_instance():
        conf = config.redis_conf()
        if not RedisManager.rdb:
            RedisManager.rdb = redis.StrictRedis(
                host=conf['host'],
                port=conf['port'],
                db=conf['db']
            )
        return RedisManager.rdb
