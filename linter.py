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

        def recurse(parsed_json):

            if parsed_json['spans'] == []:
                return

            long_message = parsed_json['message']
            if parsed_json['children'] != []:
                for child in parsed_json['children']:
                    long_message += "\n{}: {}".format(child['level'], child['message'])
                    recurse(child)

            if parsed_json['code'] is not None:
                code = parsed_json['code']['code']
            else:
                code = ''

            for span in parsed_json['spans']:

                if span['suggested_replacement'] is not None:
                    long_message += "\nsuggest: {}".format(span['suggested_replacement'])

                yield LintMatch(
                    line=span['line_start']-1,
                    end_line=span['line_end']-1,
                    message=long_message,
                    col=span['column_start']-1,
                    end_col=span['column_end']-1,
                    error_type=parsed_json['level'],
                    code=code,
                    filename=span['file_name']
                )

        for i in output.split('\n'):

            try:
                error = json.loads(i)
                recurse(error)
            except ValueError:
                continue
            except TypeError:
                continue
