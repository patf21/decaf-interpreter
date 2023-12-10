import sys
import ply.lex as lex
import ply.yacc as yacc
from decaf_ast import AST  # Import the AST class
from decaf_asbmc import write_asm
def just_scan():
    fn = sys.argv[1] if len(sys.argv) > 1 else ""
    if fn == "":
        print("Missing file name for source program.")
        print("USAGE: python3 decaf_checker.py <decaf_source_file_name>")
        sys.exit()
    import decaf_lexer
    lexer = lex.lex(module = decaf_lexer)

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
    import decaf_lexer
    import decaf_parser
    lexer = lex.lex(module = decaf_lexer)
    parser = yacc.yacc(module = decaf_parser)

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
    print(source)
    result = parser.parse(source, lexer = lexer)
    # print(result)
    # Parsing Successful
    #print()
    # Use the AST class
    print("Successful Parse/Lex")
    ast = AST()
    ast.build(result)
    ast.print_tree(ast.tree)
    write_asm("assembly_printout.txt", ast.asm)
    print("\n\n\n" + ast.asm)
    #print(ast.asm_data)
    # print(ast.tree)
    #print(result)
    # Parsing Successful
    #print()
   
    #print()

if __name__ == "__main__":
    just_scan()
    main()