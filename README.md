humpy
=====

Python Manipulation of Humdrum Kern Files

```
from humpy.kernscore import KernScore

x = KernScore()
x.import_kernfile('chorales/bwv0377.krn')

x.cadences
x.export_midi('blat.mid')
```
