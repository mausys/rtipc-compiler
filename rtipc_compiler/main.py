from argparse import ArgumentParser, FileType
from parser import RtIpcParser
from c.gen import CGenerator
from pathlib import Path


def main():
    langs = ["c", "rust", "cpp"]
    argparser = ArgumentParser(
        prog="rtipcc",
        description="Compile Schema and generate code",
    )
    arggroup = argparser.add_mutually_exclusive_group(required=False)
    arggroup.add_argument(
        "-s", "--server", action="store_true", help="generate server code"
    )
    arggroup.add_argument(
        "-c", "--client", action="store_true", help="generate client code"
    )
    argparser.add_argument(
        "-l", "--lang", choices=langs, required=True, help="output programming language"
    )
    argparser.add_argument("schema", type=FileType("r"), help="RTIPC schema file")
    argparser.add_argument("-o", "--output", type=Path, required=True)
    ns = argparser.parse_args()
    parser = RtIpcParser()
    structs = parser.parse(ns.schema)

    gen = CGenerator(structs)
    gen.write(ns.output)


if __name__ == "__main__":
    main()
