import json
from SublimeLinter.lint import Linter, LintMatch, STREAM_STDERR


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

            if error['code'] is not None:
                code = error['code']['code']
            else:
                code = ''

            for span in error['spans']:

                long_message = error['message']

                for child in error['children']:
                    if child['spans'] == []:
                        long_message += "\n{}: {}".format(child['level'], child['message'])
                    else:
                        message = child['message']
                        message += "\nsuggest: {}".format(child['spans'][0]['suggested_replacement'])
                        yield LintMatch(
                            line=child['spans'][0]['line_start']-1,
                            end_line=child['spans'][0]['line_end']-1,
                            message=message,
                            col=child['spans'][0]['column_start']-1,
                            end_col=child['spans'][0]['column_end']-1,
                            error_type=child['level'],
                            filename=child['spans'][0]['file_name']
                        )

                if span['suggested_replacement'] is not None:
                    long_message += "\nsuggest: {}".format(span['suggested_replacement'])

                yield LintMatch(
                    line=span['line_start']-1,
                    end_line=span['line_end']-1,
                    message=long_message,
                    col=span['column_start']-1,
                    end_col=span['column_end']-1,
                    error_type=error['level'],
                    code=code,
                    filename=span['file_name']
                )