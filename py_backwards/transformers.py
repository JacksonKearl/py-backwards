from typed_ast import ast3 as ast
from astunparse import unparse
from autopep8 import fix_code


class FormattedValuesTransformer(ast.NodeTransformer):
    target = (3, 5)

    def visit_FormattedValue(self, node):
        if node.format_spec:
            template = ''.join(['{:', node.format_spec.s, '}'])
        else:
            template = '{}'

        format_call = ast.Call(func=ast.Attribute(value=ast.Str(s=template),
                                                  attr='format'),
                               args=[node.value],
                               keywords=[])
        return self.generic_visit(format_call)

    def visit_JoinedStr(self, node):
        join_call = ast.Call(func=ast.Attribute(value=ast.Str(s=''),
                                                attr='join'),
                             args=[ast.List(elts=node.values, ctx=ast.Load())],
                             keywords=[])
        return self.generic_visit(join_call)


class FunctionsAnnotationsTransformer(ast.NodeTransformer):
    target = (2, 7)

    def visit_arg(self, node):
        node.annotation = None
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node.returns = None
        return self.generic_visit(node)


class VariablesAnnotationsTransformer(ast.NodeTransformer):
    target = (3, 5)

    def visit_AnnAssign(self, node):
        if node.value is None:
            return

        return self.generic_visit(ast.Assign(targets=[node.target],
                                             value=node.value))


class StarredUnpackingTransformer(ast.NodeTransformer):
    target = (3, 4)

    def _has_starred(self, xs):
        for x in xs:
            if isinstance(x, ast.Starred):
                return True

        return False

    def _prepare_lists(self, xs):
        """Wrap starred in list call and list elts to just List."""
        for x in xs:
            if isinstance(x, ast.Starred):
                yield ast.Call(
                    func=ast.Name(id='list'),
                    args=[x.value],
                    keywords=[])
            elif x:
                yield ast.List(elts=x)

    def _split_by_starred(self, xs):
        """Split `xs` to separate list by Starred."""
        lists = [[]]
        for x in xs:
            if isinstance(x, ast.Starred):
                lists.append(x)
                lists.append([])
            else:
                lists[-1].append(x)
        return lists

    def _merge_lists(self, xs):
        """Merge lists by summing them."""
        if len(xs) == 1:
            return xs

        result = ast.BinOp(left=xs[0], right=xs[1], op=ast.Add())
        for x in xs[2:]:
            result = ast.BinOp(left=result, right=x, op=ast.Add())
        return result

    def _to_sum_of_lists(self, xs):
        """Convert list of arguments / list to sum of lists."""
        splitted = self._split_by_starred(xs)
        prepared = list(self._prepare_lists(splitted))
        return self._merge_lists(prepared)

    def visit_List(self, node):
        if not self._has_starred(node.elts):
            return self.generic_visit(node)

        return self._to_sum_of_lists(node.elts)

    def visit_Call(self, node):
        if not self._has_starred(node.args):
            return self.generic_visit(node)

        args = self._to_sum_of_lists(node.args)
        node.args = [ast.Starred(value=args)]
        return node


transformers = [FormattedValuesTransformer,
                FunctionsAnnotationsTransformer,
                VariablesAnnotationsTransformer,
                StarredUnpackingTransformer]


def transform(code, target):
    tree = ast.parse(code)
    for transformer in transformers:
        if transformer.target >= target:
            transformer().visit(tree)
    return fix_code(unparse(tree))