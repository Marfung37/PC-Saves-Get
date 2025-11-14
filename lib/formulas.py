# Various functions representing useful calculations
from .constants import HOLD

def WIDTHHEIGHT2NUMPIECES(width: int, height: int) -> int:
  area = width * height
  num_pieces, r = divmod(area, 4)
  if r != 0:
    raise ValueError("Width and height is not divisible by 4 necessary for PC")
  
  return num_pieces + HOLD


def LONUM2BAGCOMP(leftover_num: int, num_pieces: int = 11) -> list[int]:
    '''
    Generate the bag composition of the pc to 11 pieces

    Parameters:
        leftover_num(int): length of the leftovere in range 1-7

    Return:
        list[int]: number of pieces for each bag in the pc
    '''

    bag_comp: list[int] = [leftover_num]

    while sum(bag_comp) < num_pieces:
        bag_comp.append(min(num_pieces - sum(bag_comp), 7))
    
    return bag_comp
