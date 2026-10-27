"""Local credentials stay out of argv, user-visible errors, and implicit imports."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from local_config import load_local_configuration

class LocalConfigurationTests(unittest.TestCase):
    def write(self,folder,text,mode=0o600):
        path=Path(folder)/'.env.local';path.write_text(text);path.chmod(mode);return path
    def test_valid_local_configuration_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict('os.environ',{'NEBIUS_API_KEY':'existing-environment'},clear=True):
            path=self.write(folder,"NEBIUS_API_KEY='local-test-value'\nNEBIUS_MODEL=nvidia/test\n")
            self.assertTrue(load_local_configuration(path))
            self.assertEqual(os.environ['NEBIUS_API_KEY'],'existing-environment')
            self.assertEqual(os.environ['NEBIUS_MODEL'],'nvidia/test')
    def test_missing_file_is_not_a_failure(self):
        with tempfile.TemporaryDirectory() as folder:self.assertFalse(load_local_configuration(Path(folder)/'absent'))
    def test_unsafe_permissions_rejected_without_exposing_key(self):
        with tempfile.TemporaryDirectory() as folder:
            path=self.write(folder,'NEBIUS_API_KEY=private-test-value\nNEBIUS_MODEL=nvidia/test\n',0o644)
            with self.assertRaises(ValueError) as result:load_local_configuration(path)
            self.assertNotIn('private-test-value',str(result.exception))
    def test_incomplete_configuration_is_not_partially_applied(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict('os.environ',{},clear=True):
            path=self.write(folder,'NEBIUS_API_KEY=test\nUNKNOWN=value\n')
            with self.assertRaises(ValueError):load_local_configuration(path)
            self.assertNotIn('NEBIUS_API_KEY',os.environ)
    def test_symlink_not_followed(self):
        if not hasattr(os,'O_NOFOLLOW'):self.skipTest('OS has no no-follow file flag')
        with tempfile.TemporaryDirectory() as folder:
            target=self.write(folder,'NEBIUS_API_KEY=test\nNEBIUS_MODEL=nvidia/test\n')
            link=Path(folder)/'link';link.symlink_to(target)
            with self.assertRaises(OSError):load_local_configuration(link)
    def test_shell_substitution_is_not_executed(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict('os.environ',{},clear=True):
            path=self.write(folder,"NEBIUS_API_KEY='$(not-a-command)'\nNEBIUS_MODEL=nvidia/test\n")
            load_local_configuration(path)
            self.assertEqual(os.environ['NEBIUS_API_KEY'],'$(not-a-command)')
