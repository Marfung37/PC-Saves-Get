import ply.lex as lex
import ply.yacc as yacc
import re
from collections import Counter

class AST:
    pass

class BinaryOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op # Store the operator token or type
        self.right = right
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    def __repr__(self):
        return f"({self.op} {self.expr})"

class Identifier(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Ident({self.value})"

class RegexLiteral(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Regex(`{self.value}`)"

# --- Lexer ---
tokens = (
  'IDENTIFIER',
  'REGEX',
  'AVOID',
  'AND',
  'OR',
  'NOT',
  'LPAREN',
  'RPAREN',
)

t_AVOID = r'\^'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_IDENTIFIER(t):
  r'[TILJSZO]+'
  return t

def t_REGEX(t):
  r'/([^/\n]*)/' # Matches / follow by another /
  t.value = t.value[1:-1] # Strip the leading and trailing forward slash
  return t

t_ignore = ' \t'

def t_error(t):
  print(f"Illegal character '{t.value[0]}'")
  t.lexer.skip(1)

lexer = lex.lex()

# --- Parser ---
precedence = (
  ('left', 'OR'),
  ('left', 'AND'),
  ('right', 'NOT'),
  ('right', 'AVOID'),
)

# Grammar rules (using p_ prefix for PLY)
def p_expression_binop(p):
    '''
    expression : expression AND expression
               | expression OR expression
    '''
    # Create BinaryOp AST nodes
    if p[2] == '&&':
        p[0] = BinaryOp(p[1], 'AND', p[3])
    elif p[2] == '||':
        p[0] = BinaryOp(p[1], 'OR', p[3])

def p_expression_avoid(p):
    'expression : AVOID expression'
    # Create UnaryOp AST node for AVOID
    p[0] = UnaryOp('AVOID', p[2])

def p_expression_not(p):
    'expression : NOT expression'
    # Create UnaryOp AST node for NOT
    p[0] = UnaryOp('NOT', p[2])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2] # The expression inside the parentheses

def p_expression_identifier(p):
    'expression : IDENTIFIER'
    # Create Identifier AST node
    p[0] = Identifier(p[1])

def p_expression_regex(p):
    'expression : REGEX'
    # Create RegexLiteral AST node
    p[0] = RegexLiteral(p[1])

# Error rule for syntax errors
def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}' (type: {p.type}, line: {p.lineno}, pos: {p.lexpos})")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

# --- AST Evaluator ---
# This function will traverse the AST and execute the boolean logic.
# For readability and simplicity, no simplification of the boolean expression is done.
def evaluate_ast(node, saves: list[str]) -> bool:
  if isinstance(node, Identifier):
    # if save within any of the saves
    wantedSaveCount = Counter(node.value)
    return any(map(lambda save: wantedSaveCount <= Counter(save), saves))

  elif isinstance(node, RegexLiteral):
    try:
      # Compile the regex and check for a match
      pattern = re.compile(node.value)
      return any(map(lambda save: pattern.search(save), saves))
    except re.error as e:
      raise Exception(f"Invalid regex: '{node.value}' - {e}")
  elif isinstance(node, UnaryOp):
    if node.op == 'NOT':
      return not evaluate_ast(node.expr, saves)
    elif node.op == 'AVOID':
      # if there is at least one that is not the expression
      return any(map(lambda save: not evaluate_ast(node.expr, [save]), saves))

  elif isinstance(node, BinaryOp):
    # Evaluate left side first
    left_val = evaluate_ast(node.left, saves)

    # short circuit if possible
    if node.op == 'AND' and not left_val:
      return False

    elif node.op == 'OR' and left_val:
      return True

    # evaluate and return right side otherwise
    return evaluate_ast(node.right, saves)

  raise Exception(f"Unknown AST node type or operation: {type(node)}")

if __name__ == '__main__':
  print("--- PLY Parsing Examples ---")

  # Test 1: Basic boolean expression with identifiers
  expr1 = "S && !T || (O && !I)"
  print(f"\nParsing: '{expr1}'")
  ast1 = parser.parse(expr1, lexer=lexer)
  print(f"AST: {ast1}")

  saves1 = ['ST', 'SZ', 'OI']
  result1 = evaluate_ast(ast1, saves1)
  print(f"Evaluate with {saves1}: {result1}") # Expected: (T && !T || (T && !T)) -> F

  saves2 = ['ST', 'SZ', 'SO']
  result2 = evaluate_ast(ast1, saves2)
  print(f"Evaluate with {saves2}: {result2}") # Expected: (T && !T || (T && !F)) -> T

  # Test 2: Expression with regex literals
  expr2 = r'/T[ISZO]/ || LJ'
  print(f"\nParsing: '{expr2}'")
  ast2 = parser.parse(expr2, lexer=lexer)
  print(f"AST: {ast2}")
  
  saves3 = ['TL', 'TJ', 'TS', 'SZ', 'IL']
  result3 = evaluate_ast(ast2, saves3)
  print(f"Evaluate with {saves3}: {result3}") # Expected: T || F -> T
  
  # # Evaluate Scenario 2: fileType doesn't match, fileSizeSmall is false, phone number present
  # vars4 = {'fileType': False, 'fileSizeSmall': False}
  # text_to_match_4 = "my_report.pdf with a number 123-45-6789" # Matches \d{3}-\d{2}-\d{4}
  # result4 = evaluate_ast(ast2, vars4, text_to_match_4)
  # print(f"Evaluate with {vars4}, text='{text_to_match_4}': {result4}") # Expected: (F && !F || T) -> (F || T) -> T
  #
  # # Test 3: Invalid regex (demonstrates error handling)
  # expr_invalid_regex = r'isValid && \d{3}-\['
  # print(f"\nParsing invalid regex: '{expr_invalid_regex}'")
  # try:
  #     ast_invalid_regex = parser.parse(expr_invalid_regex, lexer=lexer)
  #     # If parsing succeeds, try evaluating to trigger regex compilation error
  #     evaluate_ast(ast_invalid_regex, {'isValid': True})
  # except Exception as e:
  #     print(f"Caught error during parsing/evaluation: {e}")
  #
  # # Test 4: Unclosed regex (lexer error)
  # expr_unclosed_regex = r'value && \unclosed'
  # print(f"\nParsing unclosed regex: '{expr_unclosed_regex}'")
  # try:
  #     parser.parse(expr_unclosed_regex, lexer=lexer.clone()) # Use clone for fresh lexer state
  # except Exception as e:
  #     print(f"Caught error during parsing: {e}")
