import re
from collections import Counter
from collections.abc import Callable

TOKEN_SPEC = [
  ('OR',       r'\|\|'),
  ('AND',      r'&&'),
  ('NOT',      r'!'),
  ('AVOID',    r'\^'),
  ('LPAREN',   r'\('),
  ('RPAREN',   r'\)'),
  ('REGEX',    r'/[^/]+/'), # regex within forward slashes, ie /abc/
  ('PIECES',   r'[TILJSZO]+'),
  ('WS',       r'\s+'),  # Skip whitespace
]
MASTER_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
token_re = re.compile(MASTER_REGEX)

class Token:
  def __init__(self, kind: str | None = None, value: str | None = None):
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
  def __init__(self, value: str):
    self.value = value
  def __repr__(self):
    return f"Pieces({self.value})"

class RegexLiteral(AST):
  def __init__(self, value: str):
    self.value = value
  def __repr__(self):
    return f"Regex(`{self.value}`)"

def tokenize(text):
  tokens = []
  for match in token_re.finditer(text):
    kind = match.lastgroup
    value = match.group()
    if kind == 'WS':
      continue  # skip whitespace
    if kind == 'REGEX':
      value = value[1:-1] # strip forward slashes
    tokens.append(Token(kind, value))

  if len(tokens) == 0:
    raise ValueError(f"Expression {text} could not be tokenized")

  return tokens

class Parser:
  """
  Recursive Descent Parser with precedence OR, AND, NOT, AVOID, ATOMIC
  """
  def __init__(self, lexer: Callable[[str], list[Token]] = tokenize):
    self._tokens = []
    self._pos = 0
    self._lexer = lexer

  def _peek(self) -> Token:
    return self._tokens[self._pos] if self._pos < len(self._tokens) else Token()

  def _consume(self, expected=None) -> Token:
    token = self._peek()
    if expected and token.kind != expected:
      raise ValueError(f"Expected {expected} but got {token.kind}")
    self._pos += 1
    return token

  def parse(self, expr: str, lexer: Callable[[str], list[Token]] | None = None) -> AST:
    if lexer is None:
      lexer = self._lexer
    self._tokens = lexer(expr)
    self._pos = 0
    return self._parse_tokens()

  def _parse_tokens(self) -> AST:
    return self._parse_or()

  def _parse_or(self) -> AST:
    left = self._parse_and()
    while self._peek().kind == 'OR':
      self._consume('OR')
      right = self._parse_and()
      left = BinaryOp(left, 'OR', right)
    return left

  def _parse_and(self) -> AST:
    left = self._parse_unary()
    while self._peek().kind == 'AND':
      self._consume('AND')
      right = self._parse_unary()
      left = BinaryOp(left, 'AND', right)
    return left

  def _parse_unary(self) -> AST:
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
      if regex_expr.value is None:
        raise ValueError(f"No regex expression found for REGEX token")
      return RegexLiteral(regex_expr.value) 

    elif token.kind == 'PIECES':
      pieces = self._consume('PIECES')
      if pieces.value is None:
        raise ValueError(f"No pieces found for PIECES token")
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
      raise ValueError(f"Invalid regex: '{node.value}' - {e}")
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

  raise ValueError(f"Unknown AST node type or operation: {type(node)}")

if __name__ == "__main__":
  parser = Parser()

  # Test 1: Basic boolean expression with identifiers
  expr1 = "S && !T || (O && !I)"
  print(f"\nParsing: '{expr1}'")
  ast1 = parser.parse(expr1, tokenize)
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
  ast2 = parser.parse(expr2, tokenize)
  print(f"AST: {ast2}")

  saves3 = ['TL', 'TJ', 'TS', 'SZ', 'IL']
  result3 = evaluate_ast(ast2, saves3)
  print(f"Evaluate with {saves3}: {result3}") # Expected: T || F -> T

  expr3 = r'/T[^T]/||/^[^LJ]*[LJ]{2}[^LJ]*$/||/^[^LJ]+$/'
  print(f"\nParsing: '{expr3}'")
  ast3 = parser.parse(expr3, tokenize)
  print(f"AST: {ast3}")

  # Expect to error
  ast4 = parser.parse('abc', tokenize)
  print(ast3)


