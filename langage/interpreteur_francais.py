import re
import string
import math
import random
import importlib
from typing import Any, Dict, List, Union, Optional

class DAVInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.modules = {}
        self.output_buffer = []
        self.should_flush_output = True
        
    def reset(self):
        """Reset the interpreter state"""
        self.variables = {}
        self.functions = {}
        self.modules = {}
        self.output_buffer = []
        self.should_flush_output = True

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class BreakLoop(Exception):
    pass

class ContinueLoop(Exception):
    pass

# Global interpreter instance
dav = DAVInterpreter()

def to_number(value):
    """Convert string to number (int or float)"""
    try:
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            if '.' in value:
                return float(value)
            return int(value)
        return value
    except (ValueError, TypeError):
        return value

def to_boolean(value):
    """Convert various representations to boolean"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['vrai', 'oui', '1', 'true', 'yes']
    return bool(value)

def eval_expr(expr, local_vars=None):
    """Evaluate expressions with proper scope handling - FIXED"""
    if not expr or not expr.strip():
        return None
        
    if local_vars is None:
        local_vars = {}
        
    expr = expr.strip()
    
    # Remove trailing period
    if expr.endswith('.'):
        expr = expr[:-1].strip()
    
    # Handle string literals
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]
    
    # Handle boolean literals
    if expr.lower() == 'vrai':
        return True
    if expr.lower() == 'faux':
        return False
    
    # Handle numeric literals
    try:
        if '.' in expr and re.match(r'^\d+\.\d+$', expr):
            return float(expr)
        if re.match(r'^\d+$', expr):
            return int(expr)
    except ValueError:
        pass
    
    # Handle list/string access like liste[0]
    list_access_match = re.match(r'(\w+)\[(\d+)\]', expr)
    if list_access_match:
        var_name, index_str = list_access_match.groups()
        index = int(index_str)
        
        # Look for variable in local then global scope
        var_value = None
        if var_name in local_vars:
            var_value = local_vars[var_name]
        elif var_name in dav.variables:
            var_value = dav.variables[var_name]
        
        if var_value is not None:
            try:
                return var_value[index]
            except (IndexError, TypeError):
                return None
    
    # Built-in functions
    builtin_functions = {
        'longueur': lambda x: len(x) if hasattr(x, '__len__') else 0,
        'maximum': lambda lst: max(lst) if lst and hasattr(lst, '__iter__') and not isinstance(lst, str) else None,
        'minimum': lambda lst: min(lst) if lst and hasattr(lst, '__iter__') and not isinstance(lst, str) else None,
        'taille': lambda x: len(x) if hasattr(x, '__len__') else 0,
        'somme': lambda lst: sum(lst) if lst and hasattr(lst, '__iter__') and not isinstance(lst, str) else 0,
        'moyenne': lambda lst: sum(lst) / len(lst) if lst and hasattr(lst, '__iter__') and not isinstance(lst, str) and len(lst) > 0 else 0,
        'aleatoire': lambda: random.random(),
        'entier_aleatoire': lambda a, b: random.randint(a, b),
        'racine_carree': lambda x: math.sqrt(x),
        'puissance': lambda x, y: x ** y,
        'valeur_absolue': lambda x: abs(x),
        'arrondir': lambda x: round(x),
        'majuscule': lambda s: s.upper() if isinstance(s, str) else s,
        'minuscule': lambda s: s.lower() if isinstance(s, str) else s,
        'contient': lambda s, sub: sub in s if isinstance(s, str) else False,
        'remplace': lambda s, old, new: s.replace(old, new) if isinstance(s, str) else s,
        'diviser': lambda s, sep: s.split(sep) if isinstance(s, str) else [],
        'joindre': lambda lst, sep: sep.join(str(x) for x in lst) if isinstance(lst, list) else "",
        'trier': lambda lst: sorted(lst) if isinstance(lst, list) else lst,
        'inverser': lambda lst: list(reversed(lst)) if isinstance(lst, list) else lst,
    }
    
    # Function call detection - IMPROVED
    func_match = re.match(r'(\w+)\((.*)\)', expr)
    if func_match:
        func_name, args_str = func_match.groups()
        args = []
        
        if args_str.strip():
            # Parse arguments carefully
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
            
            # Evaluate each argument
            args = []
            for arg in args_list:
                args.append(eval_expr(arg, local_vars))
        
        # Check built-in functions first
        if func_name in builtin_functions:
            try:
                return builtin_functions[func_name](*args)
            except Exception as e:
                print(f"Erreur dans fonction built-in {func_name}: {e}")
                return None
        
        # Check user-defined functions
        if func_name in dav.functions:
            return call_function(func_name, args, local_vars)
        
        # Function not found
        return None
    
    # Replace French operators - FIXED ORDER
    french_ops = [
        (' est supérieur ou égal à ', ' >= '),
        (' est inférieur ou égal à ', ' <= '),
        (' est supérieur à ', ' > '),
        (' est inférieur à ', ' < '),
        (' n\'est pas égal à ', ' != '),
        (' est égal à ', ' == '),
        (' égale ', ' == '),
        (' égal ', ' == '),
        (' multiplié par ', ' * '),
        (' divisé par ', ' / '),
        (' division entière par ', ' // '),
        (' élevé à ', ' ** '),
        (' à la puissance ', ' ** '),
        (' modulo ', ' % '),
        (' mod ', ' % '),
        (' plus ', ' + '),
        (' moins ', ' - '),
        (' fois ', ' * '),
        (' et ', ' and '),
        (' ou ', ' or '),
        (' pas ', ' not ')
    ]
    
    # Apply French operator replacements
    original_expr = expr
    for fr_op, py_op in french_ops:
        expr = expr.replace(fr_op, py_op)
    
    # Create evaluation scope
    eval_scope = {}
    eval_scope.update(dav.variables)  # Global variables
    eval_scope.update(local_vars)     # Local variables (higher priority)
    eval_scope.update(dav.modules)    # Modules
    eval_scope.update(builtin_functions)  # Built-in functions
    
    # Add math functions directly to scope
    eval_scope.update({
        'sqrt': math.sqrt,
        'pow': pow,
        'abs': abs,
        'round': round,
        'max': max,
        'min': min,
        'sum': sum,
        'len': len
    })
    
    # Try to evaluate as Python expression
    try:
        result = eval(expr, {"__builtins__": {}}, eval_scope)
        return result
    except:
        # If it's just a variable name, look it up
        if expr in eval_scope:
            return eval_scope[expr]
        
        # Try the original expression as a variable lookup
        if original_expr in eval_scope:
            return eval_scope[original_expr]
        
        # Last resort: try to parse manually for French expressions
        try:
            # Handle "nombre moins 1" pattern
            if " moins " in original_expr:
                parts = original_expr.split(" moins ")
                if len(parts) == 2:
                    left = eval_expr(parts[0].strip(), local_vars)
                    right = eval_expr(parts[1].strip(), local_vars) 
                    if left is not None and right is not None:
                        return left - right
                        
            # Handle "nombre fois " pattern  
            if " fois " in original_expr:
                parts = original_expr.split(" fois ")
                if len(parts) == 2:
                    left = eval_expr(parts[0].strip(), local_vars)
                    right = eval_expr(parts[1].strip(), local_vars)
                    if left is not None and right is not None:
                        return left * right
        except:
            pass
        
        # If all else fails, return None instead of string
        return None

def call_function(name, args, caller_local_vars=None):
    """Call a user-defined function with proper scope isolation - FIXED"""
    if name not in dav.functions:
        return None
    
    params, body = dav.functions[name]
    
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

def get_indentation_level(line):
    """Get the indentation level of a line"""
    return len(line) - len(line.lstrip())

def parse_logical_blocks(lines):
    """Parse lines into logical blocks"""
    blocks = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        if not stripped_line or stripped_line.startswith('#'):
            i += 1
            continue
        
        # Function definition
        if any(phrase in stripped_line.lower() for phrase in ["crée une fonction", "créer une fonction", "définis une fonction"]):
            func_block, next_i = parse_function_block_with_indentation(lines, i)
            blocks.append(func_block)
            i = next_i
        
        # If-else statement
        elif stripped_line.lower().startswith("si "):
            if_block, next_i = parse_if_block_with_indentation(lines, i)
            blocks.append(if_block)
            i = next_i
        
        # While loop
        elif stripped_line.lower().startswith("tant que "):
            loop_block, next_i = parse_while_block_with_indentation(lines, i)
            blocks.append(loop_block)
            i = next_i
            
        # For loop
        elif stripped_line.lower().startswith("pour "):
            loop_block, next_i = parse_for_block_with_indentation(lines, i)
            blocks.append(loop_block)
            i = next_i
            
        # Do while loop
        elif stripped_line.lower().startswith("fais:"):
            loop_block, next_i = parse_do_while_block_with_indentation(lines, i)
            blocks.append(loop_block)
            i = next_i
        
        # Single statement
        else:
            blocks.append({'type': 'statement', 'line': stripped_line})
            i += 1
    
    return blocks

def parse_function_block_with_indentation(lines, start_i):
    """Parse a function definition block - IMPROVED parameter parsing"""
    line = lines[start_i].strip()
    base_indent = get_indentation_level(lines[start_i])
    
    # Extract function name
    func_match = re.search(r"(?:crée|créer|définis) une fonction (?:nommée|appelée) (\w+)", line.lower())
    if not func_match:
        return {'type': 'statement', 'line': line}, start_i + 1
    
    func_name = func_match.group(1)
    
    # Extract parameters - MUCH IMPROVED
    params = []
    
    # Look for parameter patterns
    if "qui prend" in line.lower():
        # Extract everything after "qui prend"
        prend_pos = line.lower().find("qui prend") + len("qui prend")
        param_part = line[prend_pos:].strip()
        
        # Handle numbered parameters (deux paramètres, trois paramètres, etc.)
        numbered_pattern = re.search(r'(deux|trois|quatre|cinq|six|sept|huit|neuf|dix)\s+(?:paramètre|parametre|nombre)(?:s)?', param_part.lower())
        if numbered_pattern:
            number_word = numbered_pattern.group(1)
            number_map = {
                'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5,
                'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9, 'dix': 10
            }
            param_count = number_map.get(number_word, 2)
            # Generate generic parameter names
            params = [f'param{i+1}' for i in range(param_count)]
        else:
            # Clean up common French phrases - IMPROVED
            # Only remove articles if they're followed by more text
            param_part = re.sub(r'(?:un |une |le |la |les |des |deux |trois |quatre |cinq )(?=\w)', '', param_part)
            
            # Special case: if the parameter is just "nombre" or "paramètre", keep it
            clean_param = param_part.lower().rstrip('.').strip()
            if clean_param in ['nombre', 'paramètre', 'nombres', 'paramètres']:
                pass  # Keep the original name
            else:
                # Remove technical words only if there's other content
                original_param = param_part
                param_part = re.sub(r'(?:nombre|paramètre)(?:s)?\s*', '', param_part)
                # If we removed everything or only punctuation, restore original
                if not param_part.strip() or param_part.strip() in ['.', ',', ';']:
                    param_part = original_param
            param_part = param_part.rstrip('.')
            
            if param_part:
                # Split on various separators
                if " et " in param_part:
                    params = [p.strip() for p in param_part.split(" et ") if p.strip()]
                elif ", " in param_part:
                    params = [p.strip() for p in param_part.split(", ") if p.strip()]
                elif param_part:
                    params = [param_part.strip()]
    
    # Default parameter if none found
    if not params:
        params = ['n']
    

    
    # Capture function body
    body_lines = []
    i = start_i + 1
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        if not current_stripped:
            i += 1
            continue
        
        if current_indent <= base_indent:
            break
        
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
    """Parse an if-else block with proper indentation handling - FIXED for nested conditions"""
    if_line = lines[start_i].strip()
    base_indent = get_indentation_level(lines[start_i])
    
    # Extract condition
    condition = if_line[3:].rstrip(':').strip()
    if condition.endswith(" alors"):
        condition = condition[:-6].strip()
    
    # Parse if body and handle nested if-else properly
    if_body = []
    else_body = []
    i = start_i + 1
    current_section = 'if'
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        if not current_stripped:
            i += 1
            continue
        
        # If we encounter a line at the same indentation level as the base if statement
        if current_indent == base_indent:
            if current_stripped.lower().startswith("sinon"):
                current_section = 'else'
                i += 1
                continue
            else:
                # End of if-else block
                break
        
        # If we encounter a line at lower indentation than base, we're done
        if current_indent < base_indent:
            break
        
        # For lines with higher indentation (body content)
        if current_indent > base_indent:
            # Check if this is a nested Si statement
            if current_stripped.lower().startswith("si "):
                # Parse the nested if block recursively
                nested_if_block, next_i = parse_if_block_with_indentation(lines, i)
                if current_section == 'if':
                    if_body.append(nested_if_block)
                else:
                    else_body.append(nested_if_block)
                i = next_i
                continue
            else:
                # Regular statement
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

def parse_while_block_with_indentation(lines, start_i):
    """Parse a while loop block with proper indentation handling"""
    loop_line = lines[start_i].strip()
    base_indent = get_indentation_level(lines[start_i])
    
    body = []
    i = start_i + 1
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        if not current_stripped:
            i += 1
            continue
        
        if current_indent <= base_indent:
            break
        
        body.append(current_stripped)
        i += 1
    
    return {
        'type': 'while_loop',
        'condition': loop_line[9:].rstrip(':').strip(),
        'body': body
    }, i

def parse_for_block_with_indentation(lines, start_i):
    """Parse a for loop block with proper indentation handling"""
    loop_line = lines[start_i].strip()
    base_indent = get_indentation_level(lines[start_i])
    
    body = []
    i = start_i + 1
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        if not current_stripped:
            i += 1
            continue
        
        if current_indent <= base_indent:
            break
        
        body.append(current_stripped)
        i += 1
    
    return {
        'type': 'for_loop',
        'loop_line': loop_line,
        'body': body
    }, i

def parse_do_while_block_with_indentation(lines, start_i):
    """Parse a do-while loop block"""
    base_indent = get_indentation_level(lines[start_i])
    
    body = []
    i = start_i + 1
    while_condition = None
    
    while i < len(lines):
        current_line = lines[i]
        current_stripped = current_line.strip()
        current_indent = get_indentation_level(current_line)
        
        if not current_stripped:
            i += 1
            continue
        
        if current_stripped.lower().startswith("tant que ") and current_indent <= base_indent:
            while_condition = current_stripped[9:].rstrip(':').strip()
            i += 1
            break
        
        if current_indent <= base_indent:
            break
        
        body.append(current_stripped)
        i += 1
    
    return {
        'type': 'do_while_loop',
        'condition': while_condition,
        'body': body
    }, i

def execute_blocks(blocks, local_vars=None):
    """Execute a list of parsed blocks"""
    if local_vars is None:
        local_vars = {}
    
    for block in blocks:
        try:
            if block['type'] == 'statement':
                execute_statement(block['line'], local_vars)
            elif block['type'] == 'function':
                dav.functions[block['name']] = (block['params'], block['body'])
            elif block['type'] == 'if':
                execute_if_block(block, local_vars)
            elif block['type'] == 'while_loop':
                execute_while_loop_block(block, local_vars)
            elif block['type'] == 'for_loop':
                execute_for_loop_block(block, local_vars)
            elif block['type'] == 'do_while_loop':
                execute_do_while_loop_block(block, local_vars)
        except (BreakLoop, ContinueLoop, ReturnValue):
            raise
        except Exception as e:
            print(f"Erreur dans le bloc: {e}")

def execute_if_block(block, local_vars):
    """Execute an if block - FIXED"""
    condition = block['condition']
    
    # Evaluate condition once and execute only the appropriate branch
    condition_result = eval_expr(condition, local_vars)
    
    # Convert to boolean properly
    if isinstance(condition_result, str):
        condition_result = condition_result.lower() in ['vrai', 'true', 'oui']
    else:
        condition_result = bool(condition_result)
    
    if condition_result:
        execute_block(block['if_body'], local_vars)
    elif block['else_body']:
        execute_block(block['else_body'], local_vars)

def execute_while_loop_block(block, local_vars):
    """Execute a while loop block"""
    condition = block['condition']
    
    while eval_expr(condition, local_vars):
        try:
            execute_block(block['body'], local_vars)
        except BreakLoop:
            break
        except ContinueLoop:
            continue

def execute_for_loop_block(block, local_vars):
    """Execute a for loop block"""
    loop_line = block['loop_line']
    
    # Parse the for loop line
    match = re.search(r"pour (?:chaque )?(\w+) dans (?:la plage |)(\w+)", loop_line.lower())
    if match:
        var_name, iterable_name = match.groups()
        
        # Get the iterable
        items = []
        if iterable_name in local_vars:
            items = local_vars[iterable_name]
        elif iterable_name in dav.variables:
            items = dav.variables[iterable_name]
        
        if not isinstance(items, (list, str)):
            items = []
        
        for item in items:
            local_vars[var_name] = item
            try:
                execute_block(block['body'], local_vars)
            except BreakLoop:
                break
            except ContinueLoop:
                continue

def execute_do_while_loop_block(block, local_vars):
    """Execute a do-while loop block"""
    condition = block['condition']
    
    while True:
        try:
            execute_block(block['body'], local_vars)
        except BreakLoop:
            break
        except ContinueLoop:
            pass
        
        if not condition or not eval_expr(condition, local_vars):
            break

def execute_block(lines, local_vars=None):
    """Execute a block of statements - FIXED to handle nested if blocks properly"""
    if local_vars is None:
        local_vars = {}
    
    for line in lines:
        # Handle both parsed if blocks and statement strings
        if isinstance(line, dict):
            # This is a parsed block (like if-else)
            if line['type'] == 'if':
                execute_if_block(line, local_vars)
            elif line['type'] == 'while_loop':
                execute_while_loop_block(line, local_vars)
            elif line['type'] == 'for_loop':
                execute_for_loop_block(line, local_vars)
            elif line['type'] == 'do_while_loop':
                execute_do_while_loop_block(line, local_vars)
        else:
            # This is a statement string
            line_str = line.strip() if isinstance(line, str) else str(line).strip()
            if line_str and not line_str.startswith('#'):
                execute_statement(line_str, local_vars)

def execute_statement(line, local_vars=None):
    """Execute a single statement"""
    if local_vars is None:
        local_vars = {}
    
    line = line.strip()
    if not line or line.startswith('#'):
        return
    
    try:
        # Variable declarations
        if any(phrase in line.lower() for phrase in ["j'ai un", "j'ai une", "créer un", "créer une"]):
            handle_variable_declaration(line)
        
        # Assignments
        elif any(phrase in line.lower() for phrase in ["assigne ", "définis ", "mets "]):
            handle_assignment(line, local_vars)
        
        # User input
        elif "demande à l'utilisateur" in line.lower():
            handle_user_input(line, local_vars)
        
        # Import modules
        elif line.lower().startswith("importe "):
            handle_import(line)
        
        # Return statement
        elif line.lower().startswith("je retourne") or line.lower().startswith("retourne"):
            handle_return(line, local_vars)
        
        # Break and continue
        elif line.lower().strip() in ["arrête", "stop"]:
            raise BreakLoop()
        elif line.lower().strip() in ["continue", "passe"]:
            raise ContinueLoop()
        
        # List operations
        elif "ajoute " in line.lower() and " à " in line.lower():
            handle_list_add(line, local_vars)
        
        elif "enlève " in line.lower() and " de " in line.lower():
            handle_list_remove(line, local_vars)
        
        # Display operations
        elif any(word in line.lower() for word in ["affiche ", "montre ", "imprime "]):
            handle_display(line, local_vars)
        
        # Increase/Decrease operations
        elif "augmente " in line.lower() or "diminue " in line.lower():
            handle_increment_decrement(line, local_vars)
        
        # Function calls with "Appelle fonction avec paramètre"
        elif line.lower().startswith("appelle "):
            handle_function_call(line, local_vars)
        
        # Line break control
        elif line.lower().strip() == "ligne":
            print()  # Force newline
        
        else:
            # Try to evaluate as expression (but don't print result)
            result = eval_expr(line, local_vars)
    
    except (BreakLoop, ContinueLoop, ReturnValue):
        raise
    except Exception as e:
        print(f"Erreur: {e}")

def handle_variable_declaration(line):
    """Handle variable declarations"""
    patterns = [
        r"j'ai un (\w+) appelé (\w+)",
        r"j'ai une (\w+) appelée (\w+)",
        r"créer un (\w+) appelé (\w+)",
        r"créer une (\w+) appelée (\w+)",
        r"j'ai un (\w+) nommé (\w+)",
        r"j'ai une (\w+) nommée (\w+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line.lower())
        if match:
            var_type, var_name = match.groups()
            if var_type in ['nombre', 'entier', 'int']:
                dav.variables[var_name] = 0
            elif var_type in ['chaîne', 'str', 'texte']:
                dav.variables[var_name] = ""
            elif var_type in ['booléen', 'bool']:
                dav.variables[var_name] = False
            elif var_type in ['liste', 'array']:
                dav.variables[var_name] = []
            elif var_type in ['dictionnaire', 'dict']:
                dav.variables[var_name] = {}
            else:
                dav.variables[var_name] = None
            break

def handle_assignment(line, local_vars):
    """Handle assignments"""
    patterns = [
        r"mets (\w+) à (.+)",
        r"définis (\w+) à (.+)",
        r"assigne (.+) à (\w+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line.lower())
        if match:
            if "assigne" in pattern:
                value_expr, var_name = match.groups()
            else:
                var_name, value_expr = match.groups()
            
            value = eval_expr(value_expr.strip(), local_vars)
            
            # Assign to local scope if we're in a function, otherwise global
            if local_vars and var_name in local_vars:
                local_vars[var_name] = value
            else:
                # For assignments, prefer local scope if we have it
                if local_vars:
                    local_vars[var_name] = value
                else:
                    dav.variables[var_name] = value
            break

def handle_user_input(line, local_vars):
    """Handle user input"""
    match = re.search(r"demande à l'utilisateur.*?(?:pour|de donner.*?pour|la valeur de|la valeur pour) (\w+)", line.lower())
    if match:
        var_name = match.group(1)
        user_input = input(f"Entrez la valeur pour {var_name}: ")
        
        # Try to convert to appropriate type
        value = user_input
        try:
            value = to_number(user_input)
        except:
            if user_input.lower() in ['vrai', 'faux', 'true', 'false']:
                value = to_boolean(user_input)
        
        if var_name in local_vars:
            local_vars[var_name] = value
        else:
            dav.variables[var_name] = value

def handle_import(line):
    """Handle imports"""
    match = re.search(r"importe (?:le module )?(\w+)", line.lower())
    if match:
        module_name = match.group(1)
        try:
            if module_name == 'math':
                dav.modules['math'] = math
            elif module_name == 'random':
                dav.modules['random'] = random
            else:
                dav.modules[module_name] = importlib.import_module(module_name)
        except ImportError:
            print(f"Attention: Impossible d'importer le module {module_name}")

def handle_return(line, local_vars):
    """Handle return statements"""
    if line.lower().startswith("je retourne"):
        expr = line[12:].strip()
    else:
        expr = line[8:].strip()
    
    value = eval_expr(expr, local_vars)
    raise ReturnValue(value)

def handle_list_add(line, local_vars):
    """Handle adding to lists"""
    match = re.search(r"ajoute (.+) à (\w+)", line.lower())
    if match:
        value_expr, list_name = match.groups()
        value = eval_expr(value_expr, local_vars)
        
        target_list = None
        if list_name in local_vars and isinstance(local_vars[list_name], list):
            target_list = local_vars[list_name]
        elif list_name in dav.variables and isinstance(dav.variables[list_name], list):
            target_list = dav.variables[list_name]
        
        if target_list is not None:
            target_list.append(value)

def handle_list_remove(line, local_vars):
    """Handle removing from lists"""
    match = re.search(r"enlève (.+) de (\w+)", line.lower())
    if match:
        value_expr, list_name = match.groups()
        value = eval_expr(value_expr, local_vars)
        
        target_list = None
        if list_name in local_vars and isinstance(local_vars[list_name], list):
            target_list = local_vars[list_name]
        elif list_name in dav.variables and isinstance(dav.variables[list_name], list):
            target_list = dav.variables[list_name]
        
        if target_list and value in target_list:
            target_list.remove(value)

def handle_display(line, local_vars):
    """Handle display operations with user-controlled line breaks"""
    line_lower = line.lower()
    
    # Extract what to display
    expr = ""
    if "affiche le résultat de" in line_lower:
        start = line_lower.find("affiche le résultat de") + len("affiche le résultat de")
        expr = line[start:].strip()
    elif "affiche " in line_lower:
        start = line_lower.find("affiche") + len("affiche")
        expr = line[start:].strip()
    elif "montre " in line_lower:
        start = line_lower.find("montre") + len("montre")
        expr = line[start:].strip()
    elif "imprime " in line_lower:
        start = line_lower.find("imprime") + len("imprime")
        expr = line[start:].strip()
    
    # Clean up expression
    if expr.endswith('.'):
        expr = expr[:-1]
    if expr.lower().endswith("sur l'écran"):
        expr = expr[:-(len("sur l'écran"))].strip()
    elif expr.lower().endswith("à l'écran"):
        expr = expr[:-(len("à l'écran"))].strip()
    
    # Check for line control keywords
    add_newline = False
    if expr.lower().endswith(" ligne"):
        expr = expr[:-6].strip()  # Remove " ligne"
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
    """Handle increment/decrement operations"""
    patterns = [
        (r"augmente (\w+) de (.+)", 1),
        (r"diminue (\w+) de (.+)", -1)
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
            elif var_name in dav.variables:
                current_value = dav.variables[var_name] or 0
                dav.variables[var_name] = current_value + amount
            break

def handle_function_call(line, local_vars):
    """Handle function calls like 'Appelle fonction avec paramètre'"""
    # Parse "Appelle nom_fonction avec paramètre"
    match = re.search(r"appelle (\w+) avec (.+)", line.lower())
    if match:
        func_name, args_expr = match.groups()
        
        # Remove trailing period
        args_expr = args_expr.rstrip('.')
        
        # Split multiple arguments by "et" and evaluate each
        args_list = []
        if " et " in args_expr:
            # Multiple arguments separated by "et"
            arg_parts = [part.strip() for part in args_expr.split(" et ")]
            for arg_part in arg_parts:
                arg_value = eval_expr(arg_part, local_vars)
                args_list.append(arg_value)
        else:
            # Single argument
            arg_value = eval_expr(args_expr, local_vars)
            args_list.append(arg_value)
        
        # Call the function
        if func_name in dav.functions:
            result = call_function(func_name, args_list, local_vars)
            return result
    
    # Parse "Appelle nom_fonction" (no parameters)
    match = re.search(r"appelle (\w+)", line.lower())
    if match:
        func_name = match.group(1)
        if func_name in dav.functions:
            result = call_function(func_name, [], local_vars)
            return result

def flush_output():
    """Flush any pending output"""
    if dav.output_buffer:
        print("".join(dav.output_buffer))
        dav.output_buffer = []

def run_dav(filename):
    """Run a .dav program from a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        lines = [line.rstrip() for line in lines]
        lines = [line for line in lines if line.strip()]
        
        # Reset interpreter state
        dav.reset()
        
        # Parse and execute
        blocks = parse_logical_blocks(lines)
        execute_blocks(blocks)
        
        # Flush any remaining output
        flush_output()
        
    except FileNotFoundError:
        print(f"Erreur: Fichier '{filename}' non trouvé.")
    except ReturnValue:
        # Top-level return should just end execution
        flush_output()
    except Exception as e:
        import traceback
        print(f"Erreur lors de l'exécution du programme: {e}")
        print("Trace:")
        traceback.print_exc()
        flush_output()

