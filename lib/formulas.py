# Various functions representing useful calculations

def PCNUM2LONUM(pc_num: int) -> int:
    '''
    Convert a given pc number to the length of leftover

    Parameters:
        pc_num(int): a pc number in range 1-9

    Return:
        int: a length of the leftover in range 1-7
    '''
    
    return ((pc_num * 4) + 2) % 7 + 1

def LONUM2PCNUM(leftover_num: int) -> int:
    '''
    Convert a given length of leftover to pc number
    
    Parameters:
        leftover_num(int): length of the leftover in range 1-7

    Return:
        int: a pc number in range 1-7
    '''

    return (leftover_num * 2) % 7 + 1

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
