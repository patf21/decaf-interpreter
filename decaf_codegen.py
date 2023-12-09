def generate_commented_label(label, comment):
    output = f"\n# {comment}\n{label}:\n"
    return output  

def generate_label(label):
    output = f"\n{label}:\n"
    return output

def generate_method(method, method_id):
    """
    :param ast_method: the function AST node
    :param data: the data dictionary (all data accessible by the function)
    :return: the assembly code for the function
    """
    output = f"\n# method {method_id}\n"
    method_name = method
    output += generate_label(f"M_{method_name}_{method_id}")
    return output  

def generate_field():
    pass

def generate_get_field_value(register, registers):
    """ 
    :param register: the register to get the field value from
    :return: the assembly code for getting the field value
    """
    new_reg = registers.pop(0)
    output = f"hload {new_reg}, sap, {register}\n"
    return output, new_reg

def generate_method_call(method_label):
    """
    :param ast_method_call: the method call AST node
    :param data: the data dictionary (all data accessible by the method call)
    :return: the assembly code for the method call
    """
    output = f"call {method_label}\n"
    return output

def generate_literal(value, registers: list(), is_float=False):
    """
    :param value: the literal value
    :param registers: the available registers for the literal
    :return: the assembly code for the literal
    """
    reg = registers.pop(0)
    output = ""
    if is_float:
        output = f"move_immed_f {reg}, {value}\n"
    else: 
        output = f"move_immed_i {reg}, {value}\n"
    return output, reg

def generate_binary_expression(value1, value2, reg1, reg2, operation, registers: list()):
    """
    Generate assembly code for a binary expression.

    :param left_operand: The left operand value or register.
    :param right_operand: The right operand value or register.
    :param operation: The operation type (e.g., 'iadd' for integer addition).
    :param registers: List of available registers.
    :return: Assembly code and result register.
    """
    result_reg = registers.pop(0)
    result = 0
    output = f"{operation} {result_reg}, {reg1}, {reg2}\n"
    if operation == "iadd" or operation == "fadd":
        result = value1 + value2
    elif operation == "isub" or operation == "fsub":
        result = value1 - value2
    elif operation == "imul" or operation == "fmul":
        result = value1 * value2
    elif operation == "idiv" or operation == "fdiv":
        result = value1 / value2
    elif operation == "imod" or operation == "fmod":
        result = value1 % value2
    elif operation == "igt" or operation == "fgt": # >
        if value1 > value2:
            result = 1
        else:
            result = 0
    elif operation == "igeq" or operation == "fgeq": # >=
        if value1 >= value2:
            result = 1
        else:
            result = 0
    elif operation == "ilt" or operation == "flt": # <
        if value1 < value2:
            result = 1
        else:
            result = 0
    elif operation == "ileq" or operation == "fleq": # <=
        if value1 <= value2:
            result = 1
        else:
            result = 0
    return output, result_reg, result

def generate_binary_expression_type(expr_type, is_float=False):
    """
    Determine the assembly instruction for a binary expression type.

    :param expr_type: The type of expression (e.g., '+', '-', '*', '/').
    :return: Corresponding assembly operation (e.g., 'iadd', 'isub').
    """
    int_operator_to_string = {
        "+": "iadd",
        "-": "isub",
        "Mult": "imul",
        "Divide": "idiv",
        "%": "imod",
        "&&": "and",
        "||": "or",
        "==": "eq",
        "!=": "neq",
        "<": "ilt",
        ">": "igt",
        "<=": "ileq",
        ">=": "igeq", 
    }

    float_operator_to_string = {
        "+": "fadd",
        "-": "fsub",
        "Mult": "fmul",
        "Divide": "fdiv",
        "%": "fmod",
        "&&": "and",
        "||": "or",
        "==": "eq",
        "!=": "neq",
        "<": "flt",
        ">": "fgt",
        "<=": "fleq",
        ">=": "fgeq"
    }

    if is_float:
        return float_operator_to_string.get(expr_type)
    else:
        return int_operator_to_string.get(expr_type)