def run_dav_code(code):
    """Run .dav code from a string"""
    try:
        lines = [line.rstrip() for line in code.split('\n')]
        lines = [line for line in lines if line.strip()]
        
        # Reset interpreter state
        dav.reset()
        
        # Parse and execute
        blocks = parse_logical_blocks(lines)
        execute_blocks(blocks)
        
        # Flush any remaining output
        flush_output()
        
    except Exception as e:
        print(f"Erreur lors de l'exécution: {e}")
        flush_output()

def test_pierre_papier_ciseaux():
    """Test the fixed conditional logic with Pierre-Papier-Ciseaux"""
    code = '''
J'ai un texte appelé joueur.
J'ai un texte appelé ordinateur.

Mets joueur à "pierre".
Mets ordinateur à "papier".

Si joueur est égal à ordinateur:
    Affiche "Égalité!".
Sinon:
    Si joueur est égal à "pierre" et ordinateur est égal à "ciseaux":
        Affiche "Joueur gagne!".
    Sinon:
        Si joueur est égal à "papier" et ordinateur est égal à "pierre":
            Affiche "Joueur gagne!".
        Sinon:
            Si joueur est égal à "ciseaux" et ordinateur est égal à "papier":
                Affiche "Joueur gagne!".
            Sinon:
                Affiche "Ordinateur gagne!".
'''
    print("Test Pierre-Papier-Ciseaux (joueur: pierre, ordinateur: papier):")
    run_dav_code(code)
    print()

