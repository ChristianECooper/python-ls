from collections import Container

import pandas as pd

# sentinel
BAD = object()


def ls(obj, attr=None, depth=None, dunder=False, under=True):
    if depth is None and attr is None:
        depth = 1

    for attr, value in iter_ls(obj, attr=attr, depth=depth,
                               dunder=dunder, under=under):
        size = ''
        if isinstance(value, pd.DataFrame):
            size = '{0}x{1}'.format(*value.shape)
        elif isinstance(value, Container):
            size = len(value)
        type_name = type(value).__name__
        print('{:<60}{:>20}{:>7}'.format(attr, type_name, size))


def xdir(obj, attr=None, depth=None, dunder=False, under=True):
    if depth is None and attr is None:
        depth = 1
    return list((x[0] for x in iter_ls(obj, attr=attr, depth=depth,
                                       dunder=dunder, under=under)))


def iter_ls(obj, attr=None, depth=1, dunder=False, under=True,
            visited=None, current_depth=1, path=''):
    visited = visited or set()

    if current_depth <= depth:
        if id(obj) not in visited:
            visited.add(id(obj))

            callbacks = []

            def include(a):
                for c in callbacks:
                    if not c(a):
                        return False
                return True

            def exclude_dunders(a):
                return not a.startswith('__')

            def exclude_unders(a):
                return not a.startswith('_')

            def attr_filter_callback(a):
                return attr in a

            if attr:
                callbacks.append(attr_filter_callback)

            if not dunder:
                callbacks.append(exclude_dunders)

            if not under:
                callbacks.append(exclude_unders)

            if isinstance(obj, dict):
                attrs = [str(k) for k in obj.keys()]
            elif isinstance(obj, pd.DataFrame):
                attrs = [str(c) for c in obj.columns]
            else:
                attrs = dir(obj)

            for a in attrs:
                if isinstance(obj, dict) or isinstance(obj, pd.DataFrame):
                    new_path = path + '[%r]' % a
                else:
                    if path:
                        new_path = '.'.join([path, a])
                    else:
                        new_path = a

                try:
                    if isinstance(obj, dict) or isinstance(obj, pd.DataFrame):
                        val = obj[a]
                    else:
                        val = getattr(obj, a)
                except Exception:
                    val = BAD

                if include(a):
                    suffix = ''
                    if val is not BAD:
                        if callable(val):
                            suffix = '()'
                    yield new_path + suffix, val

                if val is not BAD and not a.startswith('__'):
                    for sub_a, sub_val in iter_ls(val, attr=attr, depth=depth, dunder=dunder,
                                                  under=under, visited=visited,
                                                  current_depth=current_depth + 1, path=new_path):
                        yield sub_a, sub_val