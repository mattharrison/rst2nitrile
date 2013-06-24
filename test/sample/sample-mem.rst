.. include:: <s5defs.txt>

======================================================
Example ``rst2epub2.py`` Book
======================================================

.. raw:: latexpreamble

  \documentclass[10pt]{memoir}
  \checkandfixthelayout
  \usepackage[paperwidth=4.25in, paperheight=6.875in,bindingoffset=.75in]{geometry}
  % need markboth for header to appear correctly
  % better hyphenation, etc
  \usepackage[activate={true,nocompatibility},protrusion=true,expansion=true]{microtype}
  % Set a trade-size page.
  \setstocksize{9in}{6in}
  \settrimmedsize{\stockheight}{\stockwidth}{*}
  \setulmarginsandblock{0.75in}{0.75in}{*}
  \setlrmarginsandblock{0.8in}{0.55in}{*}
  \setheaderspaces{0.5in}{*}{*}
  \checkandfixthelayout

  % graphics!
  \usepackage{graphicx}

  % get the copyright character working
  \usepackage[utf8]{inputenc}

  % yes we want an index
  \usepackage{makeidx}
  \makeindex

  \usepackage{tgpagella}

  % dropped caps
  \usepackage{type1cm}
  \usepackage{lettrine}

  % don't print trivial gripes
  \hbadness = 5000

  % avoid widows, orphans
  \clubpenalty=10000
  \widowpenalty=10000
  \raggedbottom

  % clickable hyperlinks
  \usepackage[linktocpage=true]{hyperref}



  \usepackage{tabulary}

  % fix for footnote symbols
  % see http://tex.stackexchange.com/questions/826/symbols-instead-of-numbers-as-footnote-markers
  \renewcommand*{\thefootnote}{\fnsymbol{footnote}}
  \usepackage{perpage}
  \MakePerPage{footnote}

  % change font

  % code formatting
  \usepackage{listings}
  \usepackage{color}
  \definecolor{litegreen}{rgb}{0.9,0.9,0.8}
  \definecolor{mygreen}{rgb}{0,0.6,0}
  \lstset{ %
   %backgroundcolor=\color{litegreen},
    basicstyle=\ttfamily\footnotesize,        % the size of the fonts that are used for the code
    %framesep=20pt, % padding in box
    %frame=bt, %single,
   % numbers=left,
    xleftmargin=\parindent,
    % from http://www.bradleymedia.org/latex-formatting/
    aboveskip=10pt,
    belowskip=5pt,
  %    backgroundcolor=\color{grey}
  }

  % get the copyright character working
  \usepackage[utf8]{inputenc}


  %\usepackage{tgpagella}

  % dropped caps
  %\usepackage{type1cm}
  %\usepackage{lettrine}

  % don't print trivial gripes
  \hbadness = 5000

  % avoid widows, orphans
  \clubpenalty=10000
  \widowpenalty=10000
  \raggedbottom

  \usepackage{listings}

  % clickable hyperlinks
  \usepackage[linktocpage=true]{hyperref}



  \newenvironment{dedicationpage}{%
  \clearpage
   {\pagestyle{empty}\cleardoublepage}%
   \thispagestyle{empty}%
   \null\vskip1.175in%
   \centering\normalfont}


  \newcommand{\FrameTitle}[2]{%
  \fboxrule=\FrameRule \fboxsep=\FrameSep
  \fbox{\vbox{\nobreak \vskip -0.7\FrameSep
  \rlap{\strut#1}\nobreak\nointerlineskip% left justified
  \vskip 0.7\FrameSep
  \hbox{#2}}}}
  \newenvironment{framewithtitle}[2][\FrameFirst@Lab\ (cont.)]{%
  \def\FrameFirst@Lab{\textbf{#2}}%
  \def\FrameCont@Lab{\textbf{#1}}%
  \def\FrameCommand##1{%
  \FrameTitle{\FrameFirst@Lab}{##1}}%
  \def\FirstFrameCommand##1{%
  \FrameTitle{\FrameFirst@Lab}{##1}}%
  \def\MidFrameCommand##1{%
  \FrameTitle{\FrameCont@Lab}{##1}}%
  \def\LastFrameCommand##1{%
  \FrameTitle{\FrameCont@Lab}{##1}}%
  \MakeFramed{\advance\hsize-\width \FrameRestore}}%
  {\endMakeFramed}

  % OLD FRAME BELOW puts title on both pages

   \newcommand{\TitleFrame}[2]{%
  \fboxrule=\FrameRule \fboxsep=\FrameSep
  \vbox{\nobreak \vskip -0.7\FrameSep
  \rlap{\strut#1}\nobreak\nointerlineskip% left justified
  \vskip 0.7\FrameSep
  \noindent\fbox{#2}}}
  \newenvironment{titledframe}[2][\FrameFirst@Lab\ (cont.)]{%
  \def\FrameFirst@Lab{\textbf{#2}}%
  \def\FrameCont@Lab{\textbf{#1}}%
  \def\FrameCommand##1{%
  \TitleFrame{\FrameFirst@Lab}{##1}}
  \def\FirstFrameCommand##1{%
  \TitleFrame{\FrameFirst@Lab}{##1}}
  \def\MidFrameCommand##1{%
  \TitleFrame{\FrameCont@Lab}{##1}}
  \def\LastFrameCommand##1{%
  \TitleFrame{\FrameCont@Lab}{##1}}
  \MakeFramed{\hsize\textwidth
  \advance\hsize -2\FrameRule
  \advance\hsize -2\FrameSep
  \FrameRestore}}%
  {\endMakeFramed}

  \newcommand{\halftitle}[2]{%
  % half title page
    \pagestyle{empty}
    \begin{center}
    \huge{\title}
    \end{center}
    \clearpage
  }

  % no starch press stuff

   \usepackage{booktabs}
   \usepackage{caption}

   % hack around fancy header error
   \let\footruleskip\undefined
   \usepackage{fancyhdr}% http://ctan.org/pkg/fancyhdr
   \usepackage{fancyvrb}
   \usepackage{graphics}
   \usepackage{ifpdf}
   \usepackage{listings}
   \usepackage{ragged2e}
   \usepackage{upquote}

  % need tip and hint

  \newenvironment{hint}{%
    \list{\makebox[0pt][r]{\fontfamily{%
            \dgdefault}\fontseries{b}\fontsize{9pt}{11pt}\selectfont
          HINT\hspace{2em}}}{\listparindent0pt\relax
      \topsep9\p@\relax
      \itemindent0\p@\relax
      \rightmargin0\p@\relax
      \leftmargin0\p@\relax
      \labelwidth0\p@\relax
      \labelsep0\p@}%
      \item\itshape}{\vspace{-3pt}\endlist}

  \newenvironment{tip}{%
    \list{\makebox[0pt][r]{\fontfamily{%
    \dgdefault}\fontseries{b}\fontsize{9pt}{11pt}\selectfont
    TIP\hspace{2em}}}{\listparindent0pt\relax
    \topsep9\p@\relax
    \itemindent0\p@\relax
    \rightmargin0\p@\relax
    \leftmargin0\p@\relax
    \labelwidth0\p@\relax
    \labelsep0\p@}%
    \item\itshape}{\vspace{-3pt}\endlist}




  \title{Treading On Python Volume 1}
  %\subtitle{Beginning Python}
  \author{Matt Harrison}
  \date{June 2013}
  %\nostarchlocation{Utah}
  %\chapterstyle{bringhurst}



  \begin{document}

.. raw:: latex

  \frontmatter
  %   \makehalftitle
  \halftitle
  \begin{titlingpage}
  \maketitle
  \end{titlingpage}
  \null\vfill
  \begin{flushleft}
  \textit{\title}
  COPYRIGHT INFO

  ISBN--INFO

  ISBN--13:
  \bigskip
  ALL RIGHTS RESERVED OR COPYRIGHT LICENSE LANGUAGE
  \end{flushleft}
  \let\cleardoublepage\clearpage
  \begin{copyrightpage}

*Matt Harrison*
Copyright 2013

While every precaution has been taken in the preparation of this book,
the publisher and author assumes no responsibility for errors or
omissions, or for damages resulting from the use of the
information contained herein.

.. raw:: latex

  %
  \end{copyrightpage}
  \clearpage
  \tableofcontents
  % \dedicationpage
  \mainmatter
  \chapter*{Forward}
  Sample forward non-chpater




.. The table of contents will be created by the comment below

.. toc:show

Using ``rst`` for Books
=========================

.. this is the first chapter

Using rst is easy, open your favorite text editor and start
typing. Paragraphs look like you think they would.

Lists are pretty easy too. If you type a list like this::

  * Apples
  * Bannanas
  * Kiwi

You'll get this:

* Apples
* Bannanas
* Kiwi

.. need to import s5defs for following:

Normal sized text.

:tiny:`Some tiny text` (can also do ``small``, ``big``, or ``huge``)

Some *strong text* and **emphasized text**

Here is a `hyperlinked text <http://www.yahoo.com/>`_.

.. index::
  single: lorum


Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
molestie venenatis varius. Nulla interdum porttitor erat at
adipiscing. Nulla arcu metus, porta vel vestibulum sit amet,
porttitor lobortis sapien. Donec tincidunt placerat imperdiet.

.. index::

  ``code item``
  *foo*

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
molestie venenatis varius. Nulla interdum porttitor erat at
adipiscing. Nulla arcu metus, porta vel vestibulum sit amet,
porttitor lobortis sapien. Donec tincidunt placerat imperdiet.

Images
=======

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
molestie venenatis varius. Nulla interdum porttitor erat at
adipiscing. Nulla arcu metus, porta vel vestibulum sit amet,
porttitor lobortis sapien. Donec tincidunt placerat imperdiet.

.. image:: matt.jpg
   :scale: 50%

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
molestie venenatis varius. Nulla interdum porttitor erat at
adipiscing. Nulla arcu metus, porta vel vestibulum sit amet,
porttitor lobortis sapien. Donec tincidunt placerat imperdiet.


Code example
============

Code can be listed like this::

  def foo(bar):
      # do something
      return bar + 1

Not bad!

Sidebar example
===============

Here is a side bar

.. note::

  This is a side bar, it should be formatted differently.

  It can contain code::

    def sidebar_func():
        pass

  Pretty nice!

Creating an epub
================

Run this command::

  PYTHONPATH=/path/to/rst2epub python path/to/rst2epub.py book.rst \
  output.epub

To create a kindle book run::

  kindlegen output.epub

This will create a mobi file in the same directory as the epub

Assorted Code
=================

The following is a quote:

  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
  molestie venenatis varius. Nulla interdum porttitor erat at
  adipiscing. Nulla arcu metus, porta vel vestibulum sit amet,
  porttitor lobortis sapien. Donec tincidunt placerat imperdiet. Nulla
  Sample endnote [#]_. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
  molestie venenatis varius. Nulla interdum porttitor erat at
  adipiscing. Nulla arcu metus, porta vel vestibulum sit amet,
  porttitor lobortis sapien. Donec tincidunt placerat imperdiet. Nulla


.. [#] `www.python.org <www.python.org>`_

Here's another endnote [#]_.

.. [#] this endnote just has text

Another footnote using symbols [*]_.

.. [*] Only in version 2.7

Yet Another footnote using symbols [*]_.

.. [*] Only in version 2.8

Yet Another footnote using symbols [*]_.

.. [*] Only in version 2.9


Tables
=========


  ================ =================
  Escape Sequence  Output
  ================ =================
  ``\\``              Backslash
  ``\'``              Single quote
  ``\"``              Double quote
  ``\b``              ASCII Backspace
  ``\n``              Newline
  ``\t``              Tab
  ``\u12af``          Unicode 16 bit
  ``\U12af89bc``      Unicode 32 bit
  ``\o84``            Octal character
  ``\xFF``            Hex character
  ================ =================


.. note::

  Table in a note

  ================ =================
  Escape Sequence  Output
  ================ =================
  ``\\``              Backslash
  ``\'``              Single quote
  ``\"``              Double quote
  ``\b``              ASCII Backspace
  ``\n``              Newline
  ``\t``              Tab
  ``\u12af``          Unicode 16 bit
  ``\U12af89bc``      Unicode 32 bit
  ``\o84``            Octal character
  ``\xFF``            Hex character
  ================ =================


  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
  molestie venenatis varius. Nulla interdum porttitor erat at
  adipiscing. Nulla arcu metus, porta vel vestibulum sit amet,
  porttitor lobortis sapien. Donec tincidunt placerat imperdiet. Nulla
  congue consectetur magna, nec commodo nunc mattis at. Suspendisse
  aliquet sapien in ligula dictum nec adipiscing est
  pellentesque. Aliquam scelerisque nisl ac ipsum dictum porta.

  Quisque viverra mi sed justo mattis tincidunt pretium neque
  imperdiet. Maecenas quis velit mi. Maecenas mattis tempor
  vestibulum. Aenean ipsum nisi, interdum a iaculis sit amet, vehicula
  at nibh. Ut in odio et lectus fringilla volutpat. Fusce et malesuada
  mauris. Ut vitae tellus tortor, gravida sagittis odio. Vestibulum eu
  turpis orci, nec commodo ipsum. Curabitur sed mi arcu, sed tristique
  ante. Vestibulum posuere ullamcorper mauris a condimentum. Ut sapien
  ante, consequat eu ultricies faucibus, vehicula et arcu. Mauris
  viverra quam nec justo molestie id tempor nunc commodo. Suspendisse
  nisi magna, faucibus in mattis sollicitudin, convallis non
  risus. Duis a accumsan dolor. Vestibulum id laoreet est. Quisque
  posuere dictum sodales.

  Quisque sed lorem erat. Phasellus ac ligula odio, nec tincidunt
  augue. Fusce in eros lectus, et accumsan dui. In at mi eget ligula
  auctor scelerisque. Proin elementum elit ut quam aliquam
  feugiat. Nullam quis quam ac tortor faucibus sollicitudin et eu
  lectus. Proin malesuada turpis varius enim vulputate congue. Duis
  vestibulum velit et tortor adipiscing ac malesuada lorem
  varius. Suspendisse potenti. Vestibulum ac lectus non enim ornare
  porta.

More content in raw Latex.

.. raw:: latex

  \backmatter
  \part{END}

  \chapter*{About the author}

.. .. image:: matt.jpg

Matt Harrison wrote this because he wasn't satisfied with any of the existing LaTex converters.


.. raw:: latex

  \cleardoublepage
  \printindex