def test_continuous_display():
    """Test the continuous display with proper spacing"""
    code = '''
Affiche "Bonjour".
Affiche " ".
Affiche "monde".
Affiche "!".
'''
    print("Test Affichage Continu:")
    run_dav_code(code)
    print()

def test_factorial():
    """Test the COMPLETELY FIXED function scope and recursion"""
    code = '''
Crée une fonction nommée factorielle qui prend n.
    Si n est inférieur ou égal à 1:
        Je retourne 1.
    Sinon:
        Je retourne n fois factorielle(n moins 1).

Mets résultat à factorielle(5).
Affiche résultat.
'''
    print("Test Factorielle (devrait afficher 120):")
    run_dav_code(code)
    print()

def test_list_access():
    """Test the list access functionality"""
    code = '''
J'ai une liste appelée nombres.
Ajoute 10 à nombres.
Ajoute 20 à nombres.
Ajoute 30 à nombres.

Affiche "Premier élément: ".
Affiche nombres[0].
Affiche "Taille de la liste: ".
Affiche taille(nombres).
Affiche "Maximum: ".
Affiche maximum(nombres).
'''
    print("Test Accès aux Listes:")
    run_dav_code(code)
    print()

def test_string_manipulation():
    """Test the string manipulation functions"""
    code = '''
J'ai un texte appelé mot.
Mets mot à "Bonjour".

Affiche "Longueur: ".
Affiche longueur(mot).
Affiche "Première lettre: ".
Affiche mot[0].
Affiche "En majuscules: ".
Affiche majuscule(mot).
Affiche "Contient 'our': ".
Affiche contient(mot, "our").
'''
    print("Test Manipulation de Chaînes:")
    run_dav_code(code)
    print()

