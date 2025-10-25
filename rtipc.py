"""
Lark Grammar
============

A reference implementation of the Lark grammar (using LALR(1))
"""
from lark import Lark, ast_utils, Transformer, v_args
from pathlib import Path
import message

class TreeToMessage(Transformer):
    @v_args(inline=True)
    def string(self, s):
        return s[1:-1].replace('\\"', '"')
    def message(self, m):
        print("message {}", m)
        return list
    def struct(self, children):
        print("struct {}", children[0].type)
        return list

lark_path = Path(__file__).parent

parser = Lark.open(lark_path / 'rtipc.lark', rel_to=__file__, parser='lalr', transformer=TreeToMessage())



def test():
    
    tree = parser.parse(open("test.rtipc").read())
    print(tree.pretty())

if __name__ == '__main__':
    test()
