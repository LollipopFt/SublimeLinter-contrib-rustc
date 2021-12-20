import json
from SublimeLinter.lint import Linter, LintMatch, STREAM_STDERR  # or NodeLinter, PythonLinter, ComposerLinter, RubyLinter


class Rustc(Linter):
    cmd = ('rustc', '--error-format=json', '--emit=mir', '-o', '/dev/null', '${file}')
    defaults = {
        'selector': 'source.rust'
    }
    error_stream = STREAM_STDERR
    name = 'rustc'
    on_stderr = None

    def find_errors(self, output):

        for i in output.split('\n'):

            try:
                error = json.loads(i)
            except ValueError:
                continue

            if error['spans'] == []:
                continue

            long_message = error['message']
            for child in error['children']:
                long_message += "\n{}: {}".format(child['level'], child['message'])

            if error['code'] is not None:
                code = error['code']['code']
            else:
                code = ''

            for span in error['spans']:

                def linenumber(num):
                    if num == 1:
                        return 1
                    return num-1

                if span['file_name'] == self.context.get('file'):

                    if span['suggested_replacement'] is not None:
                        long_message += "\nsuggest: {}".format(span['suggested_replacement'])

                    yield LintMatch(
                        line=linenumber(span['line_start']),
                        end_line=linenumber(span['line_end']),
                        message=long_message,
                        col=linenumber(span['column_start']),
                        end_col=linenumber(span['column_end']-1),
                        error_type=error['level'],
                        near=span['text'][0]['text'],
                        code=code,
                        filename=span['file_name']
                    )
                else:
                    continue
