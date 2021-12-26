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

        for i in output.splitlines():

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

                elong_message = error['message']
                if span['expansion']['span']['suggested_replacement'] is not None:
                    elong_message += "\nsuggest: {}".format(span['expansion']['span']['suggested_replacement'])

                yield LintMatch(
                    line=span['expansion']['span']['line_start']-1,
                    end_line=span['expansion']['span']['line_end']-1,
                    message=elong_message,
                    col=span['expansion']['span']['column_start']-1,
                    end_col=span['expansion']['span']['column_end']-1,
                    error_type=error['level'],
                    code=code,
                    filename=span['expansion']['span']['file_name']
                )
                for child in error['children']:
                    if child['spans'] == []:
                        if child['code'] is not None:
                            code = child['code']
                        else:
                            code = ''
                        yield LintMatch(
                            line=span['line_start']-1,
                            end_line=span['line_end']-1,
                            message=child['message'],
                            col=span['column_start']-1,
                            end_col=span['column_end']-1,
                            error_type=child['level'],
                            code=code,
                            filename=span['file_name']
                        )
                        if span['expansion'] is not None:
                            yield LintMatch(
                                line=span['expansion']['span']['line_start']-1,
                                end_line=span['expansion']['span']['line_end']-1,
                                message=child['message'],
                                col=span['expansion']['span']['column_start']-1,
                                end_col=span['expansion']['span']['column_end']-1,
                                error_type=child['level'],
                                code=code,
                                filename=span['expansion']['span']['file_name']
                            )
            if error['children'] == []:
                continue
            for child in error['children']:
                if child['code'] is not None:
                    code = child['code']
                else:
                    code = ''
                if child['spans'] != []:
                    for cspan in child['spans']:
                        long_message = child['message']
                        if cspan['suggested_replacement'] is not None:
                            long_message += "\nsuggest: {}".format(cspan['suggested_replacement'])
                        yield LintMatch(
                            line=cspan['line_start']-1,
                            end_line=cspan['line_end']-1,
                            message=long_message,
                            col=cspan['column_start']-1,
                            end_col=cspan['column_end']-1,
                            error_type=child['level'],
                            code=code,
                            filename=cspan['file_name']
                        )
