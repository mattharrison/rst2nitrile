#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008-2009 Matt Harrison
# Licensed under Apache License, Version 2.0 (current)
import sys
import os

import docutils
import docutils.utils #hack around circ. dep in io (docutils.10)
from docutils import io, writers, nodes
from docutils.readers import standalone
from docutils.core import Publisher, default_description, \
    default_usage
from docutils.parsers import rst
from docutils.parsers.rst import Directive, directives

import nitrile as nt

SECTIONS = ['part', 'chapter', 'section', 'subsection', 'subsubsection']
DEFAULT_SECTION_IDX = 1

from docutils import nodes
class envvar(nodes.Inline, nodes.TextElement): pass
def ignore_role(role, rawtext, text, lineno, inliner,
                       options={}, content=[]):
    return [envvar(rawtext, text)],[]
from docutils.parsers.rst import roles
roles.register_local_role('envvar', ignore_role)


class Index(Directive):
    """
    Directive to add entries to the index.
    """
    #has_content = False
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}
    count = 0

    def run(self):
        text = ''.join(self.content)
        # Create the admonition node, to be populated by `nested_parse`.
        index_node = index(rawsource=text)
        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset,
            index_node)
        targetid = 'index-%s' % Index.count
        Index.count += 1
        target_node = nodes.target('', '', ids=[targetid])
        index_node['entries'] = ne = []
        index_node['inline'] = False
        if self.arguments:
            arguments = self.arguments[0].split('\n')
            for entry in arguments:
                ne.extend(process_index_entry(entry, targetid))
        return [index_node, target_node]

    def run_old(self):
        #return [] #None #ignore for now
        # see sphinx.directives.other.Index for hints
        arguments = self.arguments[0].split('\n')
        targetid = 'index-%s' % Index.count
        Index.count += 1
        targetnode = nodes.target('', '', ids=[targetid])
        self.state.document.note_explicit_target(targetnode)
        indexnode = index()
        indexnode['entries'] = ne = []
        indexnode['inline'] = False
        for entry in arguments:
            ne.extend(process_index_entry(entry, targetid))
        return [indexnode, targetnode]

indextypes = [
    'single', 'pair', 'double', 'triple', 'see', 'seealso',
]

def process_index_entry(entry, targetid):
    indexentries = []
    entry = entry.strip()
    oentry = entry
    main = ''
    if entry.startswith('!'):
        main = 'main'
        entry = entry[1:].lstrip()
    for type in pairindextypes:
        if entry.startswith(type+':'):
            value = entry[len(type)+1:].strip()
            value = pairindextypes[type] + '; ' + value
            indexentries.append(('pair', value, targetid, main))
            break
    else:
        for type in indextypes:
            if entry.startswith(type+':'):
                value = entry[len(type)+1:].strip()
                if type == 'double':
                    type = 'pair'
                indexentries.append((type, value, targetid, main))
                break
        # shorthand notation for single entries
        else:
            for value in oentry.split(','):
                value = value.strip()
                main = ''
                if value.startswith('!'):
                    main = 'main'
                    value = value[1:].lstrip()
                if not value:
                    continue
                indexentries.append(('single', value, targetid, main))
    return indexentries
pairindextypes = {
    'module':    ('module'),
    'keyword':   ('keyword'),
    'operator':  ('operator'),
    'object':    ('object'),
    'exception': ('exception'),
    'statement': ('statement'),
    'builtin':   ('built-in function'),
}
class index(nodes.Invisible, nodes.Inline, nodes.TextElement):
    """Node for index entries.

    This node is created by the ``index`` directive and has one attribute,
    ``entries``.  Its value is a list of 4-tuples of ``(entrytype, entryname,
    target, ignored)``.

    *entrytype* is one of "single", "pair", "double", "triple".
    """


class Parser(docutils.parsers.rst.Parser):
    def __init__(self):
        #directives.register_directive('contents', Contents)
        directives.register_directive('index', Index)
        docutils.parsers.rst.Parser.__init__(self)

