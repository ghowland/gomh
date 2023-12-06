

class Vector2:
  """Stop using a list, and use a specific class for tracking position points in 2D"""
  
  def __init__(self, x=0, y=0):
    self.x = int(x)
    self.y = int(y)


  def __repr__(self):
    return f'({self.x}, {self.y})'


  def MoveX(self, move):
    self.x += int(move)


  def MoveY(self, move):
    self.y += int(move)


  def HorizTest(self, other):
    if self.x < other.x:
      return -1
    elif self.x == other.x: 
      return 0
    else:
      return 1


  def VertTest(self, other):
    if self.y < other.y:
      return -1
    elif self.y == other.y:
      return 0
    else:

      return 1

  def ToTuple(self):
    return (self.x, self.y)


  def Clone(self):
    """Make a new Vector2, so we dont change the values"""
    return Vector2(self.x, self.y)


