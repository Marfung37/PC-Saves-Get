# PC-Saves-Get
Extension of calculating saves based on knewjade's sfinder

# Dependences
```pip3 install argparse``` - parser for command line 

# Wanted Saves Format
* ``I, LS, LSZ`` - does each wanted saves separately
* ``^S`` - avoider, possible to avoid S
    * matches ``[LS, LZ]``
    * fails ``[LS, SZ]``
* ``!T`` - NOT, gives inverse result: always unable to save T
    * matches ``[L, S] [LSZO]``
    * fails ``[T, I] [TLSZ]``
* ``T&&S`` - AND, both T&&S are saveable
    * matches ``[T, S, Z] [TSZ]``
    * fails ``[S, Z] [SZO] [TZ]``
* ``T||S`` - OR, at least one of T or S are saveable
    * matches ``[T, Z] [TSO] [LSO]``
    * fails ``[I, L, O] [LZO]``
* ``!(T&&S)||L`` - does T&&S first before rest of expression
   * With ^(T&&S) it distributes the avoider to T and S and does || instead (De Morgan's Law)
* ``LSZ`` - queue, all of L,S,Z are in at least one of the saves
    * matches ``[LSZO, TSZO] [TLSZ, LLSZ]``
    * fails ``[L, S, Z] [TSZ, JSZ]``
* ``/^[^T]\*L[^J]\*$/`` - regex queue, a regex expression in ``//``: at least one save has L but not T nor J
    * matches ``[ILSZ, IJSZ] [LL]``
    * fails ``[TLSZ] [LJSZ]``
    * the order of saves always follow TILJSZO
    * Note: this is necessary for the full potential of wanted saves expressions

# Cmd Line Format
```python3 sfinder-saves [cmd] [options]```
## Commands
### percent
Give the percent of saves based on the path file
#### Options
``--wanted-save`` or ``-w`` - the save expression  
``--key`` or ``-k`` - use wantedPiecesMap.json for preset wanted saves  
``--all`` or ``-a`` - output all of the saves and corresponding percents  
  * Note: At least one of ``-w``, ``-k``, or ``-a`` is required to run percent  
  * Note: If ``-w``, ``-k``, or ``-a`` are included, they will be concatanated together </ul>
``--pieces`` or ``-p`` - pieces used on the setup  
``--pc-num`` or ``-pc`` - pc num for setup & solve  
  * Note: At least one of ``-p`` or ``-pc`` is required for percent
  * Note: If both ``-p`` and ``-pc`` is included, ``-p`` would take precedence </ul>
``--path``  or ``-f`` - path file directory (default: output/path.csv)  
``--output`` or ``-o`` - output file directory (default: output/saves.txt)  
``--print`` or ``-pr`` - print out the output into the terminal (default: true)  
``--fraction`` or ``-fr`` - include the fraction along with the percent (default: true)  
``--fails`` or ``-fa`` - include the fail queues for saves in output (default: false)  
``--over-solves`` or ``-os`` - have the percents be saves/solves (default: false)  
