

import sys
import ply.lex as lex
import ply.yacc as yacc
from decaf_ast import AST  # Import the AST class
def just_scan():
    fn = sys.argv[1] if len(sys.argv) > 1 else ""
    if fn == "":
        print("Missing file name for source program.")
        print("USAGE: python3 decaf_checker.py <decaf_source_file_name>")
        sys.exit()
    import Decaf_lexer
    lexer = lex.lex(module = Decaf_lexer)

    fh = open(fn, 'r')
    source = fh.read()
    lexer.input(source)
    next_token = lexer.token()
    while next_token != None:
        #print(next_token)
        next_token = lexer.token()
# end def just_scan()


def main():
    fn = sys.argv[1] if len(sys.argv) > 1 else ""
    if fn == "":
        print("Missing file name for source program.")
        print("USAGE: python3 decaf_checker.py <decaf_source_file_name>")
        sys.exit()
    import Decaf_lexer
    import Decaf_parser
    lexer = lex.lex(module = Decaf_lexer)
    parser = yacc.yacc(module = Decaf_parser)

    prepend_text = '''
    class In {
        public static int scan_int() {
        }

        public static float scan_float() {
        }
    }

    class Out {
        public static void print(int i) {
        }

        public static void print(float f) {
        }

        public static void print(boolean b) {
        }

        public static void print(string s) {           
        }
    }
    '''

    fh = open(fn, 'r')
    source = fh.read()
    fh.close()

        # Prepend the text
    source = prepend_text + source

    result = parser.parse(source, lexer = lexer)
    #print(result)
    # Parsing Successful
    #print()
    # Use the AST class
    print("Successful Parse/Lex")
    ast = AST()
    ast.build(result)
    ast.print_tree(ast.tree)

    #print(result)
    # Parsing Successful
    #print()
   
    #print()

if __name__ == "__main__":
    just_scan()
    main()