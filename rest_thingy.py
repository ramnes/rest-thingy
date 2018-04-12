import functools
import os.path

import requests
from thingy import Thingy as BaseThingy
from thingy import NamesMixin, classproperty


def pluralize(url):
    return url + "s"


def extract(response):
    return response.json()


def parse_response(method):
    @functools.wraps(method)
    def wrapper(cls, *args, **kwargs):
        response = method(cls, *args, **kwargs)
        response = cls._extractor(response)
        return cls.bind(response)
    return wrapper


class Thingy(NamesMixin, BaseThingy):
    _base_url = None
    _extractor = extract
    _pluralizer = pluralize
    _resource_name = None

    @classmethod
    def bind(cls, document):
        if isinstance(document, dict):
            return cls(document)
        if isinstance(document, list):
            return [cls.bind(cls, o) for o in document]

    @classmethod
    def get_resource_name(cls):
        return "-".join(cls.names)

    @classproperty
    def base_url(cls):
        return cls._base_url

    @classproperty
    def resource_name(cls):
        if not cls._resource_name:
            cls._resource_name = cls.get_resource_name()
        return cls._resource_name

    @classproperty
    def plural_resource_name(cls):
        return cls._pluralizer(cls.resource_name)

    @classproperty
    def url(cls):
        return os.path.join(cls.base_url, cls.resource_name)

    @classproperty
    def plural_url(cls):
        return os.path.join(cls.base_url, cls.plural_resource_name)

    @classmethod
    @parse_response
    def get(cls, params=None, **kwargs):
        return requests.get(cls.plural_url, params, **kwargs)

    @classmethod
    @parse_response
    def get_one(cls, id=None, params=None, **kwargs):
        url = cls.url
        if id:
            url = os.path.join(url, id)
        return requests.get(url, params, **kwargs)

    @parse_response
    def patch(self):
        pass

    @parse_response
    def put(self):
        pass

    @parse_response
    def post(cls):
        pass


__all__ = ["Thingy"]
