from typing import Union
from enum import Enum
from dataclasses import dataclass
from lark import Lark, Transformer, v_args
from lark.tree import Meta
from pathlib import Path

from message import Message, Struct, Field, Primitive


class StructType(Enum):
    STRUCT = 1
    UNION = 2
    MESSAGE = 3


@dataclass
class SchemaType:
    type: Union[str, Primitive]
    length: int


@dataclass
class SchemaField:
    meta: Meta
    name: str
    type: SchemaType


@dataclass
class SchemaStruct:
    meta: Meta
    name: str
    type: StructType
    fields: list[SchemaField]


class StructNotFound(Exception):
    def __init__(self, name, line):
        super().__init__(f"struct {name} in line {line} not defined")


class StructAlreadyDefined(Exception):
    def __init__(self, name, line):
        super().__init__(f"struct {name} in line {line} already defined")


class RtIpcTransformer(Transformer):
    INT = int
    CNAME = str
    fields = list

    @v_args(inline=True)
    def length(self, length):
        return length

    @v_args(inline=True)
    def name(self, name):
        return name

    @v_args(inline=True)
    def primitive(self, str_prim):
        try:
            primitive = Primitive[str_prim.upper()]
            return SchemaType(primitive, 1)
        except ValueError:
            raise SyntaxError(f"unnown primitive: {str_prim}")

    @v_args(inline=True)
    def type(self, name):
        return SchemaType(name, 1)

    @v_args(inline=True)
    def array(self, type, length):
        type.length = length
        return type

    @v_args(inline=True, meta=True)
    def field(self, meta, name, type):
        return SchemaField(meta, name, type)

    @v_args(inline=True, meta=True)
    def message(self, meta, name, fields):
        return SchemaStruct(meta, name, StructType.MESSAGE, fields)

    @v_args(inline=True, meta=True)
    def struct(self, meta, name, fields):
        return SchemaStruct(meta, name, StructType.STRUCT, fields)

    @v_args(inline=True, meta=True)
    def union(self, meta, name, fields):
        return SchemaStruct(meta, name, StructType.UNION, fields)

    def start(self, children):
        return children


class RtIpcParser:
    def __init__(self, path):
        self.structs = {}
        self.messages = {}
        lark_path = Path(__file__).parent
        parser = Lark.open(
            lark_path / "rtipc.lark",
            rel_to=__file__,
            parser="lalr",
            propagate_positions=True,
        )
        tree = parser.parse(open(path).read())
        schema = RtIpcTransformer().transform(tree)

        for s in schema:
            self.create_struct(s)

    def create_field(self, field: SchemaField):
        if isinstance(field.type.type, str):
            type = self.structs.get(field.type.type)
            if type is None:
                raise StructNotFound(field.type.type, field.meta.line)
            return Field(field.name, type, field.type.length)
        else:
            return Field(field.name, field.type.type, field.type.length)

    def create_struct(self, struct: SchemaStruct):
        fields = []

        for field in struct.fields:
            fields.append(self.create_field(field))

        if struct.name in self.structs:
            raise StructAlreadyDefined(struct.name, struct.meta.line)
        if struct.type == StructType.MESSAGE:
            self.messages[struct.name] = Message(struct.name, fields)
        else:
            self.structs[struct.name] = Struct(
                struct.name, struct.type == StructType.UNION, fields
            )
