from django.test import LiveServerTestCase
from .node_runner import process_script


class NodeTestCase(LiveServerTestCase):
    def run_test_script(self, script_file, plaintext=False, enable_console=False):
        return process_script(script_file, plaintext, enable_console)
