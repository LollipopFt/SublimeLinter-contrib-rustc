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
                msg = error['message']
                if (span['suggested_replacement'] is not None) & (span['suggested_replacement'] != ""):
                    err_msg = msg+"\n{}: {}".format(span['suggestion_applicability'], span['suggested_replacement'])
                else:
                    err_msg = msg
                yield LintMatch(
                    line=span['line_start']-1,
                    end_line=span['line_end']-1,
                    message=err_msg,
                    col=span['column_start']-1,
                    end_col=span['column_end']-1,
                    error_type=error['level'],
                    code=code,
                    filename=span['file_name']
                )
                if span['expansion'] is not None:
                    spaness = span['expansion']['span']['suggested_replacement']
                    if (spaness is not None) & (spaness != ""):
                        span_err_msg = msg+"\n{}: {}".format(span['expansion']['span']['suggestion_applicability'], spaness)
                    else:
                        span_err_msg = msg
                    yield LintMatch(
                        line=span['expansion']['span']['line_start']-1,
                        end_line=span['expansion']['span']['line_end']-1,
                        message=span_err_msg,
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
                        cspans = cspan['suggested_replacement']
                        if (cspans is not None) & (cspans != ""):
                            long_message += "\n{}: {}".format(cspan['suggestion_applicability'], cspans)
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
