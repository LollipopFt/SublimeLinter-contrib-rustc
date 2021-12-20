from SublimeLinter.lint import Linter, LintMatch, STREAM_STDERR  # or NodeLinter, PythonLinter, ComposerLinter, RubyLinter
import json

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
                long_message+="\n{}: {}".format(child['level'], child['message'])
            if error['code'] != None:
                code = error['code']['code']
            else:
                code = ''
            for i in error['spans']:
                if i['is_primary'] == True:
                    yield LintMatch(
                        line = i['line_start']-1,
                        end_line = i['line_end']-1,
                        message = long_message,
                        col = i['column_start']-1,
                        end_col = i['column_end']-1,
                        error_type = error['level'],
                        near = i['text'][0]['text'],
                        code = code,
                        filename = i['file_name']
                    )
                else:
                    continue