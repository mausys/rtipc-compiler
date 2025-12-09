from message import *

STRUCT_END = 0x80

FIELD_TYPE_MASK = 0x03
FIELD_TYPE_PRIMITIVE = 0x00
FIELD_TYPE_STRUCT = 0x01
FIELD_TYPE_UNION = 0x02

FIELD_LENGTH_MASK = 0x0C
FIELD_LENGTH_SINGLE = 0x00
FIELD_LENGTH_BYTE = 0x04
FIELD_LENGTH_16 = 0x08
FIELD_LENGTH_32 = 0x0C


UINT8_MAX = 0xff
UINT16_MAX = 0xffff
UINT32_MAX = 0xffffffff

def enc_length(length: int) -> (int, bytes):
    if length <= 1:
        return (FIELD_LENGTH_SINGLE, b'')
    length = length - 1
    if length <= UINT8_MAX:
        return (FIELD_LENGTH_BYTE, length.to_bytes(1, 'little'))
    if length <= UINT16_MAX:
        return (FIELD_LENGTH_16, length.to_bytes(2, 'little'))
    if length <= UINT32_MAX:
        return (FIELD_LENGTH_32, length.to_bytes(4, 'little'))

def enc_name(name: str) -> bytes:
      return len(name).to_bytes(1, 'little') + name.encode('utf-8')



def enc_field(field: Field, close_struct: bool) -> bytes:
    name = enc_name(field.name)
    (type, length) = enc_length(field.length)

    if close_struct:
        type |= STRUCT_END

    if isinstance(field.type, Primitive):
        type |= FIELD_TYPE_PRIMITIVE
        tail = field.type.to_bytes(1, 'little')
    else:
        if field.type.is_union:
            type |= FIELD_TYPE_UNION
        else:
            type |= FIELD_TYPE_STRUCT
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
