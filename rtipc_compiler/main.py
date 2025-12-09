from argparse import ArgumentParser, FileType
from parser import RtIpcParser
from info import create_info

def main():
    langs = ['c', 'rust', 'cpp']
    argparser = ArgumentParser(
                        prog='rtipcc',
                        description='Compile Schema and generate code',
                        )
    arggroup = argparser.add_mutually_exclusive_group(required=True)
    arggroup.add_argument('-p', '--producer', action='store_true',  help='generate producer code')
    arggroup.add_argument('-c', '--consumer',  action='store_true', help='generate consumer code')
    argparser.add_argument('-l', '--lang', choices = langs, required = True, help='output programming language')
    argparser.add_argument('schema', type=FileType('r'), help='RTIPC schema file')
    argparser.add_argument('-o', '--output', type=FileType('w'), required = True)
    ns = argparser.parse_args()
    parser = RtIpcParser()
    messages = parser.parse(ns.schema)
    info = create_info(messages[0])

    print(info)

if __name__ == '__main__':
    main()
