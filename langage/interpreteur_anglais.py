import re
import string
import math
import random
import importlib

variables = {}
functions = {}
modules = {}

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class BreakLoop(Exception):
    pass

class ContinueLoop(Exception):
    pass

# ---------------------------
# Utility functions
# ---------------------------
def to_number(value):
    """Convert string to number (int or float)"""
    try:
        if '.' in str(value) or ',' in str(value):
            # Handle decimal notation
            value = str(value).replace(',', '.')
            return float(value)
        return int(value)
    except:
        return value

def to_boolean(value):
    """Convert various representations to boolean"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', 'yes', '1']
    return bool(value)

def get_indentation_level(line):
    """Get the indentation level of a line"""
    return len(line) - len(line.lstrip())

# ---------------------------
# Evaluate expressions
# ---------------------------
def eval_expr(expr, local_vars=None):
    if not expr or not expr.strip():
        return None
        
    scope = {}
    scope.update(variables)  # First add global variables
    if local_vars:
        scope.update(local_vars)  # Then add local variables (higher priority)
    
    # Add built-in functions and modules
    scope.update(modules)
    
    # Add user-defined functions to scope
    for func_name in functions:
        scope[func_name] = lambda *args, fn=func_name: call_function(fn, list(args))
    
    expr = expr.strip()
    
    # Handle string literals
    if expr.startswith('"') and expr.endswith('"'):
        return expr[1:-1]
    if expr.startswith("'") and expr.endswith("'"):
        return expr[1:-1]
    
    # Handle boolean literals in English
    if expr.lower() == 'true':
        return True
    if expr.lower() == 'false':
        return False
    
    # Replace English math words with Python operators
    replacements = {
        ' plus ': ' + ',
        ' minus ': ' - ',
        ' times ': ' * ',
        ' multiplied by ': ' * ',
        ' divided by ': ' / ',
        ' integer division by ': ' // ',
        ' modulo ': ' % ',
        ' mod ': ' % ',
        ' raised to ': ' ** ',
        ' to the power of ': ' ** ',
        ' power ': ' ** ',
        ' is greater than or equal to ': ' >= ',
        ' is less than or equal to ': ' <= ',
        ' is greater than ': ' > ',
        ' is less than ': ' < ',
        ' is equal to ': ' == ',
        ' equals ': ' == ',
        ' equal ': ' == ',
        ' is not equal to ': ' != ',
        ' and ': ' and ',
        ' or ': ' or ',
        ' not ': ' not '
    }
    
    # Apply replacements
    original_expr = expr
    for english, py in replacements.items():
        expr = expr.replace(english, py)
    
    if expr != original_expr:
        pass
    
    # Function call detection - handle explicit function calls first
    match = re.match(r'(\w+)\((.*)\)', expr)
    if match:
        func_name, args_str = match.groups()
        args = []
        if args_str.strip():
            # Split arguments more carefully
            args_list = []
            paren_count = 0
            current_arg = ""
            for char in args_str:
                if char == ',' and paren_count == 0:
                    args_list.append(current_arg.strip())
                    current_arg = ""
                else:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                    current_arg += char
            if current_arg.strip():
                args_list.append(current_arg.strip())
            
            args = [eval_expr(a, local_vars) for a in args_list]
        pass
        return call_function(func_name, args)
    
    # Handle module function calls like math.sqrt(16)
    if '.' in expr and '(' in expr:
        try:
            result = eval(expr, {"__builtins__": {}}, scope)
            pass
            return result
        except:
            pass
    
    # Try to evaluate as Python expression
    try:
        result = eval(expr, {"__builtins__": {}}, scope)
        return result
    except Exception as e:
        # If it's just a variable name
        if expr in scope:
            return scope[expr]
        # Return as string if nothing else works (this should rarely happen)
        return expr

# ---------------------------
# Call function
# ---------------------------
def call_function(name, args, caller_local_vars=None):
    """Call a user-defined function with proper scope isolation"""
    if name not in functions:
        return None
    
    params, body = functions[name]
    
    # Create new local scope for this function call
    func_local_vars = {}
    
    # Bind parameters to arguments
    for i, param in enumerate(params):
        if i < len(args):
            func_local_vars[param] = args[i]
        else:
            func_local_vars[param] = None
    
    # Execute function body
    try:
        execute_blocks(body, func_local_vars)
    except ReturnValue as rv:
        return rv.value
    
    return None

# ---------------------------
# Parse and group lines into logical blocks with proper indentation handling
# ---------------------------
def parse_logical_blocks(lines):
    """Parse lines into logical blocks with proper indentation handling"""
    blocks = []
    i = 0
    
    pass
    
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        if not stripped_line or stripped_line.startswith('#'):
            i += 1
            continue
        
        pass
        
        # Function definition - capture everything at higher indentation
        if any(phrase in stripped_line.lower() for phrase in ["create a function", "define a function", "i have a function"]):
            func_block, next_i = parse_function_block_with_indentation(lines, i)
            blocks.append(func_block)
            i = next_i
            pass
        
        # If-else statement
        elif stripped_line.lower().startswith("if "):
            if_block, next_i = parse_if_block_with_indentation(lines, i)
            blocks.append(if_block)
            i = next_i
            pass
        
        # While loop
        elif stripped_line.lower().startswith("while "):
            loop_block, next_i = parse_loop_block_with_indentation(lines, i)
            blocks.append(loop_block)
            i = next_i
            pass
        
        # For loop
        elif stripped_line.lower().startswith("for "):
            loop_block, next_i = parse_for_block_with_indentation(lines, i)
            blocks.append(loop_block)
            i = next_i
            pass
        
        # Do while loop
        elif stripped_line.lower().startswith("do:"):
            loop_block, next_i = parse_do_while_block_with_indentation(lines, i)
            blocks.append(loop_block)
            i = next_i
            pass
        
        # Single statement
        else:
            blocks.append({'type': 'statement', 'line': stripped_line})
            pass
            i += 1
    
    pass
    return blocks

def parse_function_block_with_indentation(lines, start_i):
    """Parse a function definition block with proper indentation handling"""
    line = lines[start_i].strip()
    base_indent = get_indentation_level(lines[start_i])
    
    # Extract function name and parameters
    match = re.search(r"(?:create|define|i have) a function (?:named|called) (\w+)", line.lower())
    if not match:
        return {'type': 'statement', 'line': line}, start_i + 1
    
    func_name = match.group(1)
    
    # Extract parameters - IMPROVED
    params = []
    if "that takes" in line.lower():
        # Extract everything after "that takes"
        prend_pos = line.lower().find("that takes") + len("that takes")
        param_part = line[prend_pos:].strip()
        
        # Handle numbered parameters (two parameters, three parameters, etc.)
        numbered_pattern = re.search(r'(two|three|four|five|six|seven|eight|nine|ten)\s+(?:parameter|number)(?:s)?', param_part.lower())
        if numbered_pattern:
            number_word = numbered_pattern.group(1)
            number_map = {
                'two': 2, 'three': 3, 'four': 4, 'five': 5,
                'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
            }
            param_count = number_map.get(number_word, 2)
            # Generate generic parameter names
            params = [f'param{i+1}' for i in range(param_count)]
        else:
            # Clean up common English phrases
            # Only remove articles if they're followed by more text
            param_part = re.sub(r'(?:a |an |the |some |two |three |four |five )(?=\w)', '', param_part)
            
            # Special case: if the parameter is just "number" or "parameter", keep it
            clean_param = param_part.lower().rstrip('.').strip()
            if clean_param in ['number', 'parameter', 'numbers', 'parameters']:
                pass  # Keep the original name
            else:
                # Remove technical words only if there's other content
                original_param = param_part
                param_part = re.sub(r'(?:number|parameter)(?:s)?\s*', '', param_part)
                # If we removed everything or only punctuation, restore original
                if not param_part.strip() or param_part.strip() in ['.', ',', ';']:
                    param_part = original_param
            param_part = param_part.rstrip('.')
            
            if param_part:
                # Split on various separators
                if " and " in param_part:
                    params = [p.strip() for p in param_part.split(" and ") if p.strip()]
                elif ", " in param_part:
                    params = [p.strip() for p in param_part.split(", ") if p.strip()]
                elif param_part:
                    params = [param_part.strip()]
    elif "with parameters" in line.lower():
        param_match = re.search(r"with parameters (.+)", line.lower())
        if param_match:
            param_str = param_match.group(1)
            params = [p.strip() for p in param_str.split(",")]
    
    # Default parameter if none found
    if not params:
        params = ['n']
    
    # Capture all lines that are indented relative to the function definition
    body_lines = []
    i = start_i + 1
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        # Skip empty lines
        if not current_stripped:
            i += 1
            continue
        
        # If we encounter a line at the same or lower indentation level as the function definition,
        # and it's not empty, then we've reached the end of the function
        if current_indent <= base_indent:
            # This line belongs to the next block
            break
        
        # This line is part of the function body
        body_lines.append(current_line)  # Keep original line with indentation
        i += 1
    
    # Parse the body lines as logical blocks
    body_blocks = parse_logical_blocks(body_lines)
    
    return {
        'type': 'function',
        'name': func_name,
        'params': params,
        'body': body_blocks
    }, i

def parse_if_block_with_indentation(lines, start_i):
    """Parse an if-else block with proper indentation handling"""
    if_line = lines[start_i].strip()
    base_indent = get_indentation_level(lines[start_i])
    
    # Extract condition
    condition = if_line[3:].rstrip(':').strip()  # Remove "if " and potential ":"
    
    # Parse if body
    if_body = []
    else_body = []
    i = start_i + 1
    current_section = 'if'
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        # Skip empty lines
        if not current_stripped:
            i += 1
            continue
        
        # If we encounter a line at the same or lower indentation level, end of block
        if current_indent <= base_indent:
            # Check if it's "otherwise:"
            if current_stripped.lower().startswith("otherwise"):
                current_section = 'else'
                i += 1
                continue
            else:
                # End of if-else block
                break
        
        # Add to appropriate body
        if current_section == 'if':
            if_body.append(current_stripped)
        else:
            else_body.append(current_stripped)
        
        i += 1
    
    return {
        'type': 'if',
        'condition': condition,
        'if_body': if_body,
        'else_body': else_body
    }, i

def parse_loop_block_with_indentation(lines, start_i):
    """Parse a loop block with proper indentation handling"""
    loop_line = lines[start_i].strip()
    base_indent = get_indentation_level(lines[start_i])
    
    # Parse loop body
    body = []
    i = start_i + 1
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        # Skip empty lines
        if not current_stripped:
            i += 1
            continue
        
        # If we encounter a line at the same or lower indentation level, end of loop
        if current_indent <= base_indent:
            break
        
        # This line is part of the loop body
        body.append(current_stripped)
        i += 1
    
    return {
        'type': 'loop',
        'loop_line': loop_line,
        'body': body
    }, i

def parse_for_block_with_indentation(lines, start_i):
    """Parse a for loop block with proper indentation handling"""
    loop_line = lines[start_i].strip()
    base_indent = get_indentation_level(lines[start_i])
    
    # Parse loop body
    body = []
    i = start_i + 1
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        # Skip empty lines
        if not current_stripped:
            i += 1
            continue
        
        # If we encounter a line at the same or lower indentation level, end of loop
        if current_indent <= base_indent:
            break
        
        # This line is part of the loop body
        body.append(current_stripped)
        i += 1
    
    return {
        'type': 'for_loop',
        'loop_line': loop_line,
        'body': body
    }, i

def parse_do_while_block_with_indentation(lines, start_i):
    """Parse a do-while loop block with proper indentation handling"""
    base_indent = get_indentation_level(lines[start_i])
    
    # Parse do body first
    body = []
    i = start_i + 1
    while_condition = None
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        # Skip empty lines
        if not current_stripped:
            i += 1
            continue
        
        # Check for "while" at the end
        if current_stripped.lower().startswith("while ") and current_indent <= base_indent:
            while_condition = current_stripped[6:].rstrip(':').strip()
            i += 1
            break
        
        # If we encounter a line at the same or lower indentation level, might be end
        if current_indent <= base_indent:
            break
        
        # This line is part of the loop body
        body.append(current_stripped)
        i += 1
    
    return {
        'type': 'do_while_loop',
        'condition': while_condition,
        'body': body
    }, i

def parse_if_block(lines, start_i):
    """Parse an if-else block"""
    if_line = lines[start_i].strip()
    condition = if_line[3:].rstrip(':').strip()  # Remove "if " and potential ":"
    
    # Parse if body
    if_body = []
    else_body = []
    i = start_i + 1
    in_else = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Check for "otherwise"
        if line.lower().startswith("otherwise"):
            in_else = True
            i += 1
            continue
        
        # Stop if we encounter another major block
        if (any(phrase in line.lower() for phrase in ["create a function", "define a function"]) or
            line.lower().startswith("if ") or
            line.lower().startswith("repeat ") or
            line.lower().startswith("while ") or
            line.lower().startswith("for ")):
            break
        
        if in_else:
            else_body.append(line)
        else:
            if_body.append(line)
        
        i += 1
    
    return {
        'type': 'if',
        'condition': condition,
        'if_body': if_body,
        'else_body': else_body
    }, i

def parse_loop_block(lines, start_i):
    """Parse a loop block"""
    loop_line = lines[start_i].strip()
    
    # Parse loop body
    body = []
    i = start_i + 1
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Stop if we encounter another major block
        if (any(phrase in line.lower() for phrase in ["create a function", "define a function"]) or
            line.lower().startswith("if ") or
            line.lower().startswith("repeat ") or
            line.lower().startswith("while ") or
            line.lower().startswith("for ")):
            break
        
        body.append(line)
        i += 1
    
    return {
        'type': 'loop',
        'loop_line': loop_line,
        'body': body
    }, i

# ---------------------------
# Execute parsed blocks
# ---------------------------
def execute_blocks(blocks, local_vars=None):
    """Execute a list of parsed blocks"""
    if local_vars is None:
        local_vars = {}
    
    pass
    
    for i, block in enumerate(blocks):
        pass
        try:
            if block['type'] == 'statement':
                pass
                execute_statement(block['line'], local_vars)
            elif block['type'] == 'function':
                pass
                functions[block['name']] = (block['params'], block['body'])
            elif block['type'] == 'if':
                pass
                execute_if_block(block, local_vars)
            elif block['type'] == 'loop':
                pass
                execute_loop_block(block, local_vars)
            elif block['type'] == 'for_loop':
                pass
                execute_for_loop_block(block, local_vars)
            elif block['type'] == 'do_while_loop':
                pass
                execute_do_while_loop_block(block, local_vars)
        except (BreakLoop, ContinueLoop, ReturnValue):
            raise
        except Exception as e:
            print(f"Error in block {i}: {e}")
            import traceback
            traceback.print_exc()

def execute_statement(line, local_vars):
    """Execute a single statement"""
    line = line.strip()
    
    # Variable declarations in English
    if any(phrase in line.lower() for phrase in ["i have a", "i have an", "create a", "create an"]):
        handle_variable_declaration(line)
    
    # Set/Assign variable in English
    elif any(phrase in line.lower() for phrase in ["set ", "assign ", "put "]):
        handle_assignment(line, local_vars)
    
    # Ask user for input in English
    elif "ask the user" in line.lower():
        handle_user_input(line, local_vars)
    
    # Import modules in English
    elif "import " in line.lower():
        handle_import(line)
    
    # Return statement in English
    elif any(phrase in line.lower() for phrase in ["i will return", "return"]):
        handle_return(line, local_vars)
    
    # Break and continue in English
    elif line.lower().strip() == "break":
        raise BreakLoop()
    elif line.lower().strip() == "continue":
        raise ContinueLoop()
    
    # List operations in English
    elif "add " in line.lower() and " to " in line.lower():
        handle_list_add(line, local_vars)
    
    elif "remove " in line.lower() and " from " in line.lower():
        handle_list_remove(line, local_vars)
    
    # Display/Print operations in English
    elif any(word in line.lower() for word in ["show ", "display ", "print "]):
        handle_display(line, local_vars)
    
    # Increase/Decrease operations in English
    elif "increase " in line.lower() or "decrease " in line.lower():
        handle_increment_decrement(line, local_vars)
    
    # Function calls with "Call function with parameter"
    elif line.lower().startswith("call "):
        handle_function_call(line, local_vars)
    
    # Line break control
    elif line.lower().strip() == "line":
        print()  # Force newline
    
    # General assignment (fallback)
    else:
        try:
            eval_expr(line, local_vars)
        except:
            pass

def execute_if_block(block, local_vars):
    """Execute an if block"""
    condition = block['condition']
    
    if eval_expr(condition, local_vars):
        execute_block(block['if_body'], local_vars)
    elif block['else_body']:
        execute_block(block['else_body'], local_vars)

def execute_loop_block(block, local_vars):
    """Execute a loop block"""
    loop_line = block['loop_line']
    
    if "repeat " in loop_line.lower() and "times" in loop_line.lower():
        match = re.search(r"repeat (\d+) times", loop_line.lower())
        if match:
            times = int(match.group(1))
            for _ in range(times):
                try:
                    execute_block(block['body'], local_vars)
                except BreakLoop:
                    break
                except ContinueLoop:
                    continue
                except ReturnValue:
                    raise
    
    elif loop_line.lower().startswith("while "):
        condition = loop_line[6:].rstrip(':').strip()
        while eval_expr(condition, local_vars):
            try:
                execute_block(block['body'], local_vars)
            except BreakLoop:
                break
            except ContinueLoop:
                continue
            except ReturnValue:
                raise
    
    elif loop_line.lower().startswith("for ") and " in " in loop_line.lower():
        match = re.search(r"for (?:each )?(\w+) in (\w+)", loop_line.lower())
        if match:
            var_name, list_name = match.groups()
            
            # Get the list to iterate over
            if list_name in local_vars:
                items = local_vars[list_name]
            elif list_name in variables:
                items = variables[list_name]
            else:
                items = []
            
            for item in items:
                local_vars[var_name] = item
                try:
                    execute_block(block['body'], local_vars)
                except BreakLoop:
                    break
                except ContinueLoop:
                    continue
                except ReturnValue:
                    raise

def execute_for_loop_block(block, local_vars):
    """Execute a for loop block"""
    loop_line = block['loop_line'].lower()
    
    # Handle different for loop patterns
    if " in range " in loop_line:
        # "For j in range 1 to 3:"
        match = re.search(r"for (\w+) in range (\d+) to (\d+)", loop_line)
        if match:
            var_name, start_str, end_str = match.groups()
            start_val = int(start_str)
            end_val = int(end_str)
            
            for i in range(start_val, end_val + 1):
                local_vars[var_name] = i
                try:
                    execute_block(block['body'], local_vars)
                except BreakLoop:
                    break
                except ContinueLoop:
                    continue
                except ReturnValue:
                    raise
    
    elif " times:" in loop_line:
        # "For 5 times:"
        match = re.search(r"for (\d+) times", loop_line)
        if match:
            times = int(match.group(1))
            for i in range(times):
                try:
                    execute_block(block['body'], local_vars)
                except BreakLoop:
                    break
                except ContinueLoop:
                    continue
                except ReturnValue:
                    raise
    
    elif " in " in loop_line:
        # "For each item in list:"
        match = re.search(r"for (?:each )?(\w+) in (\w+)", loop_line)
        if match:
            var_name, list_name = match.groups()
            
            # Get the list to iterate over
            if list_name in local_vars:
                items = local_vars[list_name]
            elif list_name in variables:
                items = variables[list_name]
            else:
                items = []
            
            for item in items:
                local_vars[var_name] = item
                try:
                    execute_block(block['body'], local_vars)
                except BreakLoop:
                    break
                except ContinueLoop:
                    continue
                except ReturnValue:
                    raise

def execute_do_while_loop_block(block, local_vars):
    """Execute a do-while loop block"""
    condition = block['condition']
    
    # Execute the body at least once
    while True:
        try:
            execute_block(block['body'], local_vars)
        except BreakLoop:
            break
        except ContinueLoop:
            pass
        except ReturnValue:
            raise
        
        # Check condition after execution
        if condition and not eval_expr(condition, local_vars):
            break

# ---------------------------
# Execute a block of code with proper indentation-aware parsing
# ---------------------------
def execute_block(lines, local_vars=None):
    if local_vars is None:
        local_vars = {}
    
    # If lines is a list of strings, we need to handle if/otherwise specially
    if isinstance(lines, list) and lines and isinstance(lines[0], str):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # Handle if/otherwise blocks specially
            if line.lower().startswith("if "):
                i = handle_if_condition_direct(lines, i, local_vars)
            else:
                # Execute as single statement
                execute_statement(line, local_vars)
                i += 1
    else:
        # If it's already parsed blocks
        execute_blocks(lines, local_vars)

def handle_if_condition_direct(lines, start_index, local_vars):
    """Handle if conditions directly from line array with proper nesting"""
    line = lines[start_index].strip()
    condition = line[3:].rstrip(':').strip()  # Remove "if " and potential ":"
    
    pass
    
    # Find the if body and else body
    if_body = []
    else_body = []
    i = start_index + 1
    in_else = False
    
    while i < len(lines):
        current_line = lines[i].strip()
        
        if not current_line:
            i += 1
            continue
        
        # Check for "otherwise" - should be at same logical level as the "if"
        if current_line.lower().startswith("otherwise"):
            in_else = True
            pass
            i += 1
            continue
        
        # Stop if we encounter another major construct at same level
        # Functions are at top level, so if inside functions shouldn't break on them
        if (current_line.lower().startswith("if ") or
            current_line.lower().startswith("repeat ") or
            current_line.lower().startswith("while ") or
            current_line.lower().startswith("for ")):
            break
        
        if in_else:
            else_body.append(current_line)
            pass
        else:
            if_body.append(current_line)
            pass
        
        i += 1
    
    pass
    pass
    
    # Evaluate condition and execute appropriate body
    condition_result = eval_expr(condition, local_vars)
    pass
    
    if condition_result:
        for stmt in if_body:
            execute_statement(stmt, local_vars)
    elif else_body:
        for stmt in else_body:
            execute_statement(stmt, local_vars)
    
    return i

# ---------------------------
# Handler functions in English
# ---------------------------
def handle_variable_declaration(line):
    """Handle variable declarations in English like 'I have a number called x'"""
    patterns = [
        r"i have a (\w+) called (\w+)",
        r"i have an (\w+) called (\w+)",
        r"create a (\w+) called (\w+)",
        r"create an (\w+) called (\w+)",
        r"i have a (\w+) named (\w+)",
        r"i have an (\w+) named (\w+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line.lower())
        if match:
            var_type, var_name = match.groups()
            # Initialize with appropriate default value
            if var_type in ['number', 'integer', 'num']:
                variables[var_name] = 0
            elif var_type in ['string', 'text', 'word']:
                variables[var_name] = ""
            elif var_type in ['boolean', 'bool']:
                variables[var_name] = False
            elif var_type in ['list', 'array']:
                variables[var_name] = []
            elif var_type in ['dictionary', 'dict']:
                variables[var_name] = {}
            else:
                variables[var_name] = None
            break

def handle_assignment(line, local_vars):
    """Handle assignments in English like 'Set x to 5' or 'Put 5 in x'"""
    patterns = [
        r"set (\w+) to (.+)",
        r"put (.+) in (\w+)",
        r"assign (.+) to (\w+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line.lower())
        if match:
            if "put" in pattern:
                value_expr, var_name = match.groups()
            else:
                var_name, value_expr = match.groups()
            
            # Clean up value expression (remove trailing period)
            value_expr = value_expr.strip()
            if value_expr.endswith('.'):
                value_expr = value_expr[:-1].strip()
            
            value = eval_expr(value_expr, local_vars)
            
            if var_name in local_vars:
                local_vars[var_name] = value
            else:
                variables[var_name] = value
            break

def handle_user_input(line, local_vars):
    """Handle user input in English like 'Ask the user for a value for n'"""
    match = re.search(r"ask the user.*?(?:for a value for|for) (\w+)", line.lower())
    if match:
        var_name = match.group(1)
        user_input = input(f"Enter a value for {var_name}: ")
        
        # Try to convert to appropriate type
        value = user_input
        try:
            value = to_number(user_input)
        except:
            if user_input.lower() in ['true', 'false']:
                value = to_boolean(user_input)
        
        if var_name in local_vars:
            local_vars[var_name] = value
        else:
            variables[var_name] = value

def handle_import(line):
    """Handle imports in English like 'Import the math module'"""
    match = re.search(r"import (?:the )?(?:module )?(\w+)", line.lower())
    if match:
        module_name = match.group(1)
        try:
            if module_name == 'math':
                modules['math'] = math
            elif module_name == 'random':
                modules['random'] = random
            else:
                modules[module_name] = importlib.import_module(module_name)
        except ImportError:
            print(f"Warning: Unable to import module {module_name}")

def handle_return(line, local_vars):
    """Handle return statements in English"""
    if line.lower().startswith("i will return"):
        expr = line[13:].strip()
    else:
        expr = line[6:].strip()  # "return" = 6 characters
    
    # Remove trailing period if present
    if expr.endswith('.'):
        expr = expr[:-1]
    
    pass
    value = eval_expr(expr, local_vars)
    pass
    raise ReturnValue(value)

def handle_list_add(line, local_vars):
    """Handle adding to lists in English like 'Add 4 to numbers'"""
    match = re.search(r"add (.+) to (\w+)", line.lower())
    if match:
        value_expr, list_name = match.groups()
        value = eval_expr(value_expr, local_vars)
        
        if list_name in local_vars:
            if isinstance(local_vars[list_name], list):
                local_vars[list_name].append(value)
        elif list_name in variables:
            if isinstance(variables[list_name], list):
                variables[list_name].append(value)

def handle_list_remove(line, local_vars):
    """Handle removing from lists in English like 'Remove 2 from numbers'"""
    match = re.search(r"remove (.+) from (\w+)", line.lower())
    if match:
        value_expr, list_name = match.groups()
        value = eval_expr(value_expr, local_vars)
        
        target_list = None
        if list_name in local_vars and isinstance(local_vars[list_name], list):
            target_list = local_vars[list_name]
        elif list_name in variables and isinstance(variables[list_name], list):
            target_list = variables[list_name]
        
        if target_list and value in target_list:
            target_list.remove(value)

def handle_display(line, local_vars):
    """Handle display/print statements in English with user-controlled line breaks"""
    line_lower = line.lower()
    
    # Extract what to display
    expr = ""
    if "show the result of" in line_lower:
        start = line_lower.find("show the result of") + len("show the result of")
        expr = line[start:].strip()
    elif "show " in line_lower:
        start = line_lower.find("show") + len("show")
        expr = line[start:].strip()
    elif "display " in line_lower:
        start = line_lower.find("display") + len("display")
        expr = line[start:].strip()
    else:
        return
    
    # Clean up expression
    if expr.endswith('.'):
        expr = expr[:-1]
    if expr.lower().endswith("on the screen"):
        expr = expr[:-(len("on the screen"))].strip()
    elif expr.lower().endswith("on screen"):
        expr = expr[:-(len("on screen"))].strip()
    
    # Check for line control keywords
    add_newline = False
    if expr.lower().endswith(" line"):
        expr = expr[:-5].strip()  # Remove " line"
        add_newline = True
    elif expr.lower().endswith(" continue"):
        expr = expr[:-9].strip()  # Remove " continue"
        add_newline = False
    else:
        # Default behavior: no newline (user controls it)
        add_newline = False
    
    if expr:
        result = eval_expr(expr, local_vars)
        if add_newline:
            print(result)  # With newline
        else:
            print(result, end='')  # Without newline

def handle_increment_decrement(line, local_vars):
    """Handle increment/decrement in English like 'Increase x by 1'"""
    patterns = [
        (r"increase (\w+) by (.+)", 1),
        (r"decrease (\w+) by (.+)", -1)
    ]
    
    for pattern, sign in patterns:
        match = re.search(pattern, line.lower())
        if match:
            var_name, amount_expr = match.groups()
            amount = eval_expr(amount_expr, local_vars) * sign
            
            current_value = 0
            if var_name in local_vars:
                current_value = local_vars[var_name] or 0
                local_vars[var_name] = current_value + amount
            elif var_name in variables:
                current_value = variables[var_name] or 0
                variables[var_name] = current_value + amount
            break

def handle_function_call(line, local_vars):
    """Handle function calls like 'Call function with parameter'"""
    # Parse "Call function_name with parameter"
    match = re.search(r"call (\w+) with (.+)", line.lower())
    if match:
        func_name, args_expr = match.groups()
        
        # Remove trailing period
        args_expr = args_expr.rstrip('.')
        
        # Split multiple arguments by "and" and evaluate each
        args_list = []
        if " and " in args_expr:
            # Multiple arguments separated by "and"
            arg_parts = [part.strip() for part in args_expr.split(" and ")]
            for arg_part in arg_parts:
                arg_value = eval_expr(arg_part, local_vars)
                args_list.append(arg_value)
        else:
            # Single argument
            arg_value = eval_expr(args_expr, local_vars)
            args_list.append(arg_value)
        
        # Call the function
        if func_name in functions:
            result = call_function(func_name, args_list, local_vars)
            return result
    
    # Parse "Call function_name" (no parameters)
    match = re.search(r"call (\w+)", line.lower())
    if match:
        func_name = match.group(1)
        if func_name in functions:
            result = call_function(func_name, [], local_vars)
            return result

# ---------------------------
# Run a .dav program with proper indentation handling
# ---------------------------
def run_dav(filename):
    """Run a .dav program from a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Keep original lines with indentation for proper parsing
        lines = [line.rstrip() for line in lines]
        # Remove completely empty lines
        lines = [line for line in lines if line.strip()]
        
        pass
        for i, line in enumerate(lines):
            pass
        
        # Parse into logical blocks first
        blocks = parse_logical_blocks(lines)
        execute_blocks(blocks)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except ReturnValue as rv:
        # This should never happen at the top level
        pass
    except Exception as e:
        import traceback
        print(f"Error executing program: {e}")
        print("Traceback:")
        traceback.print_exc()

def run_dav_code(code):
    """Run .dav code from a string"""
    lines = [line.rstrip() for line in code.split('\n')]
    lines = [line for line in lines if line.strip()]
    blocks = parse_logical_blocks(lines)
    execute_blocks(blocks)

# ---------------------------
# Main entry
# ---------------------------
def main():
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        run_dav(filename)
    else:
        # Interactive mode
        print("DAV English Language Interpreter")
        print("Type 'exit' to quit, 'help' for examples")
        
        while True:
            try:
                line = input("dav> ").strip()
                if line.lower() in ['exit', 'quit']:
                    break
                elif line.lower() == 'help':
                    print("""
Examples:
  I have a number called x.
  Set x to 10.
  Show x on screen.
  
  Create a function named double that takes a number.
  I will return number times 2.
  
  Show the result of double(5) on screen.
""")
                elif line:
                    execute_block([line])
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Goodbye!")

if __name__ == "__main__":
    main()
