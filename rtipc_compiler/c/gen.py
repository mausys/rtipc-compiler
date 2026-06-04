from dataclasses import dataclass
from pathlib import Path
from protocol import Struct, Field, Primitive
from utils import Indent, convert_name, IndentStyle, NameStyle

file_begin = """#pragma once

$include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif
"""

file_end = """
#ifdef __cplusplus
}
#endif
"""


def primitiveName(primitive: Primitive) -> str:
    match primitive:
        case Primitive.BOOL:
            return "bool"
        case Primitive.I8:
            return "int8_t"
        case Primitive.U8:
            return "uint8_t"
        case Primitive.I16:
            return "int16_t"
        case Primitive.U16:
            return "uint16_t"
        case Primitive.I32:
            return "int32_t"
        case Primitive.U32:
            return "uint32_t"
        case Primitive.F32:
            return "float"
        case Primitive.I64:
            return "int64_t"
        case Primitive.U64:
            return "uint64_t"
        case Primitive.F64:
            return "double"
        case Primitive.I128:
            raise RuntimeError("I128 not supported")
        case Primitive.U128:
            raise RuntimeError("U128 not supported")
        case Primitive.F128:
            raise RuntimeError("F128 not supported")
        case _:
            raise RuntimeError("unknown primitive type")


@dataclass
class COption:
    filename: str
    outPath: str


class CGenerator(object):
    def __init__(self, structs: list[Struct]):
        self.structs = structs
        self.content = ""
        self.indent = Indent(IndentStyle.SPACES, 4)
        self.prefix = ""
        self.variableStyle = NameStyle.SNAKECASE
        self.structStyle = NameStyle.SNAKECASE
        self.generate()

    def variableName(self, name: str) -> str:
        return convert_name(name, self.variableStyle)

    def structName(self, name: str) -> str:
        return self.prefix + convert_name(name, self.structStyle)

    def addLine(self, line: str):
        self.content = self.content + "\n" + str(self.indent) + line

    def generate(self):
        self.content = file_begin
        for struct in self.structs:
            self.addStruct(struct)
            self.addLine("")
            self.addLine("")
        self.content = self.content + file_end
        print(self.content)

    def addField(self, field: Field):
        line = ""
        if isinstance(field.type, Primitive):
            line = line + primitiveName(field.type)
        elif isinstance(field.type, Struct):
            if field.type.is_union:
                line = line + "union " + self.structName(field.type.name)
            else:
                line = line + "struct " + self.structName(field.type.name)
        else:
            raise RuntimeError("unsupported field type: " + str(field))

        line = line + " " + self.variableName(field.name)
        if field.length > 1:
            line = line + "[" + str(field.length) + "]"
        line = line + ";"
        self.addLine(line)

    def beginStruct(self, struct: Struct):
        line = ""
        if struct.is_union:
            line = line + "union"
        else:
            line = line + "struct"
        line = line + " " + self.structName(struct.name) + " {"
        self.addLine(line)
        self.indent.increase()

    def endStruct(self):
        self.indent.decrease()
        self.addLine("};")

    def addStruct(self, struct: Struct):
        self.beginStruct(struct)
        for field in struct.fields:
            self.addField(field)
        self.endStruct()

    def write(path: Path, name: str):
        pass
