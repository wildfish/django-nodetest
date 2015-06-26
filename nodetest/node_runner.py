from django.conf import settings
import subprocess
import tempfile
import sys


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
