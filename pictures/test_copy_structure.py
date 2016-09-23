import sys
from cStringIO import StringIO
from contextlib import contextmanager

from . import copy_structure as cs


class EqStringIO(object):
    def __init__(self, *args, **kwargs):
        self.string_io = StringIO(*args, **kwargs)

    def __eq__(self, other):
        return self.value() == other

    def __repr__(self):
        return '<sys.stdout ' + str(self.value()) + '>'

    def value(self):
        return self.string_io.getvalue().rstrip('\n').split('\n')


@contextmanager
def capture():
    mock = EqStringIO()
    out, sys.stdout = sys.stdout, mock.string_io
    try:
        yield mock
    except:
        import traceback
        traceback.print_exc()
        out.write(sys.stdout.getvalue())
    finally:
        out.write(sys.stdout.getvalue())
        sys.stdout = out


class MockStack(object):
    def __init__(self, mock):
        self.stack = [mock]

    def __call__(self, *args, **kwargs):
        return self.stack.pop(0)(*args, **kwargs)

    @classmethod
    def push(cls, module, function, mock):
        to_mock = getattr(module, function)
        if isinstance(to_mock, cls):
            to_mock.stack.append(mock)
        else:
            setattr(module, function, cls(mock))


def mock_open(module, filename, opt, content):
    class IterExit(object):
        def __init__(self, v):
            self.v = v
        def __enter__(self):
            return self.v
        def __exit__(self, *args):
            pass
    def open_(filename_, opt_):
        assert filename_ == filename
        assert opt_ == opt
        return IterExit([l + '\n' for l in content])
    open_.__exit__ = lambda: None
    MockStack.push(module, 'open', open_)


def run(left_content, right_content):
    mock_open(cs, 'left_file', 'r', left_content)
    mock_open(cs, 'right_file', 'r', right_content)
    with capture() as output:
        cs.main(['left_file', 'right_file'])
    return output


def script(content):
    return ['#!/bin/sh', 'set -e'] + content


def test_same():
    output = run(['b   a/f2', 'a b/f1'], ['b a/f2', 'a b/f1'])
    assert output.value() == ['# Nothing to do, left and right are identical']


def test_same_root():
    output = run(['b   f2', 'a f1'], ['b f2', 'a f1'])
    assert output.value() == ['# Nothing to do, left and right are identical']


def test_more_on_left():
    output = run(['b a/f2', 'a b/f1'], ['b a/f2'])
    assert output.value() == ['# Nothing to do, right is a subset of left']


def test_more_on_right():
    output = run(['b a/f2'], ['b a/f2', 'a b/f1'])
    assert output.value() == script(['# Did not move:', '# b/f1'])


def test_nothing_to_do():
    output = run(['b a/f2', 'c b/f3'], ['b a/f2', 'a a/f1'])
    assert output.value() == script(['# Did not move:', '# a/f1'])


def test_move_dir():
    output = run(['a a/f1', 'b a/f2', 'c d/f3'], ['a b/f1', 'b b/f2', 'c f/f3'])
    assert output.value() == script(['mkdir -p a', 'mkdir -p d', 'mv b a', 'mv f d'])


def test_move_one_file():
    output = run(['a a/f1'], ['a b/f1'])
    assert output.value() == script(['mkdir -p a', 'mv b a'])


def test_move_nested():
    output = run(['a a/a/f1', 'b a/a/f2'], ['a b/c/d/f1', 'b b/c/d/f2'])
    assert output.value() == script(['mkdir -p a/a', 'mv b/c/d a/a'])


def test_move_mixed():
    output = run(['a a/f1', 'b b/f2', 'x g/f1', 'y g/f2'], ['a x/f1', 'b x/f2', 'c x/f3', 'x f/f1', 'y f/f2'])
    assert output.value() == script([
        '# Did not move:', '# x/f3',
        'mkdir -p a',
        'mkdir -p b',
        'mkdir -p g',
        'mv f g',
        'mv x/f1 a/f1',
        'mv x/f2 b/f2'
    ])


def test_move_together():
    output = run(['a a/f1', 'b a/f2'], ['a x/f1', 'b x/f2', 'y x/f3'])
    assert output.value() == script([
        'mkdir -p a',
        'mv x a'
    ])


def test_move_together_multiple():
    output = run(['a a/f1', 'b a/f2', 'c a/f3', 'd a/f4'],
                 ['a x/f1', 'b x/f2', 'x x/f3', 'c y/f3', 'd y/f4', 'y y/f5'])
    assert output.value() == script([
        'mkdir -p a',
        'mv x/* a',
        'mv y/* a',
    ])


def test_move_together_multiple_():
    output = run(['a a/f1', 'b a/f2', 'c a/f3', 'd a/f4'],
                 ['a x/f1', 'b x/f2', 'x x/f3', 'c y/g1', 'd y/g2', 'y y/g3'])
    assert output.value() == script([
        'mkdir -p a',
        'mv x/* a',
        'mv y/g1 a/f3',
        'mv y/g2 a/f4',
        'mv y/g3 a/g3',
    ])


def test_move_not_together_on_split():
    output = run(['a a/f1', 'b a/f2', 'c b/f3'], ['a x/f1', 'b x/f2', 'c x/f3', 'd x/f4'])
    assert output.value() == script([
        '# Did not move:',
        '# x/f4',
        'mkdir -p a',
        'mkdir -p b',
        'mv x/f1 a/f1',
        'mv x/f2 a/f2',
        'mv x/f3 b/f3'
    ])


def test_move_not_together_on_split_():
    output = run(['a a/f1', 'b a/f2', 'c b/f3'], ['a x/f1', 'b x/f2', 'c x/f3'])
    assert output.value() == script([
        'mkdir -p a',
        'mkdir -p b',
        'mv x/f1 a/f1',
        'mv x/f2 a/f2',
        'mv x/f3 b/f3'
    ])


def test_move_not_together_on_split__():
    output = run(['a a/f1', 'b a/f2', 'c b/f3', 'd b/f4'], ['a x/f1', 'b x/f2', 'c x/f3', 'd y/f4'])
    assert output.value() == script([
        'mkdir -p a',
        'mkdir -p b',
        'mv x/f1 a/f1',
        'mv x/f2 a/f2',
        'mv x/f3 b/f3',
        'mv y/* b'
    ])


def test_move_not_together_on_split__():
    output = run(['a a/g1', 'b a/g2', 'c b/g3', 'd b/g4'], ['a x/f1', 'b x/f2', 'c x/f3', 'd y/f4'])
    assert output.value() == script([
        'mkdir -p a',
        'mkdir -p b',
        'mv x/f1 a/g1',
        'mv x/f2 a/g2',
        'mv x/f3 b/g3',
        'mv y/f4 b/g4'
    ])


def test_move_root():
    output = run(['a f1', 'b f2'], ['a f3', 'b f4'])
    assert output.value() == script(['mv f3 f1', 'mv f4 f2'])


def test_no_move_root():
    output = run(['a f1', 'b f2'], ['c f3', 'd f4'])
    assert output.value() == script(['# Did not move:', '# f3', '# f4'])
