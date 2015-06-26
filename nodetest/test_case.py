from django.conf import settings
from django.test import LiveServerTestCase
from os.path import abspath, dirname, join
from uuid import uuid4
from shutil import copyfile
from os.path import join
from os import remove
from .node_runner import run_node_script
import json


_js_repl = """;(function () {
    var repl = require('repl');
    var os = require('os');
    var empty = '(' + os.EOL + ')';
    repl.start({
        prompt: "NODE> ",
        eval: function (cmd, context, filename, callback) {
            if (cmd === ".scope") cmd = empty;
            if (cmd === empty) return callback();
            var result = eval(cmd);
            callback(null, result)
        }
    })
})();
"""

class JavaScriptException(Exception):
    pass


def _make_temp_name(js_src):
    return '{}/__{}.js'.format(
        js_src.rsplit('/', 1)[0],
        uuid4().hex
    )


def _make_temp_file(root_dir, js_src):
    temp_name = _make_temp_name(js_src)
    src = join(root_dir, js_src)
    dst = join(root_dir, temp_name)
    full_dest = copyfile(src, dst)
    return {
        'absolute_path': full_dest,
        'relative_path': temp_name
    }


def _parse_repl(src):
    with open(src, 'r') as src_file:
        file_content = src_file.read()
        file_content = file_content.replace('/*REPL*/', _js_repl)

    with open(src, 'w') as src_file:
        src_file.write(file_content)

def _get_script_root():
    assert hasattr(settings, 'NODETEST_SCRIPT_ROOT'), """Set "NODETEST_SCRIPT_ROOT" in settings, \ne.g: NODETEST_SCRIPT_ROOT = join(BASE_DIR, 'static', 'js')"""
    return settings.NODETEST_SCRIPT_ROOT


class NodeTestCase(LiveServerTestCase):
    def run_test_script(self, script_file, plaintext=False, enable_console=False):
        cwd = dirname(dirname(abspath(__file__)))
        js_dir = _get_script_root()
        copied_script_path = _make_temp_file(js_dir, script_file)

        # Only parse REPL if the console is enabled
        # or the script will hang waiting for input
        if enable_console:
            _parse_repl(copied_script_path['absolute_path'])

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
