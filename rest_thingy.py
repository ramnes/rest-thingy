import functools
import fnmatch
import os.path

import requests
from thingy import Thingy as BaseThingy
from thingy import NamesMixin, classproperty


def parse_response(method):
    @functools.wraps(method)
    def wrapper(cls, *args, **kwargs):
        response = method(cls, *args, **kwargs)
        response = cls.extract(response)
        if cls.deserialize:
            response = cls.deserialize(response)
        return cls.bind(response)
    return wrapper


class Thingy(NamesMixin, BaseThingy):
    _base_url = None
    _inferences = {}
    _resource_name = None

    @classmethod
    def bind(cls, response):
        if isinstance(response, dict):
            return cls(response)
        if isinstance(response, list):
            return [cls.bind(o) for o in response]
        raise TypeError("Can't bind a '{}'.".format(type(response)))

    @classmethod
    def deserialize(cls, response):
        if cls._inferences:
            for pattern, inference in cls._inferences.items():
                for key, value in response.items():
                    if fnmatch.fnmatch(key, pattern):
                        response[key] = inference(value)
        return response

    @classmethod
    def extract(cls, response):
        return response.json()

    @classmethod
    def get_resource_name(cls):
        return "-".join(cls.names)

    @classmethod
    def pluralize(cls, url):
        return url + "s"

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
        return cls.pluralize(cls.resource_name)

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


class MarshmallowMixin():
    _schema = None

    @classmethod
    def deserialize(cls, response):
        data, errors = cls._schema.load(response)
        if errors:
            raise TypeError(errors)
        response.update(data)
        return response


__all__ = ["MarshmallowMixin", "Thingy"]