def generate_conversions(dest_reg, input_reg, value, value_type):
    if value_type == "int":
        return generate_itof(dest_reg, input_reg, value)
    else:
        return generate_ftoi(dest_reg, input_reg, value)

def generate_ftoi(dest_reg, float_reg, float_value):
    """
    Convert float to int.

    :param dest_reg: The destination register for the integer.
    :param float_reg: The register containing the floating point value.
    :return: Assembly code for float to int conversion.
    """
    output_code = f"ftoi {dest_reg}, {float_reg}\n"
    result_value = int(float_value)
    return output_code, result_value

def generate_itof(dest_reg, int_reg, int_value):
    """
    Convert int to float.

    :param dest_reg: The destination register for the floating point.
    :param int_reg: The register containing the integer value.
    :return: Assembly code for int to float conversion.
    """
    output_code = f"itof {dest_reg}, {int_reg}\n"
    result_value = float(int_value)
    return output_code, result_value

# def generate_auto

# def generate_if_header

# def generate_else_header

# def generate_while_header

def generate_while_condition(register, count):
    """ 
    Generate the condition for a while loop.

    :param register: the register containing the condition value
    :param count: the count
    :return: the assembly code representing the while loop condition
    """
    output = ""
    output += f"bz {register}, endwhile_{count}\n"
    return output

def generate_while_footer(count):
    """ 
    :param ast_while: the while AST node
    :param count: the
    """
    output = ""
    output += f"jmp while_{count}\n"
    output += f"endwhile_{count}:\n"
    return output

def generate_for_header(ast_for, count):
    """
    :param ast_for_header: the for header AST node
    :param count: the count
    :return: the assembly code for the for header

    this should be called after initializing the for loop and before the condition
    """
    pass

def generate_for_condition(ast_for, count, register1):
    """
    :param ast_for_header: the for header AST node
    :param count: the count
    :param register1: the register to evaluate the condition in
    :param register2: the register with a changing value
    :return: the assembly code for the for header

    this should be called after initializing the for loop and before the condition
    """
    return f"bz {register1}, endfor_{count}\n"

def generate_for_footer(count):
    return generate_label(f"endfor_{count}")

def generate_if_footer(count):
    return generate_label(f"endif_{count}")

def generate_move(reg1, reg2):
    """ 
    :param: reg1: the register to
    :param: reg2: the register to
    :return: the assembly code for the move statement
    """
    output = ""
    output += f"move {reg1}, {reg2}\n"
    return output

def generate_jump(label):
    """ 
    :param: label: the label to jump
    :return: the assembly code for the jump statement
    """
    output = ""
    output += f"jmp {label}\n"
    return output

def generate_return(register):
    """ 
    :param: register: the register to return
    :return: the assembly code for the return statement
    """
    output = f"\n# return expression\n"
    output += f"move a0, {register}\n"
    output += "ret\n"
    return output

def generate_negative(register, registers):
    """
    :param register: the register to negate
    :return: the assembly code for the negation
    """
    output = ""
    temp = registers.pop(0)
    output += f"move_immediate_i {temp}, -1\n"
    output += f"imul {register}, {register}, {temp}\n"
    output += f"# free {temp}\n"
    return output

def generate_hstore(register, field_register):
    """ 
    :param register: the register with the value
    :param field_register: the register with the field address
    :return: the assembly code for the hstore statement
    """
    output = ""
    output += f"hstore sap, {field_register}, {register}\n"
    return output

def generate_hload(register, registers):
    """ 
    :param register: the register to get the field value from
    :return: the assembly code for getting the field value
    """
    new_reg = registers.pop(0)
    output = f"hload {new_reg}, sap, {register}\n"
    return output, new_reg

def generate_if_header(ast_if, register, count):
    pass
def generate_else_header(ast_if, count):
    pass
def generate_initializer(): # -- for creating new object with constructor# id
    pass