class Writer(writers.Writer):
    settings_spec = (
        'NiTrile/LaTex Specific Options', # option group title
        None, # Description
        ( # options (help string, list of options, dictions of OptionParser.add_option dicts)
            ('Specify a template (.otp) to use for styling',
             ['--template-file'],
             {'action': 'store',
              'dest': 'template_file'}),
            ('Specify a monospace font to use ("Courier New" default)',
             ['--mono-font'],
             {'action': 'store',
              'dest': 'mono_font'}),
            ('Specify a normal font to use ("Arial" default)',
             ['--font'],
             {'action': 'store',
              'dest': 'font'}),
            ('Specify pages to export (2,3,9-10)',
             ['--pages-to-output'],
             {'action': 'store',
              'dest': 'pages_to_output'}),
            ('Specify a Pygments style (see pygmentize -L styles)',
             ['--pygments-style'],
             {'action': 'store',
              'dest': 'pygments_style'}),
            )
        )
    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = NitrileTranslator

    def translate(self):
        self.visitor = self.translator_class(self.document)
        self.document.walkabout(self.visitor)
        self.parts['whole'] = self.visitor.get_whole()
        self.output = self.parts['whole']
        self.parts['encoding'] = self.document.settings.output_encoding
        self.parts['version'] = docutils.__version__


MEMOIR_MAPPING = {
    #'literal': (r'\texttt{\detokenize{', '}}'),
    'literal': (r'\texttt{', '}'),
    #'note': (r'\begin{titledframe}[Note]{Note}','\n\\end{titledframe}\n'),
    'note': (r'\begin{framewithtitle}{Note}','\n\\end{framewithtitle}\n'),
    'hint': (r'\begin{framewithtitle}{Hint}','\n\\end{framewithtitle}\n'),
    'tip': (r'\begin{framewithtitle}{Tip}','\n\\end{framewithtitle}\n'),
    'literal_block':#('\\begin{lstlisting}[frame=none]\n',
    ('\\begin{lstlisting}\n',
                     '\n\\end{lstlisting}\n\n'),
    'doctest_block':('\\begin{lstlisting}[frame=none]\n',
                     '\n\\end{lstlisting}\n\n'),
    #'table':('\\begin{tabular*}{250pt}', '\\end{tabular*}\n'),
    #'table':('\\begin{tabular*}{\\textwidth}', '\\end{tabular*}\n'),
    'table':('\\begin{center}\\begin{tabulary}{\\textwidth}', '\\end{tabulary}\\end{center}\n'),
    'block_quote':('\\begin{quote}\n', '\n\\end{quote}\n\n'),
    #'attribution':('\\attrib{','}'),
    'attribution':('\\sourceatright{','}'),
    # 'footnote':('\\footnote','}'),
    'footnote':('\\footnotetext','}'),
    #'footnote_reference':('\\footnotemark[',']'),
    #'label':('',''),
    # #'footnote_reference':('\\footref{','}'),
    # #'footnote_reference':('',''),
    # #'label':('\\footref{','}'),
    # 'label':('[',']{'), # part of footnote
    'enumerated_list': ('\\begin{enumerate}\n', '\\end{enumerate}\n\n')

}

NOSTARCH_MAPPING = MEMOIR_MAPPING.copy()
NOSTARCH_MAPPING.update({
    'table':('\\begin{table}\n\\tbfont\n\\begin{tabulary}{\\textwidth}', '\\end{tabulary}\\end{table}\n'),
    'literal': (r'\lstinline{', '}'),
    #'literal': (r'\verb{', '}'),
    'note': (r'\begin{note}','\n\\end{note}\n'),
    'tip': (r'\begin{note}','\n\\end{note}\n'),
    'hint': (r'\begin{note}','\n\\end{note}\n'),
    'doctest_block':('\\begin{Code}\n',
                     '\n\\end{Code}\n\n'),
    # get rid of lines above/below code
    'literal_block':('\\begin{Code}[frame=none,framerule=0.25pt]\n',
                     '\n\\end{Code}\n\n'),
    })

