import os
import datetime
import time
import unittest
import mock
from cleanup import (
    is_path_old,
    delete_path_check,
    all_files_old,
    delete_files,
    delete_dir,
    is_empty,
    clean_up_files
)

class FakeStatResponse(object):
    st_mtime = None

class Test_is_path_old(unittest.TestCase):
    def test_returns_false_for_relative_path(self):
        result = is_path_old('foo', None)
        self.assertEquals(False, result)

    def test_returns_false_for_nonexistant_path(self):
        result = is_path_old('/my/nonexistant/path', None)
        self.assertEquals(False, result)

    def test_raises_for_non_date(self):
        self.assertRaises(
            ValueError,
            is_path_old,
            os.path.abspath(__file__),
            None)

    def test_returns_false_for_young_files(self):
        # create a fake response with a young
        # modified timestamp of "now"
        fake_stat = FakeStatResponse()
        fake_stat.st_mtime = time.time()

        # create an older comparison date of yesterday
        old_comp_date = datetime.datetime.now() - datetime.timedelta(days=1)

        # set the fake response on os.stat
        with mock.patch('os.stat', return_value=fake_stat):
            result = is_path_old(os.path.abspath(__file__), old_comp_date)
            self.assertEquals(False, result)

    def test_returns_true_for_old_files(self):
        # create a fake response with a
        # modified timestamp of "now"
        fake_stat = FakeStatResponse()
        fake_stat.st_mtime = time.time()

        # create an younger comparison date of tomorrow
        young_comp_date = datetime.datetime.now() + datetime.timedelta(days=1)

        # set the fake response on os.stat
        with mock.patch('cleanup.os.stat', return_value=fake_stat):
            result = is_path_old(os.path.abspath(__file__), young_comp_date)
            self.assertEquals(True, result)


class Test_delete_path_check(unittest.TestCase):
    def test_returns_true_for_Y_input(self):
        with mock.patch('__builtin__.raw_input', return_value='Y'):
            result = delete_path_check('foo')
            self.assertEquals(True, result)

    def test_not_true_for_N_input(self):
        with mock.patch('__builtin__.raw_input', return_value='N'):
            result = delete_path_check('foo')
            self.assertNotEqual(True, result)

    def test_not_true_for_no_input(self):
        with mock.patch('__builtin__.raw_input', return_value=''):
            result = delete_path_check('foo')
            self.assertNotEqual(True, result)


class Test_all_files_old(unittest.TestCase):
    def test_returns_true_when_all_files_are_old(self):
        file_list = ['foo', 'bar', 'baz', 'boz', 'bur']
        with mock.patch('cleanup.is_path_old', side_effect=[True] * 5):
            result = all_files_old(file_list, None)
            self.assertEquals(True, result)

    def test_returns_false_for_young_files(self):
        file_list = ['foo', 'bar', 'baz', 'boz', 'bur']
        with mock.patch('cleanup.is_path_old', side_effect=[False] * 5):
            result = all_files_old(file_list, None)
            self.assertEquals(False, result)

    def test_returns_false_for_a_mix_of_young_and_old_files(self):
        file_list = ['foo', 'bar', 'baz', 'boz', 'bur']
        results = [True, False, True, False, True]
        with mock.patch('cleanup.is_path_old', side_effect=results):
            result = all_files_old(file_list, None)
            self.assertEquals(False, result)


class Test_delete_files(unittest.TestCase):
    def test_nothing_is_deleted_for_empty_list_of_paths(self):
        with mock.patch('cleanup.os.remove') as remove:
            delete_files([])
            self.assertEquals(0, remove.call_count)

    def test_delete_is_called_for_list_of_paths(self):
        with mock.patch('cleanup.os.remove') as remove:
            with mock.patch('cleanup.delete_path_check', return_value=True) as dpc:
                delete_files(['foo', 'bar', 'baz'])
                self.assertEquals(3, remove.call_count)
                self.assertEquals(3, dpc.call_count)

    def test_deletes_when_force_is_true(self):
        with mock.patch('cleanup.os.remove') as remove:
            with mock.patch('cleanup.delete_path_check') as dpc:
                delete_files(['foo', 'bar', 'baz'], True)
                self.assertEquals(3, remove.call_count)
                self.assertEquals(0, dpc.call_count)

    def test_does_not_delete_when_delete_path_check_is_not_true(self):
        with mock.patch('cleanup.os.remove') as remove:
            with mock.patch('cleanup.delete_path_check', return_value=None) as dpc:
                delete_files(['foo', 'bar', 'baz'])
                self.assertEquals(0, remove.call_count)
                self.assertEquals(3, dpc.call_count)


