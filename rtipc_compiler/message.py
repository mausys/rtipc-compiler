from typing import Union
from enum import Enum
from dataclasses import dataclass


class Primitive(Enum):
    BOOL = 1
    U8 = 2
    I8 = 3
    U16 = 4
    I16 = 5
    U32 = 6
    F32 = 6
    U64 = 7
    I64 = 8
    F64 = 8
    U128 = 9
    I128 = 10
    F128 = 11


@dataclass
class Struct:
    name: str
    is_union: bool
    fields: list["Field"]


@dataclass
class Field:
    name: str
    type: Union[Struct, Primitive]
    length: int


@dataclass
class Message:
    name: str
    fields: list[Field]
