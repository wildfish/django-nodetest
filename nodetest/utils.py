from os.path import join
from uuid import uuid4
from shutil import copyfile


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


def _make_temp_name(js_src):
    return '{}/__{}.js'.format(
        js_src.rsplit('/', 1)[0],
        uuid4().hex
    )


def make_temp_file(root_dir, js_src):
    temp_name = _make_temp_name(js_src)
    src = join(root_dir, js_src)
    dst = join(root_dir, temp_name)
    full_dest = copyfile(src, dst)
    return {
        'absolute_path': full_dest,
        'relative_path': temp_name
    }


def parse_repl(src):
    with open(src, 'r') as src_file:
        file_content = src_file.read()
        file_content = file_content.replace('/*REPL*/', _js_repl)

    with open(src, 'w') as src_file:
        src_file.write(file_content)

