from SublimeLinter.lint import Linter, LintMatch, STREAM_STDERR  # or NodeLinter, PythonLinter, ComposerLinter, RubyLinter
import json

class Rustc(Linter):
    cmd = ('rustc', '--error-format=json', '${file}')
    defaults = {
        'selector': 'source.rust'
    }
    error_stream = STREAM_STDERR
    name = 'rustc'
    on_stderr = None
    def find_errors(self, output)
        error = [json.loads(i) for i in output]
        long_message = error['message']
        for child in error['children']:
            long_message+=("\n{}: {}".format(child['level'], child['message']))
        yield LintMatch(
            line = error['spans']['line_start'],
            end_line = error['spans']['line_end'],
            message = long_message,
            col = error['spans']['column_start'],
            end_col = error['spans']['column_end'],
            error_type = error['level'],
            near = error['text']['text'],
            code = error['code']['code'],
            filename = error['spans']['file_name']
        )