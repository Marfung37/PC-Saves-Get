import re
from collections import Counter

TOKEN_SPEC = [
  ('OR',       r'\|\|'),
  ('AND',      r'&&'),
  ('NOT',      r'!'),
  ('AVOID',    r'\^'),
  ('LPAREN',   r'\('),
  ('RPAREN',   r'\)'),
  ('REGEX',    r'/([^/\\]|\\.)+/'),
  ('PIECES',   r'[TILJSZO]+'),
  ('WS',       r'\s+'),  # Skip whitespace
]
MASTER_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
token_re = re.compile(MASTER_REGEX)

class Token:
  def __init__(self, kind=None, value=None):
    self.kind = kind
    self.value = value
  def __repr__(self):
    return f"({self.kind}, '{self.value}')"

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

class PiecesLiteral(AST):
  def __init__(self, value):
    self.value = value
  def __repr__(self):
    return f"Pieces({self.value})"

class RegexLiteral(AST):
  def __init__(self, value):
    self.value = value
  def __repr__(self):
    return f"Regex(`{self.value}`)"

class Parser:
  """
  Recursive Descent Parser with precedence OR, AND, NOT, AVOID, ATOMIC
  """
  def __init__(self):
    self._tokens = []
    self._pos = 0

  def _peek(self):
    return self._tokens[self._pos] if self._pos < len(self._tokens) else Token()

  def _consume(self, expected=None):
    token = self._peek()
    if expected and token.kind != expected:
      raise ValueError(f"Expected {expected} but got {token.kind}")
    self._pos += 1
    return token

  def parse(self, expr, lexer):
    self._tokens = lexer(expr)
    self._pos = 0
    return self._parse_tokens()

  def _parse_tokens(self):
    return self._parse_or()

  def _parse_or(self):
    left = self._parse_and()
    while self._peek().kind == 'OR':
      self._consume('OR')
      right = self._parse_and()
      left = BinaryOp(left, 'OR', right)
    return left

  def _parse_and(self):
    left = self._parse_unary()
    while self._peek().kind == 'AND':
      self._consume('AND')
      right = self._parse_unary()
      left = BinaryOp(left, 'AND', right)
    return left

  def _parse_unary(self):
    # NOT
    if self._peek().kind == 'NOT':
      self._consume('NOT')
      expr = self._parse_unary()
      return UnaryOp('NOT', expr)

    # AVOID
    if self._peek().kind == 'AVOID':
      self._consume('AVOID')
      expr = self._parse_unary()
      return UnaryOp('AVOID', expr)
    else:
      return self._parse_atom()

  def _parse_atom(self):
    token = self._peek()
    if token is None:
      raise ValueError(f"Reached each of tokens too early")

    # if parentheses
    if token.kind == 'LPAREN':
      self._consume('LPAREN')
      expr = self._parse_tokens()
      self._consume('RPAREN')
      return expr

    # if regex
    elif token.kind == 'REGEX':
      regex_expr = self._consume('REGEX')
      return RegexLiteral(regex_expr.value)

    elif token.kind == 'PIECES':
      pieces = self._consume('PIECES')
      return PiecesLiteral(pieces.value)

    else:
      raise ValueError(f"Unexpected token: {token}")

# --- AST Evaluator ---
# This function will traverse the AST and execute the boolean logic.
# For readability and simplicity, no simplification of the boolean expression is done.
def evaluate_ast(node, saves: list[str]) -> bool:
  if isinstance(node, PiecesLiteral):
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

def tokenize(text):
  tokens = []
  for match in token_re.finditer(text):
    kind = match.lastgroup
    value = match.group()
    if kind == 'WS':
      continue  # skip whitespace
    tokens.append(Token(kind, value))
  return tokens

expr1 = "(S && ^T || (O && !I))"
parser = Parser()
ast = parser.parse(expr1, tokenize)
print(ast)
