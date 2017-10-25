from camisole.conf import conf


def test_read():
    conf.reset()
    assert len(conf)
    assert list(conf)


def test_conf_default():
    conf.reset()
    assert 'isolate-conf' in conf
    assert conf['isolate-conf'] == '/etc/isolate'


def test_conf_merge():
    conf.reset()
    conf.merge({'foo': {'bar': 1, 'baz': 2}})
    assert conf['foo']['bar'] == 1
    assert conf['foo']['baz'] == 2

    conf.merge({"foo": {'baz': 3}})
    assert conf['foo']['bar'] == 1
    assert conf['foo']['baz'] == 3
    conf.reset()