def test_advanced_features():
    """Test more advanced features - COMPLETELY REWRITTEN"""
    code = '''
# Test de fonctions avec paramètres multiples
Crée une fonction nommée addition qui prend a et b.
    Je retourne a plus b.

Crée une fonction nommée puissance_personnalisee qui prend base et exposant.
    Si exposant est égal à 0:
        Je retourne 1.
    Sinon:
        Si exposant est égal à 1:
            Je retourne base.
        Sinon:
            Je retourne base fois puissance_personnalisee(base, exposant moins 1).

# Test des fonctions
Affiche "Addition 3 + 4 = ".
Affiche addition(3, 4).
Affiche "Puissance 2^3 = ".
Affiche puissance_personnalisee(2, 3).

# Test de liste avec boucle
J'ai une liste appelée nombres.
Ajoute 1 à nombres.
Ajoute 2 à nombres.
Ajoute 3 à nombres.

Affiche "Somme de la liste: ".
Affiche somme(nombres).
Affiche "Liste triée: ".
Affiche trier(nombres).
'''
    print("Test Fonctionnalités Avancées:")
    run_dav_code(code)
    print()

def test_debug_factorial():
    """Special debug test for factorial to see what's happening"""
    print("=== Test Debug Factorielle ===")
    
    # Test step by step
    print("1. Définition de la fonction:")
    code1 = '''
Crée une fonction nommée factorielle qui prend n.
    Si n est inférieur ou égal à 1:
        Je retourne 1.
    Sinon:
        Je retourne n fois factorielle(n moins 1).
'''
    run_dav_code(code1)
    print("Fonction définie.")
    
    print("\n2. Test avec n=1:")
    code2 = '''
Affiche factorielle(1).
'''
    run_dav_code(code2)
    
    print("\n3. Test avec n=2:")
    code3 = '''
Affiche factorielle(2).
'''
    run_dav_code(code3)
    
    print("\n4. Test avec n=3:")
    code4 = '''
Affiche factorielle(3).
'''
    run_dav_code(code4)
    
    print("\n5. Test avec n=5:")
    code5 = '''
Mets résultat à factorielle(5).
Affiche "Résultat final: ".
Affiche résultat.
'''
    run_dav_code(code5)
    print()

