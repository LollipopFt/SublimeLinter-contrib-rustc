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
    def find_errors(self, output):
        for i in output.split('\n'):
            error = json.loads(i)
            long_message = error['message']
            for child in error['children']:
                long_message+="\n{}: {}".format(child['level'], child['message'])
            yield LintMatch(
                line = error['spans'][0]['line_start'],
                end_line = error['spans'][0]['line_end'],
                message = long_message,
                col = error['spans'][0]['column_start'],
                end_col = error['spans'][0]['column_end'],
                error_type = error['level'],
                near = error['spans'][0]['text'][0]['text'],
                code = error['code']['code'],
                filename = error['spans'][0]['file_name']
            )