class Test_delete_dir(unittest.TestCase):
    def test_does_not_delete_when_delete_path_check_is_not_true(self):
        with mock.patch('cleanup.os.rmdir') as rmdir:
            with mock.patch('cleanup.delete_path_check', return_value=None) as dpc:
                delete_dir('foo')
                self.assertEquals(0, rmdir.call_count)
                self.assertEquals(1, dpc.call_count)

    def test_deletes_when_force_is_true(self):
        with mock.patch('cleanup.os.rmdir') as rmdir:
            with mock.patch('cleanup.delete_path_check') as dpc:
                delete_dir('foo', True)
                self.assertEquals(1, rmdir.call_count)
                self.assertEquals(0, dpc.call_count)

    def test_deletes_when_delete_path_check_is_true(self):
        with mock.patch('cleanup.os.rmdir') as rmdir:
            with mock.patch('cleanup.delete_path_check', return_value=True) as dpc:
                delete_dir('foo')
                self.assertEquals(1, rmdir.call_count)
                self.assertEquals(1, dpc.call_count)


class Test_is_empty(unittest.TestCase):
    def test_return_false_for_invalid_path(self):
        result = is_empty('')
        self.assertEquals(False, result)

    def test_return_true_for_valid_dir_when_empty(self):
        with mock.patch('cleanup.os.listdir', return_value=[]) as listdir:
            result = is_empty(os.path.dirname(__file__))
            self.assertEquals(True, result)

    def test_return_false_for_valid_dir_when_not_empty(self):
        result = is_empty(os.path.dirname(__file__))
        self.assertEquals(False, result)


class Test_clean_up_files(unittest.TestCase):
    @mock.patch('cleanup.is_path_old', return_value=True)
    @mock.patch('cleanup.is_empty', return_value=True)
    @mock.patch('cleanup.delete_dir')
    @mock.patch('cleanup.delete_files')
    def test_delete_files_is_called_when_old_files_are_found(self, df, dd, ie, ipo):
        with mock.patch('cleanup.os.walk') as walk:
            walk.return_value = [['/my/test/path', [], ['foo']]]
            clean_up_files('/my/test/path', None)
            self.assertEquals(1, walk.call_count)
            self.assertEquals(2, ipo.call_count)
            self.assertEquals(1, df.call_count)
            self.assertEquals(1, ie.call_count)
            self.assertEquals(1, dd.call_count)

    @mock.patch('cleanup.is_path_old', return_value=False)
    @mock.patch('cleanup.is_empty', return_value=False)
    @mock.patch('cleanup.delete_dir')
    @mock.patch('cleanup.delete_files')
    def test_delete_files_is_not_called_when_new_files_are_found(self, df, dd, ie, ipo):
        with mock.patch('cleanup.os.walk') as walk:
            walk.return_value = [['/my/test/path', [], ['foo']]]
            clean_up_files('/my/test/path', None)
            self.assertEquals(1, walk.call_count)
            self.assertEquals(1, ipo.call_count)
            self.assertEquals(0, df.call_count)
            self.assertEquals(0, ie.call_count)
            self.assertEquals(0, dd.call_count)

    @mock.patch('cleanup.is_path_old', return_value=True)
    @mock.patch('cleanup.is_empty', return_value=False)
    @mock.patch('cleanup.delete_dir')
    @mock.patch('cleanup.delete_files')
    def test_delete_dir_is_not_called_when_not_empty(self, df, dd, ie, ipo):
        with mock.patch('cleanup.os.walk') as walk:
            walk.return_value = [['/my/test/path', [], ['foo']]]
            clean_up_files('/my/test/path', None)
            self.assertEquals(1, walk.call_count)
            self.assertEquals(1, ipo.call_count)
            self.assertEquals(1, df.call_count)
            self.assertEquals(1, ie.call_count)
            self.assertEquals(0, dd.call_count)


if __name__ == '__main__':
    unittest.main()