def main():
    """Main entry point with improved functionality"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            print("=== Tests des Améliorations DAV (Version COMPLETEMENT Corrigée) ===\n")
            test_pierre_papier_ciseaux()
            test_continuous_display()
            test_factorial()
            test_list_access()
            test_string_manipulation()
            test_advanced_features()
        elif sys.argv[1] == "--debug":
            test_debug_factorial()
        else:
            filename = sys.argv[1]
            run_dav(filename)
    else:
        # Interactive mode
        print("Interpréteur du Langage DAV Français - Version COMPLÈTEMENT Corrigée")
        print("Tapez 'sortie' pour quitter, 'aide' pour des exemples, 'test' pour les tests, 'debug' pour debug")
        
        while True:
            try:
                line = input("dav> ").strip()
                if line.lower() in ['sortie', 'quit', 'exit']:
                    break
                elif line.lower() == 'test':
                    print("\n=== Tests des Améliorations ===")
                    test_pierre_papier_ciseaux()
                    test_continuous_display()
                    test_factorial()
                    test_list_access()
                    test_string_manipulation()
                    test_advanced_features()
                elif line.lower() == 'debug':
                    test_debug_factorial()
                elif line.lower() == 'aide':
                    print("""
Exemples avec les nouvelles fonctionnalités COMPLÈTEMENT corrigées:

