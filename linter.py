from SublimeLinter.lint import Linter  # or NodeLinter, PythonLinter, ComposerLinter, RubyLinter


class Rustc(Linter):
    cmd = ('rustc', '--error-format=json', '${file}')
    regex = r'''^{"message":"(?P<message>(?!could not emit MIR).*)","code":{"code":"(?P<code>.*)","explanation":.*},"level":"(?P<error_type>.*?)","spans":\[{.*"line_start":(?P<line>[0-9]+),"line_end":(?P<end_line>[0-9]+),"column_start":(?P<col>[0-9]+),"column_end":(?P<end_col>[0-9]+),.*"text":\[{"text":"(?P<near>.*)","highlight_start".*$'''
    multiline = True
    defaults = {
        'selector': 'source.rust'
    }
    on_stderr = None
    name = 'rustc'