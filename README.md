humpy
=====

Python Manipulation of Humdrum Kern Files

This is not a full-fledged project, just a bit of work in the right general
direction.

```
from humpy.kernscore import KernScore

x = KernScore()
x.import_kernfile('chorales/bwv0377.krn')

x.cadences
x.export_midi('blat.mid')
```
