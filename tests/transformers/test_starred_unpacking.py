import pytest
from py_backwards.transformers.starred_unpacking import StarredUnpackingTransformer
from ..utils import transform, run


@pytest.mark.parametrize('before, after', [
    ('[1, 2, 3]', '[1, 2, 3]'),
    ('[1, 2, *range(5, 10), 3, 4]',
     '(([1, 2] + list(range(5, 10))) + [3, 4])'),
    ('[*range(5), *range(5, 10)]', '(list(range(5)) + list(range(5, 10)))'),
    ('[*range(5, 10)]', 'list(range(5, 10))'),
    ('print(1, 2, 3)', 'print(1, 2, 3)'),
    ('print(1, 2, *range(5, 10), 3, 4)',
     'print(*(([1, 2] + list(range(5, 10))) + [3, 4]))'),
    ('print(*range(5), *range(5, 10))',
     'print(*(list(range(5)) + list(range(5, 10))))'),
    ('print(*range(5, 10))',
     'print(*list(range(5, 10)))'),
])
def test_transform(before, after):
    assert transform(StarredUnpackingTransformer, before) == after


@pytest.mark.parametrize('code, result', [
    ('[1, 2, *range(5, 10), 3, 4]',
     [1, 2, 5, 6, 7, 8, 9, 3, 4]),
    ('[*range(5), *range(5, 10)]',
     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
    ('[*range(5, 10)]', [5, 6, 7, 8, 9]),
    ('to_tuple = lambda *xs: xs; to_tuple(1, 2, *range(5, 10), 3, 4)',
     (1, 2, 5, 6, 7, 8, 9, 3, 4)),
    ('to_tuple = lambda *xs: xs; to_tuple(*range(5), *range(5, 10))',
     (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)),
    ('to_tuple = lambda *xs: xs; to_tuple(*range(5, 10))',
     (5, 6, 7, 8, 9)),
])
def test_run(code, result):
    assert run(StarredUnpackingTransformer, code) == result
