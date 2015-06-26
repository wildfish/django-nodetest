from os import remove
from django.conf import settings
from .utils import make_temp_file, parse_repl
import subprocess
import tempfile
import sys
import json


class JavaScriptException(Exception):
    pass


def _get_script_root():
    assert hasattr(settings, 'NODETEST_SCRIPT_ROOT'), """Set "NODETEST_SCRIPT_ROOT" in settings, \ne.g: NODETEST_SCRIPT_ROOT = join(BASE_DIR, 'static', 'js')"""
    return settings.NODETEST_SCRIPT_ROOT


def process_script(script_file, plaintext=False, enable_console=False):
    js_dir = _get_script_root()
    copied_script_path = make_temp_file(js_dir, script_file)

    # Only parse REPL if the console is enabled
    # or the script will hang waiting for input
    if enable_console:
        parse_repl(copied_script_path['absolute_path'])

    try:
        err, out = run_node_script(
            js_dir,
            copied_script_path['relative_path'],
            enable_console
        )

        if err:
            err = '\n\n-------------- JAVASCRIPT EXCEPTION --------------\n{}'.format(err)
            raise JavaScriptException(err)

        if plaintext:
            return out.strip()

        if out == '':
            return {}

        return json.loads(out.strip())
    except Exception as ex:
        raise ex
    finally:
        remove(copied_script_path['absolute_path'])


def run_node_script(js_dir, script_path, enable_console=False):
    node_path = getattr(settings, 'NODETEST_NODE_BIN', 'node')

    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:

        # Enabling console means output is written to stdout.
        # this means no return values from the JavaScript code
        # but it makes it possible to enter the Node REPL
        if enable_console:
            stdout_file = sys.stdout

        # cmd = 'babel-node {}'.format(script_path)
        cmd = '{} {}'.format(node_path, script_path)
        popen = subprocess.Popen(cmd, stdout=stdout_file, stderr=stderr_file, shell=True, cwd=js_dir)
        popen.wait()

        stderr_file.seek(0)

        stderr = stderr_file.read()
        stderr = stderr.decode()

        if not enable_console:
            stdout_file.seek(0)
            stdout = stdout_file.read()
            stdout = stdout.decode()
        else:
            stdout = ''

        return stderr, stdout
