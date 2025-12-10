from message import *

STRUCT_END = 0x80

FIELD_TYPE_MASK = 0x03
class FieldType(IntEnum):
    PRIMITIVE = 0x00
    STRUCT = 0x01
    UNION = 0x02

FIELD_LENGTH_MASK = 0x0C
class ArrayLengthSize(IntEnum):
    NONE = 0x00
    ONE = 0x04
    TWO = 0x08
    FOUR = 0x0C


UINT8_MAX = 0xff
UINT16_MAX = 0xffff
UINT32_MAX = 0xffffffff

def enc_length(length: int) -> (int, bytes):
    if length <= 1:
        return (ArrayLengthSize.NONE, b'')
    length = length - 1
    if length <= UINT8_MAX:
        return (ArrayLengthSize.ONE, length.to_bytes(1, 'little'))
    if length <= UINT16_MAX:
        return (ArrayLengthSize.TWO, length.to_bytes(2, 'little'))
    if length <= UINT32_MAX:
        return (ArrayLengthSize.FOUR, length.to_bytes(4, 'little'))

def enc_name(name: str) -> bytes:
      return len(name).to_bytes(1, 'little') + name.encode('utf-8')



def enc_field(field: Field, close_struct: bool) -> bytes:
    name = enc_name(field.name)
    (type, length) = enc_length(field.length)

    if close_struct:
        type |= STRUCT_END

    if isinstance(field.type, Primitive):
        type |= FieldType.PRIMITIVE
        tail = field.type.to_bytes(1, 'little')
    else:
        if field.type.is_union:
            type |= FieldType.UNION
        else:
            type |= FieldType.STRUCT
        tail = enc_struct(field.type)
    return name + type.to_bytes(1, 'little') + length + tail

def enc_struct(struct: Struct) -> bytes:
    info = b''
    close_struct = False
    for field in struct.fields:
          info += enc_field(field, close_struct)
          if isinstance(field.type, Struct):
              close_struct = True
          else:
              close_struct = False
    return info

def create_info(message: Message) -> bytes:
      info = bytes()
      for field in message.fields:
            info += enc_field(field, False)
      return info


def indent(n: int) -> str:
    return ("\t" * n)


def dec_primitive(primitive: int) -> str:
    return str(Primitive(primitive).name)


def dec_array_length(type: int, info: bytes) ->  (int ,bytes):
    match (type & FIELD_LENGTH_MASK):
        case ArrayLengthSize.NONE:
            return (1, info)
        case ArrayLengthSize.ONE:
            length = info[0]
            return (info[0], info[1:])
        case ArrayLengthSize.TWO:
            length = int.from_bytes(info[0:2], byteorder='little')
            return (length, info[2:])
        case ArrayLengthSize.FOUR:
            length = int.from_bytes(info[0:4], byteorder='little')
            return (length, info[4:])

def dump_field(info: bytes, n_indent: int) -> (bytes, int):
    name_length = info[0]
    info = info[1:]
    name = info[:name_length].decode("utf-8")
    info = info[name_length:]
    type = info[0]
    info = info[1:]
    (array_length, info) = dec_array_length(type, info)

    if array_length == 1:
        array = ""
    else:
        array = " [" + str(array_length) + "]"

    if type & STRUCT_END:
        n_indent = n_indent - 1
        print(indent(n_indent) + "}")

    out = indent(n_indent) + str(name) + array

    match (type & FIELD_TYPE_MASK):
        case FieldType.PRIMITIVE:
            out += " " + dec_primitive(info[0])
            info = info[1:]
        case FieldType.STRUCT:
            out += " struct {"
            n_indent = n_indent + 1
        case FieldType.UNION:
            out += " union {"
            n_indent = n_indent + 1

    print(out)
    return (info, n_indent)


def dump_info(info: bytes):

    n_indent = 0
    while len(info) > 0:
        (info, n_indent) = dump_field(info, n_indent)

