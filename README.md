# PC-Saves-Get
Extension of calculating saves based on knewjade's sfinder

# Dependencies
```pip install py_fumen_py``` - [fumen api](https://github.com/OctupusTea/py-fumen-py/tree/main)  
```npm install -g sfinder-strict-minimal``` - [sfinder-strict-minimal](https://github.com/eight04/sfinder-strict-minimal)  

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
* ``/^[^T]*L[^J]*$/`` - regex queue, a regex expression in ``//``: at least one save has L but not T nor J
    * matches ``[ILSZ, IJSZ] [LL]``
    * fails ``[TLSZ] [LJSZ]``
    * the order of saves always follow TILJSZO
    * Note: this is necessary for the full potential of wanted saves expressions
* ``/T[^T]/#one T`` - add ``#`` with text to label the expression
# Cmd Line Format
```python3 sfinder-saves.py [cmd] [options]```
## Commands
## percent
Gives the save percentage
#### Options
``--wanted-save`` or ``-w`` - the save expression  
``--key`` or ``-k`` - use saves.json for preset wanted saves  
``--all`` or ``-a`` - output all of the saves and corresponding percents  

  * Note: At least one of ``-w``, ``-k``, or ``-a`` is required to run percent  
  * Note: If ``-w`` or ``-k``, they will be concatanated together while with ``-a`` will only output all saves

`--build` or `-b` - pieces in the build of the setup  
`--leftover` or `-l` - pieces in the leftover for this pc. This is inital pieces of PC that are part of a bag.  
`--pc-num` or `-pc` - pc number for the setup  

  * Note: All `-b`, `-l`, and `-pc` are required to run  

`--two-line` or `-tl` - setup is two lines (default: false)  
``--best-save`` or ``-bs`` - enable best save where first wantedSave is priority and second and so on  
``--tree-depth`` or ``-td`` - set the tree depth of pieces in percent (default: 0)  
``--path-file``  or ``-f`` - path filepath (default: output/path.csv)  
``--log-path`` or ``-lp`` - output filepath (default: output/last_output.txt)  
``--saves-path`` or ``-sp`` - path to json file with preset wanted saves (default: GITROOT/saves.json)  
``--console-print`` or ``-pr`` - log to terminal (default: true)  
``--fails`` or ``-fa`` - include the fail queues for saves in output (default: false)  
``--over-solves`` or ``-os`` - have the percents be out of when setup is solvable (default: false)  
___
## filter
Filter path.csv for only solves that meet the wanted saves and outputs the solves
### Options
``--wanted-save`` or ``-w`` - the save expression  
``--key`` or ``-k`` - use wantedPiecesMap.json for preset wanted saves  
``--index`` or ``-i`` - index of -k or -w to pick which expression to filter by (default=0)  

  * Note: One of ``-w`` or ``-k`` is required to run filter  

`--build` or `-b` - pieces in the build of the setup  
`--leftover` or `-l` - pieces in the leftover for this pc. This is inital pieces of PC that are part of a bag.  
`--pc-num` or `-pc` - pc number for the setup  

  * Note: All `-b`, `-l`, and `-pc` are required to run  

`--two-line` or `-tl` - setup is two lines (default: false)  
``--best-save`` or ``-bs`` - enable best save where first wantedSave is priority and second and so on  
``--cumulative`` or ``-c`` - gives percents cumulatively in fumens only in a minimal set (default: False)  
``--path-file``  or ``-f`` - path filepath (default: output/path.csv)  
``--log-path`` or ``-lp`` - output filepath (default: output/last_output.txt)  
``--saves-path`` or ``-sp`` - path to json file with preset wanted saves (default: GITROOT/saves.json)  
``--filtered-path`` or ``-fp`` - path to json file with preset wanted saves (default: GITROOT/saves.json)  
``--console-print`` or ``-pr`` - print out the output into the terminal (default: true)  
``--solve`` or ``-s`` - setting for how to output solve (minimal, unique, None) (default: minimal)  
``--tinyurl`` or ``-t`` - output the link with tinyurl if possible. If false, outputs fumen code (default: true)  
