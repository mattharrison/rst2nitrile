REQs
--------

* Install nitrile.py (see github)

run::

  $ python rst2nitrile.py -r 3 --traceback book.rst build/book.tex
  $ pushd build

then::

  $ rubber -d pdf book.tex;

or::

  $ pdflatex book

create index and shove it in::

  $ makeindex book
  $ rubber -d pdf book.tex;
  $ popd


TODO
--------

* Make ``.. include:: <s5defs.txt>`` not dump ``==========`` all over the place
* index support for ``#!``
* Cleanup
