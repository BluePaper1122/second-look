import contextlib
import getpass
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from setup_nebius import main

class SetupTests(unittest.TestCase):
    def test_key_saved_with_private_permissions_but_never_printed(self):
        with tempfile.TemporaryDirectory() as folder,patch('setup_nebius.ROOT',Path(folder)),patch('setup_nebius.getpass.getpass',return_value='fake-private-key'),patch('builtins.input',return_value='nvidia/test'),contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(),0)
            file=Path(folder)/'.env.local'
            self.assertEqual(file.stat().st_mode&0o777,0o600)
            self.assertIn('fake-private-key',file.read_text())
            self.assertNotIn('fake-private-key',output.getvalue())
    def test_hidden_entry_unavailable_does_not_fall_back_to_echo(self):
        with tempfile.TemporaryDirectory() as folder,patch('setup_nebius.ROOT',Path(folder)),patch('setup_nebius.getpass.getpass',side_effect=getpass.GetPassWarning('unavailable')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(),1)
            self.assertFalse((Path(folder)/'.env.local').exists())
    def test_cancellation_saves_nothing(self):
        with tempfile.TemporaryDirectory() as folder,patch('setup_nebius.ROOT',Path(folder)),patch('setup_nebius.getpass.getpass',side_effect=KeyboardInterrupt()),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(),1)
            self.assertFalse((Path(folder)/'.env.local').exists())
    def test_declining_replacement_preserves_existing_configuration(self):
        with tempfile.TemporaryDirectory() as folder,patch('setup_nebius.ROOT',Path(folder)),patch('builtins.input',return_value='n'),patch('setup_nebius.getpass.getpass') as reader,contextlib.redirect_stdout(io.StringIO()):
            file=Path(folder)/'.env.local';file.write_text('existing')
            self.assertEqual(main(),1)
            self.assertEqual(file.read_text(),'existing')
            reader.assert_not_called()
    def test_atomic_replace_failure_leaves_no_secret_temporary_file(self):
        with tempfile.TemporaryDirectory() as folder,patch('setup_nebius.ROOT',Path(folder)),patch('setup_nebius.getpass.getpass',return_value='fake-private-key'),patch('builtins.input',return_value='nvidia/test'),patch('setup_nebius.os.replace',side_effect=OSError()),contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(),1)
            self.assertEqual(list(Path(folder).iterdir()),[])
            self.assertNotIn('fake-private-key',output.getvalue())
