import sys
from Decaf_lexer import *

class Node:
    def __init__(self, type, children=None, leaf=None,lineNo = -1):
        self.type = type
        self.children = children if children else []
        self.leaf = leaf
        self.lineNo = lineNo
names = {}
PrependLinesConst = 22
precedence = (('right', 'ASSIGN'),
              ('left', 'OR'),
              ('left', 'AND'),
              ('nonassoc', 'EQ', 'NOT_EQ'),
              ('nonassoc', 'LT', 'LTE', 'GT', 'GTE'),
              ('left', 'PLUS', 'MINUS'),
              ('left', 'STAR', 'F_SLASH'),
              ('right', 'UMINUS', 'UPLUS', 'NOT')
              )

def p_program(p):
    'program : class_decl_list'
    p[0] = Node('program', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)

def p_class_decl_list_1(p):
    'class_decl_list : class_decl class_decl_list'
    p[0] = Node('class_decl_list', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_class_decl_list_2(p):
    'class_decl_list : empty'
    p[0] = Node('class_decl_list', lineNo=p.lineno(1)-PrependLinesConst)

def p_class_decl(p):
    '''class_decl : CLASS ID LEFT_CB class_body_decl_list RIGHT_CB
                  | CLASS ID EXTENDS ID LEFT_CB class_body_decl_list  RIGHT_CB'''
    if len(p) == 6:
        p[0] = Node('class_decl', [Node('ID', leaf =p[2], lineNo=p.lineno(1)-PrependLinesConst), p[4]], lineNo=p.lineno(1)-PrependLinesConst)
        
    else:
        p[0] = Node('class_decl', [Node('ID', leaf =p[2], lineNo=p.lineno(1)-PrependLinesConst), Node('EXTENDS', [Node('ID', leaf =p[4],lineNo=p.lineno(1)-PrependLinesConst)], lineNo=p.lineno(1)-PrependLinesConst), p[6]], lineNo=p.lineno(1)-PrependLinesConst)

def p_class_body_decl_list(p):
    'class_body_decl_list : class_body_decl class_body_decl_cont'
    p[0] = Node('class_body_decl_list', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_class_body_decl_cont(p):
    '''class_body_decl_cont : class_body_decl class_body_decl_cont
                            | empty'''
    if len(p) == 3:
        p[0] = Node('class_body_decl_cont', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('class_body_decl_cont', lineNo=p.lineno(1)-PrependLinesConst)

def p_class_body_decl(p):
    '''class_body_decl : field_decl
                       | method_decl
                       | constructor_decl'''
    p[0] = Node('class_body_decl', p[1], lineNo=p.lineno(1)-PrependLinesConst)

def p_field_decl(p):
    'field_decl : modifier var_decl'
    p[0] = Node('field_decl', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_modifier(p):
    '''modifier : PUBLIC STATIC
                | PRIVATE STATIC
                | PUBLIC
                | PRIVATE
                | STATIC
                | empty'''
    if len(p) == 3:
        if p[1] == "public":
            ##print(, file=sys.__stdout__)
            p[0] = Node('modifier', leaf= "public, static", lineNo=p.lineno(1)-PrependLinesConst)
        else:    
            p[0] = Node('modifier', leaf= "private, static", lineNo=p.lineno(1)-PrependLinesConst)
    elif len(p) == 2:
        if p[1] == 'public':
            p[0] = Node('modifier', leaf= "public, instance", lineNo=p.lineno(1)-PrependLinesConst)
        elif p[1] == 'private':
            p[0] = Node('modifier', leaf= "private, instance", lineNo=p.lineno(1)-PrependLinesConst)
        elif p[1] == 'static':
            p[0] = Node('modifier', leaf = "private, static", lineNo=p.lineno(1)-PrependLinesConst)
        else:
            p[0] = Node('modifier', leaf = "private, instance", lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('modifier', leaf = "", lineNo=p.lineno(1)-PrependLinesConst)

def p_var_decl(p):
    'var_decl : type variables SEMI_COLON'
    p[0] = Node('var_decl', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_type(p):
    '''type : TYPE_INT
            | TYPE_FLOAT
            | TYPE_BOOLEAN
            | TYPE_STRING
            | TYPE_VOID
            | ID'''
    if p[1] != "int" and p[1] != "float" and p[1] != "boolean" and p[1] != "string" and p[1] != "void":
        p[0] = Node('type', leaf = "user("+p[1]+")", lineNo=p.lineno(1)-PrependLinesConst)
    else:   
        p[0] = Node('type', leaf = p[1], lineNo=p.lineno(1)-PrependLinesConst)

def p_variables(p):
    'variables : variable variables_cont'
    p[0] = Node('variables', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_variables_cont(p):
    '''variables_cont : COMMA variable variables_cont
                      | empty'''
    if len(p) == 4:
        p[0] = Node('variables_cont', [p[2], p[3]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('variables_cont', lineNo=p.lineno(1)-PrependLinesConst)

def p_variable(p):
    'variable : ID'
    p[0] = Node('variable', leaf = p[1], lineNo=p.lineno(1)-PrependLinesConst)

def p_method_decl(p):
    '''method_decl : modifier type ID LEFT_PN formals RIGHT_PN block'''
    p[0] = Node('method_decl', [p[1], Node('type', [p[2]], lineNo=p.lineno(1)-PrependLinesConst), Node('ID', leaf =p[3], lineNo=p.lineno(1)-PrependLinesConst), Node('formals',[p[5]], lineNo=p.lineno(1)-PrependLinesConst), Node('block',[p[7]], lineNo=p.lineno(1)-PrependLinesConst)], lineNo=p.lineno(1)-PrependLinesConst)
        
def p_method_dec2(p):
    '''method_decl : modifier TYPE_VOID ID LEFT_PN formals RIGHT_PN block'''
    p[0] = Node('method_decl', [p[1], Node('type',leaf = "void", lineNo=p.lineno(1)-PrependLinesConst), Node('ID', leaf =p[3], lineNo=p.lineno(1)-PrependLinesConst), Node('formals',[p[5]], lineNo=p.lineno(1)-PrependLinesConst), Node('block',[p[7]], lineNo=p.lineno(1)-PrependLinesConst)], lineNo=p.lineno(1)-PrependLinesConst)
def p_constructor_decl(p):
    'constructor_decl : modifier ID LEFT_PN formals RIGHT_PN block'
    p[0] = Node('constructor_decl', [p[1], Node('ID', leaf =p[2], lineNo=p.lineno(1)-PrependLinesConst), Node('formals',[p[4]], lineNo=p.lineno(1)-PrependLinesConst), Node('block',[p[6]], lineNo=p.lineno(1)-PrependLinesConst)], lineNo=p.lineno(1)-PrependLinesConst)

def p_formals(p):
    '''formals : formal_param formals_cont
               | empty'''
    if len(p) == 3:
        p[0] = Node('formals', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('formals', lineNo=p.lineno(1)-PrependLinesConst)

def p_formals_cont(p):
    '''formals_cont : COMMA formal_param formals_cont
                    | empty'''
    if len(p) == 4:
        p[0] = Node('formals_cont', [p[2], p[3]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('formals_cont', lineNo=p.lineno(1)-PrependLinesConst)

def p_formal_param(p):
    'formal_param : type variable'
    p[0] = Node('formal_param', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_block(p):
    'block : LEFT_CB stmt_list RIGHT_CB'
    p[0] = Node('block', [p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_stmt_list(p):
    '''stmt_list : stmt stmt_list
                 | empty'''
    if len(p) == 3:
        p[0] = Node('stmt_list', [p[1], p[2]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('stmt_list', lineNo=p.lineno(1)-PrependLinesConst)
def p_stmt(p):
    '''stmt : IF LEFT_PN expr RIGHT_PN stmt 
            | IF LEFT_PN expr RIGHT_PN stmt ELSE stmt
            | WHILE LEFT_PN expr RIGHT_PN stmt
            | FOR LEFT_PN for_cond1 SEMI_COLON for_cond2 SEMI_COLON for_cond3 RIGHT_PN stmt
            | RETURN return_val SEMI_COLON
            | stmt_expr SEMI_COLON
            | BREAK SEMI_COLON
            | CONTINUE SEMI_COLON
            | block
            | var_decl
            | SEMI_COLON'''
    
    if len(p) == 6:
        if p[1] == 'if':
            p[0] = Node('if', [p[3], p[5]], lineNo=p.lineno(1)-PrependLinesConst)
        elif p[1] == 'while':
            p[0] = Node('while', [p[3], p[5]], lineNo=p.lineno(1)-PrependLinesConst)
    elif len(p) == 4:
        p[0] = Node('return_stmt', [p[2]], lineNo=p.lineno(1)-PrependLinesConst)
    elif len(p) == 3:
        if not isinstance(p[1],Node):
            if p[1] == 'break':
                p[0] = Node('break', lineNo=p.lineno(1)-PrependLinesConst)
            elif p[1] == 'continue':
                p[0] = Node('continue', lineNo=p.lineno(1)-PrependLinesConst)
        if isinstance(p[1], Node):
            if p[1].type == 'stmt_expr':
                p[0] = Node('stmt_expr', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    elif len(p) == 8:
            p[0] = Node('if_else', [p[3], p[5], p[7]], lineNo=p.lineno(1)-PrependLinesConst)
    elif len(p) == 10:  # FOR loop
        p[0] = Node('for_stmt', [p[3], p[5], p[7], p[9]], lineNo=p.lineno(1)-PrependLinesConst)
    elif len(p) == 2:  # stmt_expr or SEMI_COLON
        if isinstance(p[1], Node):
            if p[1].type == 'var_decl':
                p[0] = Node('var_decl', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
            elif p[1].type == 'block':
                p[0] = Node('block', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('empty_stmt', lineNo=p.lineno(1)-PrependLinesConst)
    #print(p[0].type, file=sys.__stdout__)
def p_for_cond1(p):
    '''for_cond1 : stmt_expr
                 | empty'''
    if isinstance(p[1], Node):
        p[0] = Node('for_cond1', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('for_cond1', lineNo=p.lineno(1)-PrependLinesConst)

def p_for_cond2(p):
    '''for_cond2 : expr
                 | empty'''
    if isinstance(p[1], Node):
        p[0] = Node('for_cond2', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('for_cond2', lineNo=p.lineno(1)-PrependLinesConst)

def p_for_cond3(p):
    '''for_cond3 : stmt_expr
                 | empty'''
    if isinstance(p[1], Node):
        p[0] = Node('for_cond3', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('for_cond3', lineNo=p.lineno(1)-PrependLinesConst)

def p_return_val(p):
    '''return_val : expr
                  | empty'''
    if isinstance(p[1], Node):
        p[0] = Node('return_val', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('return_val', lineNo=p.lineno(1)-PrependLinesConst)


def p_literal(p):
    '''literal : INT_CONST
               | FLOAT_CONST
               | STRING_CONST
               | NULL
               | TRUE
               | FALSE'''
    if isinstance(p[1],int):
        p[0] = Node('Integer-constant', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    elif isinstance(p[1],float):
        p[0] = Node('Float-constant', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    elif p[1] == "null":
        p[0] = Node('ConstantNull', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    elif p[1] == "false":
        p[0] = Node('ConstantFalse', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
    elif p[1] == "true":
        p[0] = Node('ConstantTrue', [p[1]], lineNo=p.lineno(1)-PrependLinesConst) 
    elif isinstance(p[1],str):
        #sys.stdout.write(p[1])
        p[0] = Node('String-constant', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)


def p_primary(p):
    '''primary : literal
               | THIS
               | SUPER
               | LEFT_PN expr RIGHT_PN
               | NEW ID LEFT_PN arguments RIGHT_PN
               | lhs
               | method_invocation'''
    if len(p) == 2:
        if not isinstance(p[1], Node):
            if p[1] == "this":
                p[0] = Node('this',leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)
            if p[1] == "super":
                p[0] = Node('super',leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)
        elif (p[1].type) == "method_invocation":
                p[0] = Node('method_invocation', [p[1]],leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)
        else:
            if isinstance(p[1], Node):
                if (p[1].type) == 'lhs':
                    p[0] = Node('lhs', [p[1]],leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)
                else:
                    p[0] = Node('literal', [p[1]],leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)
    elif len(p) == 4:
        if p[1] == '(':
            p[0] = Node('paren_expr', [p[2]],leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)
        else:  # lhs or method_invocation
            p[0] = Node('primary', [p[1]],leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)
    else:  # NEW ID LEFT_PN arguments RIGHT_PN
        p[0] = Node('new_object', [Node('ID', leaf =p[2], lineNo=p.lineno(1)-PrependLinesConst), p[4]],leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)

def p_arguments(p):
    '''arguments : expr arguments_cont
                 | empty'''
    if len(p) == 3:
        p[0] = Node('arguments', children = [p[1], p[2]], leaf = "nodes", lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('arguments',leaf = "EMPTY", lineNo=p.lineno(1)-PrependLinesConst)

def p_arguments_cont(p):
    '''arguments_cont : COMMA expr arguments_cont
                      | empty'''
    if len(p) == 4:
        p[0] = Node('arguments_cont', [p[2], p[3]], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('arguments_cont', lineNo=p.lineno(1)-PrependLinesConst)

def p_lhs(p):
    'lhs : field_access'
    p[0] = Node('lhs', [p[1]],lineNo=p.lineno(1)-PrependLinesConst)

def p_field_access(p):
    '''field_access : primary DOT ID
                    | ID'''
    if len(p) == 4:
        p[0] = Node('primary_field_access', [p[1], Node('ID', leaf =p[3],lineNo=p.lineno(1)-PrependLinesConst)], lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('id_field_access', [Node('ID', leaf =p[1],lineNo=p.lineno(1)-PrependLinesConst)], lineNo=p.lineno(1)-PrependLinesConst)

def p_method_invocation(p):
    'method_invocation : field_access LEFT_PN arguments RIGHT_PN'
    p[0] = Node('method_invocation', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_expr(p):
    '''expr : primary
            | assign'''
    if isinstance(p[1],Node):
        if p[1].leaf == 'primary':
            p[0] = Node('expr', [p[1]],leaf = "primary", lineNo=p.lineno(1)-PrependLinesConst)
        else:
            p[0] = Node('expr', [p[1]],leaf = "assign", lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('expr', [p[1]],leaf = "assign", lineNo=p.lineno(1)-PrependLinesConst)


def p_assign(p):
    '''assign : lhs ASSIGN expr
              | lhs INCREMENT
              | INCREMENT lhs
              | lhs DECREMENT
              | DECREMENT lhs'''
    if len(p) == 4:
        if p[2] == '=':
            p[0] = Node('assign_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)
        
    else:  # Pre-increment or pre-decrement
        if p[1] == '++':
            p[0] = Node('pre_increment_assign_expr', [p[2]], lineNo=p.lineno(1)-PrependLinesConst)
        elif p[2] == '++':
            p[0] = Node('increment_assign_expr', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
        elif p[2] == '--':  # '--'
            p[0] = Node('decrement_assign_expr', [p[1]], lineNo=p.lineno(1)-PrependLinesConst)
        else:  # '--'
            p[0] = Node('pre_decrement_assign_expr', [p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_add_expr(p):
    'expr : expr PLUS expr'
    p[0] = Node('+_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_sub_expr(p):
    'expr : expr MINUS expr'
    p[0] = Node('-_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_mult_exp(p):
    'expr : expr STAR expr'
    p[0] = Node('mult_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_div_expr(p):
    'expr : expr F_SLASH expr'
    p[0] = Node('divide_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_conj_expr(p):
    'expr : expr AND expr'
    p[0] = Node('&&_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_disj_expr(p):
    'expr : expr OR expr'
    p[0] = Node('||_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_equals_expr(p):
    'expr : expr EQ expr'
    p[0] = Node('==_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_notequals_expr(p):
    'expr : expr NOT_EQ expr'
    p[0] = Node('!=_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_lt_expr(p):
    'expr : expr LT expr'
    p[0] = Node('<_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_lte_expr(p):
    'expr : expr LTE expr'
    p[0] = Node('<=_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_gt_expr(p):
    'expr : expr GT expr'
    p[0] = Node('>_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_gte_expr(p):
    'expr : expr GTE expr'
    p[0] = Node('>=_expr', [p[1], p[3]], lineNo=p.lineno(1)-PrependLinesConst)

def p_pos_expr(p):
    'expr : PLUS expr %prec UPLUS'
    p[0] = Node('pos_expr', [p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_minus_expr(p):
    'expr : MINUS expr %prec UMINUS'
    p[0] = Node('minus_expr', [p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_not_expr(p):
    'expr : NOT expr'
    p[0] = Node('not_expr', [p[2]], lineNo=p.lineno(1)-PrependLinesConst)

def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    if p[1].type == 'assign':
        p[0] = Node('stmt_expr', [p[1]],leaf = 'assign', lineNo=p.lineno(1)-PrependLinesConst)
    else:
        p[0] = Node('stmt_expr', [p[1]],leaf = 'method_invocation', lineNo=p.lineno(1)-PrependLinesConst)

def p_empty(p):
    'empty :'
    p[0] = Node('empty')

def p_error(p):
    print()
    if p:
        print("Syntax error at token,", p.type, ", line", (p.lineno-22))
    else:
        print("Syntax error at EOF")
    print()
    sys.exit()
