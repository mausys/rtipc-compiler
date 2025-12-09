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
    def __init__(self):

        lark_path = Path(__file__).parent
        self.parser = Lark.open(
            lark_path / "rtipc.lark",
            rel_to=__file__,
            parser="lalr",
            propagate_positions=True,
        )


    def create_field(self, field: SchemaField, structs: list[Struct]):
        if isinstance(field.type.type, str):
            type = structs.get(field.type.type)
            if type is None:
                raise StructNotFound(field.type.type, field.meta.line)
            return Field(field.name, type, field.type.length)
        else:
            return Field(field.name, field.type.type, field.type.length)


    def create_fields(self, schema_struct: SchemaStruct, structs: list[Struct]) -> list[Field]:
        fields = []

        for schema_field in schema_struct.fields:
            if isinstance(schema_field.type.type, str):
                type = structs.get(schema_field.type.type)
                if type is None:
                    raise StructNotFound(schema_field.type.type, schema_field.meta.line)
                field = Field(schema_field.name, type, schema_field.type.length)
                fields.append(field)
            else:
                field = Field(schema_field.name, schema_field.type.type, schema_field.type.length)
                fields.append(field)

        return fields



    def parse(self, file) -> list[Message]:
        tree = self.parser.parse(file.read())
        schema = RtIpcTransformer().transform(tree)
        structs = {}
        messages = []

        for schema_struct in schema:
            fields = self.create_fields(schema_struct, structs)
            if schema_struct.name in structs:
                raise StructAlreadyDefined(schema_struct.name, schema_struct.meta.line)
            if schema_struct.type == StructType.MESSAGE:
                messages.append(Message(schema_struct.name, fields, ''))
            else:
                structs[schema_struct.name] = Struct(
                    schema_struct.name, schema_struct.type == StructType.UNION, fields
                )
        return messages
