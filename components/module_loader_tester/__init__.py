from .testdir import test2

b = test2.c


def test():
    try:
        from ..knowledge_lib import h

        print(h)
    except Exception as e:
        print(e)


test()