Variables et Types:
  J'ai un nombre appelé x.
  Mets x à 10.
  Affiche x.

Fonctions (scope COMPLÈTEMENT CORRIGÉ):
  Crée une fonction nommée double qui prend n.
      Je retourne n fois 2.
  Affiche double(5).

Fonctions récursives (COMPLÈTEMENT CORRIGÉES):
  Crée une fonction nommée factorielle qui prend n.
      Si n est inférieur ou égal à 1:
          Je retourne 1.
      Sinon:
          Je retourne n fois factorielle(n moins 1).
  Affiche factorielle(5).

Conditions:
  Si x est supérieur à 5:
      Affiche "Grand".
  Sinon:
      Affiche "Petit".

Listes avec accès par index:
  J'ai une liste appelée nums.
  Ajoute 1 à nums.
  Ajoute 2 à nums.
  Affiche nums[0].
  Affiche maximum(nums).

Chaînes de caractères:
  J'ai un texte appelé mot.
  Mets mot à "Hello".
  Affiche mot[0].
  Affiche longueur(mot).

CORRECTIONS MAJEURES APPORTÉES:
- Expression evaluation completely rewritten for proper recursion
- French operator translation fixed and optimized
- Conditional logic (if/else) completely fixed
- Boolean evaluation improved
- Mathematical operations now work correctly
- Function scope isolation improved
- Built-in function error handling enhanced
""")
                elif line:
                    run_dav_code(line)
                    flush_output()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erreur: {e}")
                flush_output()
        
        print("Au revoir!")

if __name__ == "__main__":
    main()
