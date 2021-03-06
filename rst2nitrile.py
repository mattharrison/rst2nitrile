#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008-2009 Matt Harrison
# Licensed under Apache License, Version 2.0 (current)
from __future__ import print_function
import os
import shutil
import sys

import docutils
import docutils.utils #hack around circ. dep in io (docutils.10)
from docutils import io, writers, nodes
from docutils.readers import standalone
from docutils.core import (Publisher, default_description, 
    default_usage)
from docutils.parsers.rst import Directive, directives, roles

import nitrile as nt

if sys.version_info[0] > 2:
    unicode = str


SECTIONS = ['part', 'chapter', 'section', 'subsection', 'subsubsection',
            'subsubsection'] #hack on end
DEFAULT_SECTION_IDX = 1
ADD_TITLE = False

class envvar(nodes.Inline, nodes.TextElement): pass
def ignore_role(role, rawtext, text, lineno, inliner,
                options={}, content=[]):
    return [envvar(rawtext, text)], []

# ignore sphinx stuff
for role in 'envvar,data,term,ref,func,class,meth,doc,attr,mod,paramref,exc'.split(','):
    roles.register_local_role(role, ignore_role)

class Ignore(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 200
    def run(self, *args, **kwargs):
        return []


for directive in 'autoclass,autodata,automodule,currentmodule,deprecated,function,seealso,toctree,module,autofunction,versionadded,versionchanged'.split(','):
    directives.register_directive(directive, Ignore)

    
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
            ('Add title',
             ['--add-title'],
             {'action': 'store_true',
              'default': False}),
            ('Do not use chapters',
             ['--no-chapters'],
             {'action': 'store_true',
              'default': False,
              'dest': 'no_chapters'}),
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
        if self.document.settings.no_chapters:
            global DEFAULT_SECTION_IDX
            DEFAULT_SECTION_IDX = 2
        if self.document.settings.add_title:
            global ADD_TITLE
            ADD_TITLE = True

        self.visitor = self.translator_class(self.document)
        self.document.walkabout(self.visitor)
        self.parts['whole'] = self.visitor.get_whole()
        self.output = self.parts['whole']
        self.parts['encoding'] = self.document.settings.output_encoding
        self.parts['version'] = docutils.__version__


MEMOIR_MAPPING = {
    'literal': (r'\texttt{', '}'),
    'strong': (r'\textbf{', '}'),
    'emphasis': (r'\emph{', '}'),
    'comment': ('%', '\n'),
    # 'note': ('\\begin{framewithtitle}{Note}\\noindent\n',
    #          '\n\\end{framewithtitle}\n'),
    #'note': ('\\begin{mdframed}[needspace=6em,frametitle={Note},backgroundcolor=litegreen,linewidth=0pt]\n',
    # 'note': ('\\begin{mdframed}[frametitle={Note},backgroundcolor=litegreen,linewidth=0pt]\n\\orphan ',
    #          '\\widow\n\\end{mdframed}\n'),
    'note': ('\\begin{mdframed}[needspace=6.5em,frametitle={Note},backgroundcolor=litegreen,linewidth=0pt]\n',
             '\n\\end{mdframed}\n'),
    'tip': ('\\begin{mdframed}[needspace=6.5em,frametitle={Tip},backgroundcolor=litegreen,linewidth=0pt]\n',
             '\n\\end{mdframed}\n'),
    'warning': ('\\begin{mdframed}[needspace=6.5em,frametitle={Warning},backgroundcolor=litegreen,linewidth=0pt]\n',
             '\n\\end{mdframed}\n'),
    'hint': ('\\begin{mdframed}[needspace=6.5em,frametitle={Hint},backgroundcolor=litegreen,linewidth=0pt]\n',
             '\n\\end{mdframed}\n'),

    # 'hint': ('\\begin{framewithtitle}{Hint}\\noindent\n',
    #          '\n\\end{framewithtitle}\n'),
    'sidebar': ('\\begin{framewithtitle}{Sidebar}\\noindent\n',
                '\n\\end{framewithtitle}\n'),
    'topic': ('\\begin{framewithtitle}{Topic}\\noindent\n',
              '\n\\end{framewithtitle}\n'),
    # 'warning': ('\\begin{framewithtitle}{Warning}\\noindent\n',
    #             '\n\\end{framewithtitle}\n'),
    # 'tip': ('\\begin{tip}\\noindent\n', '\\end{tip}\n'),
    'literal_block': ('\\needspace{1\\baselineskip} % reserve at least 1 lines, if there is not enough\n\n'+\
                      #'\\begin{lstlisting}[xleftmargin=2em]\n',
                      '\\begin{lstlisting}[xleftmargin=0em]\n',
                      '\n\\end{lstlisting}\n\n'),
    # requires verbments
    # 'literal_block': ('\\begin{pyglist}[bgcolor=gray]\n',
    #                   '\n\\end{pyglist}\n\n'),
    # minted version
    # 'literal_block': ('\\begin{minted}[frame=lines]\n',
    #                   '\n\\end{minted}\n\n'),
    'doctest_block': ('\\begin{lstlisting}[frame=none]\n',
                      '\n\\end{lstlisting}\n\n'),
    'table_code_old': (r'\begin{center}\begin{tabulary}{\textwidth}',
                       '\\end{{tabulary}}{}\\end{{center}}\n'),
    # the H in begin{figure} pins it "Here"
    # TODO figure out how to make table font small
    'table_code': (r'\begin{figure}[H]\centering \tiny \begin{tabulary}{\textwidth}',
                    '\\end{{tabulary}}{}\\end{{figure}}\n'),
    #'long_table_code': (r'\begin{longtable}', '{}\\end{{longtable}}\n')
    'long_table_code': (r'\begingroup \small \begin{longtable}',
                        '{}\\end{{longtable}}\\endgroup\n'),
    #'table_code2': (r'\centering\begin{tabulary}{\textwidth}',
    #               '{}\\end{{tabulary}}\n'),
    # <colspec colwidth="51"/><colspec colwidth="40"/>
    'colspec': (None, None),
    'thead': ('', '\n\\hline\n'),
    'tbody': ('', '\\hline\n'),
    'block_quote':('\\begin{quote}\n', '\n\\end{quote}\n\n'),
    'attribution':(r'\sourceatright{', '}'),
    'footnote':(r'\footnotetext', '}'),
    'target': (None, None),
    'field_list': (None, None),
    'field': (None, None),
    'field_name': (None, None),
    'field_body': (None, None),
    'list_item': (r'  \item ', '\n'),
    'enumerated_list': ('\\begin{enumerate}\n', '\\end{enumerate}\n\n'),
    'bullet_list': ('\\begin{itemize}\n', '\\end{itemize}\n'),
    'definition_list': ('\\begin{description}', '\\end{description}\n'),
    'definition_list_item': (None, None),
    'definition': (None, None),
    'term': (r'\item[', '] '),
    'figure': ('\\begin{figure}\n', '\n\\end{figure}\n\n'),
    'caption': (r'\caption{', '}'),
    'legend': (r'\legend{', '}'),
    'subscript': (r'\textsubscript{', '}'),
    'superscript': (r'\textsuperscript{', '}'),
    'line_block': (None, None),
    'line': (None, '\\\\\n')
    
}

NOSTARCH_MAPPING = MEMOIR_MAPPING.copy()
NOSTARCH_MAPPING.update({
    'table':('\\begin{table}\n\\tbfont\n\\begin{tabulary}{\\textwidth}',
             '\\end{tabulary}\\end{table}\n'),
    'literal': (r'\lstinline{', '}'),
    'note': (r'\begin{note}', '\n\\end{note}\n'),
    'tip': (r'\begin{note}', '\n\\end{note}\n'),
    'hint': (r'\begin{note}', '\n\\end{note}\n'),
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
        self.in_latex_role = False
        self.non_supported = False
        self.old_table = None
        self.table_fmt = None

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
        self.in_node.setdefault(node.tagname, 0)
        name = node.tagname
        self.in_node[name] += 1
        if name in self.node_mapping:
            content = self.node_mapping[name][0]
            if self.at('title') and self.at('table'):
                self.table_caption += content
            elif content:
                self.raw(content)

        else:
            nodes.GenericNodeVisitor.dispatch_visit(self, node)

    def dispatch_departure(self, node):
        self.in_node[node.tagname] -= 1
        name = node.tagname
        if name in self.node_mapping:
            content = self.node_mapping[name][1]
            if self.at('title') and self.at('table'):
                self.table_caption += content
            elif content:
                self.raw(content)
        else:
            nodes.GenericNodeVisitor.dispatch_departure(self, node)

    def default_visit(self, node):
        if self.settings.report_level >= 3:
            print("ERR! NODE", node, node.tagname)
        if self.settings.report_level >= 1:
            print("NODE", str(node))
            print("PARENT", str(node.parent))
            print("GPARENT", str(node.parent.parent))
            print("GGPARENT", str(node.parent.parent.parent))
            pass
        raise NotImplementedError('node is %r, tag is %s' % (node, node.tagname))

    def default_departure(self, node):
        if self.settings.report_level >= 3:
            print("NODE", node, node.tagname)
        raise NotImplementedError('depart node is %r, tag is %s' % (node, node.tagname))

    def _dumb_visit(self, node):
        pass
    _dumb_depart = _dumb_visit

    def visit_index(self, node):
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
            pass

    def depart_index(self, node):
        pass

    def add_index(self, name):
        # sphinx mode - not really used
        self.raw(r'\index{')
        self.raw(name, escape=True)
        self.raw(r'}')

    visit_envvar = _dumb_visit
    depart_envvar = _dumb_visit

    visit_seealso = _dumb_visit
    depart_seealso = _dumb_visit


    def visit_document(self, node):
        self.raw(r'', escape=False)

    def depart_document(self, node):
        self.raw('\n\\end{document}')

    def visit_title(self, node):
        if ADD_TITLE:
            self.raw(r'\title{')
        # we need to skip main title,
        # preamble front matter should handle it
        if self.at('admonition'):
            self.raw('{')
        elif self.at('table'):
            # skip - handled in visit_Text
            pass
        elif not self.saw_title:
            pass
        elif self.section_level:
            self.doc += nt.Raw(r'{')

    def depart_title(self, node):
        if ADD_TITLE:
            self.raw('}')
        if self.at('admonition'):
            self.raw('}')
        elif self.at('table'):
            # skip
            pass
        elif not self.saw_title:
            pass
        elif self.section_level:
            self.doc += nt.Raw('}\n')
        self.saw_title = True

    def visit_table(self, node):
        self.table_caption = ''
        self.raw(self.node_mapping['table_code'][0])

    def depart_table(self, node):
        nstr = str(node)
        if 'Data types for' in nstr:
            print("TABLE", nstr)
        if self.table_caption:
            self.table_caption = '\\caption{{{}}}'.format(self.table_caption)
        self.raw(self.node_mapping['table_code'][1].format(self.table_caption))
        if self.old_table:
            self.node_mapping['table_code'] = self.old_table
            self.old_table = None

    def visit_Text(self, node):
        if self.at('index'):
            # using @ helps control sorting
            # http://en.wikibooks.org/wiki/LaTeX/Indexing#Controlling_sorting
            self.doc += nt.Raw(index_escape(node.astext()), escape=False)
        elif self.at('comment'):
            txt = node.astext()
            if txt.startswith('longtable:'):
                if not self.old_table:
                    self.old_table = self.node_mapping['table_code']
                # placeholder for caption on depart needs to be before end of longtable!
                self.node_mapping['table_code'] = self.node_mapping['long_table_code'] 
                # specify format with
                # .. longtable: format: { r l l p {.4\textwidth }}
                if 'format:' in txt:
                    self.table_fmt = txt.split('format:')[-1].strip()

        elif self.at('title') and self.at('table'):
            self.table_caption += nt.escape(node.astext())
        elif self.at('literal_block'):
            txt = nt.accent_escape(node.astext())
            self.doc += nt.Raw(txt, escape=False)
        elif self.at('reference'):
            # for url
            # import pdb;pdb.set_trace()
            # self.raw(r'{')
            self.raw(node.astext(), escape=True)
            #pass
        elif self.at('footnote'):
            self.doc += nt.Raw(node.astext(), escape=True)
        elif self.at('title') and not self.saw_title:
            pass
        elif self.in_latex_role:
            txt = node.astext()
            txt = txt.replace(u'Φ(x)', '\\phi(x)')
            self.doc += nt.Raw(txt, escape=False)
        elif self.non_supported:
            pass
        elif not self.at('raw'):
            # should be last
            self.doc += nt.Raw(node.astext(), escape=True)

    # def depart_Text(self, node):
    #     if self.at('reference'):
    #         # for url
    #         self.raw(r'}')
        
    depart_Text = _dumb_depart

    def visit_image(self, node):
        source_img = node.attributes['uri']
        scale = node.attributes.get('scale', None)
        width = node.attributes.get('width', '0.95')
        if '%' in width:
            width = '{:.2}'.format(int(width.replace('%', ''))/100.)
        def abspath(source_img, source_file):
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
        try:
            shutil.copy(full_path, out_path)
        except shutil.Error as e:
            if 'same file' in str(e):
                pass
            else:
                raise
        if scale:
            scale = '[scale={0}]'.format(str(float(scale)/100))
        else:
            scale = r'[width={}\textwidth,height=0.9\textheight,keepaspectratio]'.format(width)  # fixme
        self.raw('\\noindent\\makebox[\\textwidth]{%\n')
        self.raw(r'\includegraphics{0}{{'.format(scale) + source_img + '}')
#\includegraphics[width=\textwidth,height=\textheight,keepaspectratio]{myfig.png}

    def depart_image(self, node):
        self.raw('}\n\n') # newlines so paragrahps start after image, not inline

    def visit_paragraph(self, node):
        classes = node.attributes.get('classes', [])
        if self.at('index'):
            # TODO - I think paragraphs in index values messing up latex paragraph indentation
            # using @ helps control sorting
            # http://en.wikibooks.org/wiki/LaTeX/Indexing#Controlling_sorting
            self.raw(r'''\index{'''+ index_escape(node.astext()) + "@")
            self.fancy_index = True

    def depart_paragraph(self, node):
        if not self.at(['entry', 'index']):
            self.raw('\n\n')
        if self.at('index'):
            self.raw(r'}')
            self.fancy_index = False

    def visit_inline(self, node):
        classes = node.attributes.get('classes', [])

        for klass in classes:
            # fixme - add support for others!!!
            if klass in ['tiny']:
                self.raw('\\tiny{')
            if klass in ['latex']:
                # need to specify ".. role:: latex" in doc!
                self.in_latex_role = True
                txt = node.astext()

    def depart_inline(self, node):
        classes = node.attributes.get('classes', [])
        for klass in classes:
            if klass in ['tiny']:
                self.raw('}\\normalsize')
            if klass in ['latex']:
                self.in_latex_role = False

    def visit_raw(self, node):
        txt = node.astext()
        if node.attributes['format'] == 'latex':
            self.in_raw = True
            self.doc +=nt.Raw(txt, escape=False)
            self.doc +=nt.Raw('\n\n', escape=False)
        elif node.attributes['format'] == 'latexpreamble':
            self.in_raw = True
            self.doc.preamble += nt.Raw(txt, escape=False)
            self.doc.preamble += nt.Raw('\n\n', escape=False)
        else:
            self.non_supported = True

    def depart_raw(self, node):
        self.in_raw = False
        self.non_supported = False

    def visit_section(self, node):
        #print("SECTION node", node, "\n*****", self.section_level, SECTIONS)
        section = SECTIONS[DEFAULT_SECTION_IDX + self.section_level]
        self.raw('\\{0}'.format(section))  # title puts opening {
        self.section_level += 1

    def depart_section(self, node):
        self.raw('\n') # title puts closing {
        self.section_level -= 1

    def visit_reference(self, node):
        # \href{http://www.wikibooks.org}{Wikibooks home}

        if 'refid' in node:
            return #hack
        self.raw(r'\href{' + node['refuri'] + '}{')
        #self.raw(r'\url{' + node['refuri'] + '}')

    def depart_reference(self, node):
        #pass
        print("DEP REF", node)
        self.raw('}')

    def visit_title_reference(self, node):
        print("TR", node.parent)

    def depart_title_reference(self, node):
        pass

    def visit_tgroup(self, node):
        # justify columns
        self.num_cols = int(node['cols'])
        if self.table_fmt:
            self.raw(self.table_fmt + '\n')
            self.table_fmt = None
        elif self.old_table:
            self.raw('{ r ' + ' l'* (self.num_cols -2)  + ' p{.4\\textwidth} }\n')
        else:
            self.raw('{ R ' + ' L'* (self.num_cols -1)  + ' }\n')

    depart_tgroup = _dumb_depart

    def visit_row(self, node):
        self.cols_seen = 0

    def depart_row(self, node):
        self.raw(r' \\' + '\n')

    def visit_entry(self, node):
        if self.at('thead'):
            self.raw(r'\emph{')
        pass

    def depart_entry(self, node):
        if self.at('thead'):
            self.raw('}')
        if self.cols_seen < self.num_cols - 1:
            self.raw(' & ')  # keep track of
        self.cols_seen += 1

    def visit_label(self, node):
        self.raw('[')

    def depart_label(self, node):
        if self.at('footnote'):
            self.raw(']{')
        else:
            self.raw('{')

    def visit_footnote_reference(self, node):
        # hack to get rid of space required by rst
        self.doc -= ' '
        self.raw('\\footnotemark[')

    def depart_footnote_reference(self, node):
        self.raw(']')

    def visit_admonition(self, node):
        self.raw('\\begin{framewithtitle}')

    def depart_admonition(self, node):
        self.raw('\\end{framewithtitle}')

    def visit_term(self, node):

        """<definition_list><definition_list_item><term>An Item</term><definition><paragraph>The defintion for an item.</paragraph></definition></definition_list_item><definition_list_item><term>Second Item</term><definition><paragraph>The first paragraph for the second item.</paragraph><paragraph>Another paragraph for the item.</paragraph></definition></definition_list_item></definition_list> definition_list"""

    def raw(self, txt, escape=False):
        self.doc += nt.Raw(txt, escape)




def index_escape(txt):
    return txt.replace('!', '"!').replace('#', '"\#').replace('%', '\%').replace('_', '\_').replace('{', '\{').replace('}', '\}').replace('@', '"@').replace('&', r'\&').replace('^ ', r'\textasciicircum{}\enspace').replace('^', r'\textasciicircum{}').replace('~', r'\textasciitilde{}')


class BinaryFileOutput(io.FileOutput):
    """
    A version of docutils.io.FileOutput which writes to a binary file.
    """
    def open(self):
        try:
            print("DEST", self.destination_path)
            self.destination = open(self.destination_path, 'wb')
        except IOError as error:
            raise
            if not self.handle_io_errors:
                raise
            sys.stderr.write('%s: %s' % (error.__class__.__name__,
                                            error))
            sys.stderr.write('Unable to open destination file for writing '
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
