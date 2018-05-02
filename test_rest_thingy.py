import pytest
from rest_thingy import Thingy, parse_response


def test_parse_response():
    class Foo:
        @classmethod
        def extract(cls, response):
            cls.extract_called = True
            return response

        @classmethod
        def deserialize(cls, response):
            cls.deserialize_called = True
            return response

        @classmethod
        def bind(cls, response):
            cls.bind_called = True
            return response

        @classmethod
        @parse_response
        def bar(cls):
            return "baz"

    assert Foo.bar() == "baz"
    assert Foo.extract_called
    assert Foo.deserialize_called
    assert Foo.bind_called


def test_thingy_bind_dict():
    thingy = Thingy.bind({"foo": "bar"})
    assert isinstance(thingy, Thingy)
    assert thingy.foo == "bar"
    assert thingy.__dict__ == {"foo": "bar"}


def test_thingy_bind_list():
    thingies = Thingy.bind([{"foo": "bar"}, {"baz": "qux"}])
    assert isinstance(thingies, list)
    assert len(thingies) == 2

    assert isinstance(thingies[0], Thingy)
    assert thingies[0].foo == "bar"
    assert isinstance(thingies[1], Thingy)
    assert thingies[1].baz == "qux"


def test_thingy_bind_unknown():
    with pytest.raises(TypeError):
        Thingy.bind("")