class NitrileTranslator(nodes.GenericNodeVisitor):
    def __init__(self, document, mapping=None):
        nodes.GenericNodeVisitor.__init__(self, document)
        self.settings = document.settings
        self.doc = nt.Document()
        self.in_node = {} # map of tagname to True if we are in/under this
        self.section_level = 0
        self.saw_title = False  # only look at first title
        self.node_mapping = mapping if mapping else MEMOIR_MAPPING
        self.fancy_index = False
        #self.node_mapping = mapping if mapping else NOSTARCH_MAPPING

    def at(self, nodename):
        """
        shortcut for at/under this node
        """
        if isinstance(nodename, list):
            for name in nodename:
                if self.in_node.get(name, False):
                    return True
        else:
            return self.in_node.get(nodename, False)

    def get_whole(self):
        return unicode(self.doc)

    def dispatch_visit(self, node):
        # Easier just to throw nodes I'm in in a dict, than keeping
        # state for each one
        count = self.in_node.setdefault(node.tagname, 0)
        name = node.tagname
        self.in_node[name] += 1
        if name in self.node_mapping:
            self.raw(self.node_mapping[name][0])
        else:
            nodes.GenericNodeVisitor.dispatch_visit(self, node)

    def dispatch_departure(self, node):
        self.in_node[node.tagname] -= 1
        name = node.tagname
        if name in self.node_mapping:
            self.raw(self.node_mapping[name][1])
        else:
            nodes.GenericNodeVisitor.dispatch_departure(self, node)

    def default_visit(self, node):
        if self.settings.report_level >= 3:
            print "ERR! NODE", node, node.tagname
        print "NODE", str(node)
        raise NotImplementedError('node is %r, tag is %s' % (node, node.tagname))

    def default_departure(self, node):
        if self.settings.report_level >= 3:
            print "NODE", node, node.tagname
        raise NotImplementedError('depart node is %r, tag is %s' % (node, node.tagname))


    def _dumb_visit(self, node):
        pass
    _dumb_depart = _dumb_visit

    def visit_index(self, node):
        print "INDEX", node
        # import pdb; pdb.set_trace() # FIXME
        entries = node.attributes['entries']
        if entries:
            #sphinx mode
            for entry in entries:
                etype, values, _, _ = entry
                if etype == 'pair':
                    pairs = [x.strip() for x in values.split(';')]
                    self.add_index(', '.join(pairs))
                    self.add_index(', '.join(pairs[::-1]))
                else:
                    self.add_index(values)
        else:
            # handle in paragraphs
            # I want formatted index entries, sphinx doesn't :(
            # self.fancy_index = True
            # self.raw(r'''\index{''')#documentclass[10pt]{memoir}
            pass
        print "FANCY", self.fancy_index

    def depart_index(self, node):
        print "DI!"
        if self.fancy_index:
            # self.raw(r'''}''')
            # self.fancy_index=False
            pass

    def add_index(self, name):
        self.raw(r'''\index{''')#documentclass[10pt]{memoir}
        self.raw(name, escape=True)
        self.raw(r'''}''')

    visit_envvar = _dumb_visit
    depart_envvar = _dumb_visit

    def visit_document(self, node):
        self.raw(r'', escape=False)

    def depart_document(self, node):
        self.raw('\n\\end{document}')

    def visit_title(self, node):
        # we need to skip main title,
        # preamble front matter should handle it
        if not self.saw_title:
            print "TITLEF", node
            pass
            #self.doc += nt.Raw(r'\title{')
        elif self.section_level:
            self.doc += nt.Raw(r'{')

    def depart_title(self, node):
        if not self.saw_title:
            pass
            #self.doc += nt.Raw('}\n')
        elif self.section_level:
            self.doc += nt.Raw('}\n')
        self.saw_title = True

    def visit_Text(self, node):
        if self.at('literal_block'):
            self.doc += nt.Raw(node.astext(), escape=False)

        # elif self.at('literal'):
        #     self.doc += nt.Raw(node.astext(), escape=False)
        # elif self.at('footnote_reference'):
        #     pass
        elif self.at('footnote'):
            print "NODE foot", node
            self.doc += nt.Raw(node.astext(), escape=True)
        elif self.at('title'):
            import pdb; pdb.set_trace() # FIXME
        elif not self.at('raw'):
            # should be last
            self.doc += nt.Raw(node.astext(), escape=True)




    depart_Text = _dumb_depart

    def visit_literal(self, node):
        self.raw(r'\texttt{\detokenize{', False)

    def depart_literal(self, node):
        self.raw('}}')

    def visit_comment(self, node):
        self.raw('%')

    def depart_comment(self, node):
        self.raw('\n')

    def visit_image(self, node):
        print "IMG", node
        source_img = node.attributes['uri']
        scale = node.attributes.get('scale', None)
        def abspath(source_img, source_file):
            # return abspath
            return os.path.abspath(os.path.join(os.path.dirname(source_file), source_img))
        full_path = abspath(source_img, self.settings._source)
        self.doc.add_image(source_img, full_path)
        out_path = abspath(source_img, self.settings._destination)
        try:
            os.makedirs(os.path.dirname(out_path))
        except OSError as e:
            if "File exists" in str(e):
                pass
            else:
                raise
        import shutil
        shutil.copy(full_path, out_path)
        if scale:
            scale = '[scale={0}]'.format(str(float(scale)/100))
        else:
            scale = ''
        self.raw(r'''\includegraphics{0}{{'''.format(scale) + source_img + '''}
''')
  #       self.raw(r'''\begin{figure}[h!]
  # \caption{A picture of a gull.}
  # \centering
  #   \includegraphics[width=0.5\textwidth]{''') # filename



    def depart_image(self, node):
        pass
