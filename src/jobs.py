import asyncio
import subprocess
import os
import logs

# COMMAND_LATEX = \
# "pdflatex -disable-pipes -disable-installer -disable-write18 -no-shell-escape -interaction=nonstopmode -output-directory={pdir} {fname}"

COMMAND_LATEX = \
"pdflatex -no-shell-escape -interaction=nonstopmode -output-directory={pdir} {fname}"

COMMAND_IMG_CONVERT = "convert -trim -density 200 -quality 85 {pdf} {dest}"


def mkdir(p):
    if not os.path.exists(p):
        os.makedirs(p)


async def run_command_async(command, timeout = 3):
    INTERVAL = 0.25
    if isinstance(command, str):
        command = command.split(' ')
    process = subprocess.Popen(command)
    for i in range(int(timeout / INTERVAL)):
        await asyncio.sleep(INTERVAL)
        retcode = process.poll()
        if retcode is not None:
            break
    if retcode is None:
        process.kill()
        raise subprocess.TimeoutExpired(command, timeout, process.stdout, process.stderr)
    if retcode == 0:
        return str(process.stdout)
    raise subprocess.CalledProcessError(retcode, command, process.stdout, process.stderr)


async def render_latex(job_id, output_format, code):
    try:
        pdir = './temp/' + job_id + '/'
        mkdir(pdir)
        fname = pdir + 'a.tex'
        latex_log = ''
        with open(fname, 'wt') as f:
            f.write(code)
            f.flush()
            f.close()
        try:
            try:
                output = await run_command_async(
                    COMMAND_LATEX.format(pdir = pdir, fname = fname),
                    timeout = 8
                )
            finally:
                log_file = fname.replace('.tex', '.log')
                try:
                    latex_log = open(log_file, encoding = 'utf-8').read()
                except FileNotFoundError:
                    pass
        except subprocess.TimeoutExpired as e:
            return {
                'status': 'error',
                'description': 'Time limit exceeded during latex rendering'
            }
        except subprocess.CalledProcessError as e:
            # NOTE: Sometimes a pdf file can still be produced.
            # Maybe we should let the caller access it anyway?
            return {
                'status': 'error',
                'description': 'pdflatex exited with non-zero return code',
                'log': latex_log
            }
        pdf_file = fname.replace('.tex', '.pdf')
        if output_format == 'pdf':
            try:
                # Binary so as to avoid encoding errors
                with open(pdf_file, 'rb') as f:
                    pass
            except FileNotFoundError:
                return {
                    'status': 'error',
                    'description': 'pdflatex produced no output',
                    'log': latex_log
                }
            return {
                'status': 'success',
                # 'filename': pdf_file,
                'log': latex_log
            }
        elif output_format in ('png', 'jpg'):
            img_file = pdf_file.replace('.pdf', '.' + output_format)
            try:
                output = await run_command_async(
                    COMMAND_IMG_CONVERT.format(pdf = pdf_file, dest = img_file),
                    timeout = 3
                )
                # If there are multiple pages, need to make sure we get the first one
                # A later version of the API will allow for accessing the rest of the
                # pages. This is more of a temporary bug fix than anything.
                multipaged = img_file.replace('.', '-0.')
                if os.path.isfile(multipaged):
                    os.rename(multipaged, img_file)
            except subprocess.TimeoutExpired:
                return {
                    'status': 'error',
                    'description': 'Time limit exceeded during image conversion',
                }
            except subprocess.CalledProcessError as proc:
                return {
                    'status': 'error',
                    'description': 'Image conversion exited with non-zero return code'
                }
            return {
                'status': 'success',
                # 'filename': img_file,
                'log': latex_log
            }
        return {
            'status': 'error',
            'description': 'Output format was invalid'
        }
    except Exception as e:
        logs.error(e)
        return {
            'status': 'error',
            'description': 'The server broke. This is bad.'
            # 'details': repr(e)
        }
