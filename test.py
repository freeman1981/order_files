from collector import process_dir, process_files
from unittest.mock import patch

DIR = 'dir_for_test'


@patch('collector.process_files')
def test_process_dir(mock_process_files):
    process_dir(path=DIR, cursor=None, connection=None)
    pass


def test_process_dir_2(monkeypatch):
    monkeypatch.setattr(process_files)
    process_dir(path=DIR, cursor=None, connection=None)