#         self.raw(r'''}
# \end{figure}''')

    def visit_paragraph(self, node):
        classes = node.attributes.get('classes', [])
        if self.at('index'):
            # using @ helps control sorting
            # http://en.wikibooks.org/wiki/LaTeX/Indexing#Controlling_sorting
            self.raw(r'''\index{'''+ node.astext().replace('!', '"!') + "@")
            self.fancy_index = True

    def depart_paragraph(self, node):
        if not self.at(['entry', 'index']):
            self.raw('\n\n')
        if self.at('index'):
            self.raw(r'''}''')
            self.fancy_index = False

    def visit_inline(self, node):
        classes = node.attributes.get('classes', [])
        for klass in classes:
            # fxxme!!!
            if klass in ['tiny']:
                self.raw('\\tiny{')

    def depart_inline(self, node):
        classes = node.attributes.get('classes', [])
        for klass in classes:
            if klass in ['tiny']:
                self.raw('}\\normalsize')

    def visit_raw(self, node):
        if node.attributes['format'] == 'latex':
            self.in_raw = True
            self.doc +=nt.Raw(node.astext(), escape=False)
            self.doc +=nt.Raw('\n\n', escape=False)
        elif node.attributes['format'] == 'latexpreamble':
            self.in_raw = True
            self.doc.preamble.__iadd__( nt.Raw(node.astext(), escape=False))
            self.doc.preamble.__iadd__(nt.Raw('\n\n', escape=False))

    # visit_raw = _dumb_visit
    def depart_raw(self, node):
        self.in_raw = False

    def visit_section(self, node):
        section = SECTIONS[DEFAULT_SECTION_IDX + self.section_level]
        self.raw('\\{0}'.format(section))  # title puts opening {
        self.section_level += 1


    def depart_section(self, node):
        #self.raw('}\n')
        self.raw('\n') # title puts closing {
        self.section_level -= 1

    def visit_literal_block(self, node):
        #self.raw('\\begin{verbatim}\n')
        self.raw('\\begin{lstlisting}[frame=single]\n')

    def depart_literal_block(self, node):
        #self.raw('\n\\end{verbatim}\n\n')
        self.raw('\n\\end{lstlisting}\n\n')

    def visit_emphasis(self, node):
        self.raw('\\emph{')

    def depart_emphasis(self, node):
        self.raw('}')

    def visit_strong(self, node):
        self.raw('\\textbf{')
    def depart_strong(self, node):
        self.raw('}')

    def visit_reference(self, node):
        # \href{http://www.wikibooks.org}{Wikibooks home}
        self.raw('\\href{' + node['refuri'] + '}{')

    def depart_reference(self, node):
        self.raw('}')

    def visit_bullet_list(self, node):
        self.raw('\\begin{itemize}\n')

    def depart_bullet_list(self, node):
        self.raw('\\end{itemize}\n')

    def visit_list_item(self, node):
        self.raw('  \\item ')

    def depart_list_item(self, node):
        self.raw('\n')

    def visit_table(self, node):
        print "NODE", str(node)
#         \begin{tabular}{ l c r }
#   1 & 2 & 3 \\
#   4 & 5 & 6 \\
#   7 & 8 & 9 \\
# \end{tabular}
        self.raw('\\begin{tabular}')  # justify columns

    def depart_table(self, node):
        self.raw('\\end{tabular}\n')

    def visit_tgroup(self, node):
        # justify columns
        self.num_cols = int(node['cols'])
        #self.raw('{ r ' + ' l'* (self.num_cols -1)  + ' }\n')
        self.raw('{ R ' + ' L'* (self.num_cols -1)  + ' }\n')

    depart_tgroup = _dumb_depart

    def visit_colspec(self, node):
        # <colspec colwidth="51"/><colspec colwidth="40"/>

        pass
    depart_colspec = _dumb_depart

    def visit_thead(self, node):
        # <thead><row><entry><paragraph>Method signature</paragraph></entry><entry><paragraph>Explanation</paragraph></entry><
        pass

    def depart_thead(self, node):
        self.raw('\n\\hline\n')

    def visit_row(self, node):
        self.cols_seen = 0

    def depart_row(self, node):
        self.raw(' \\\\\n')

    def visit_entry(self, node):
        if self.at('thead'):
            self.raw('\\emph{')
        pass

    def depart_entry(self, node):
        if self.at('thead'):
            self.raw('}')
        if self.cols_seen < self.num_cols - 1:
            self.raw(' & ')  # keep track of
        self.cols_seen += 1

    def visit_tbody(self, node):
        pass

    def depart_tbody(self, node):
        # final horiz line
        self.raw('\\hline\n')

    def visit_target(self, node):
        # handle???
        pass

    depart_target = _dumb_depart

    def visit_note(self, node):
        #self.raw(r'\subsubsection{')
        #self.raw(r'\sidebar{')  # memoir specific
        self.raw(r'\begin{framed}')
    def depart_note(self, node):
        #self.raw('}\n')
        self.raw('\n\\end{framed}\n')

    visit_tip = visit_note
    depart_tip = depart_note

    def visit_field_list(self, node):
        # see rst2epub
        pass


    def visit_footnote(self, node):
        print "FOOT", node
        print "ATT", node.attributes
        self.raw('\\footnote{')

    def depart_footnote(self, node):
        self.raw('}')

    def visit_label(self, node):
        self.raw('[')
    def depart_label(self, node):
        if self.at('footnote'):
            self.raw(']{')
        else:
            self.raw('{')
    def visit_footnote_reference(self, node):
        print "FR", node
        # hack to get rid of space required by rst
        self.doc -= ' '
        self.raw('\\footnotemark[')

        #'footnote_reference':('\\footnotemark[',']'),
        #'footnote_reference':('\\footref{','}'),

    def depart_footnote_reference(self, node):
        self.raw(']')
    #visit_problematic = _dumb_depart
    #depart_problematic = _dumb_depart
    depart_field_list = visit_field_list
    visit_field = visit_field_list
    depart_field = visit_field_list
    visit_field_name = visit_field_list
    depart_field_name = visit_field_list
    visit_field_body = visit_field_list
    depart_field_body = visit_field_list

    def raw(self, txt, escape=False):
        self.doc += nt.Raw(txt, escape)

class BinaryFileOutput(io.FileOutput):
    """
    A version of docutils.io.FileOutput which writes to a binary file.
    """
    def open(self):
        try:
            self.destination = open(self.destination_path, 'wb')

        except IOError, error:
            if not self.handle_io_errors:
                raise
            print >>sys.stderr, '%s: %s' % (error.__class__.__name__,
                                            error)
            print >>sys.stderr, ('Unable to open destination file for writing '
                                 '(%r).  Exiting.' % self.destination_path)
            sys.exit(1)
        self.opened = 1


def main(prog_args):
    argv = None
    reader = standalone.Reader()
    reader_name = 'standalone'
    writer = Writer()
    writer_name = 'NiTrile'
    parser = Parser()
    parser_name = 'restructuredtext'
    settings = None
    settings_spec = None
    settings_overrides = None
    config_section = None
    enable_exit_status = 1
    usage = default_usage
    publisher = Publisher(reader, parser, writer, settings,
                          destination_class=BinaryFileOutput)
    publisher.set_components(reader_name, parser_name, writer_name)
    description = ('Generates NiTrile/LaTex slides from '
                   'standalone reStructuredText sources.  ' + default_description)

    output = publisher.publish(argv, usage, description,
                               settings_spec, settings_overrides,
                               config_section=config_section,
                               enable_exit_status=enable_exit_status)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    #if sys.version_info >= (2, 7):
    #    raise SystemExit("Error: rst2odp is not currently compatible with python 2.7 or newer")
    if '--doctest' in sys.argv:
        _test()
    else:
        sys.exit(main(sys.argv) or 0)
