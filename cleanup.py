"""
cleanup files and empty directories which are older than N days.

Description:
  A script which, when executed, will run through a path
  removing files and empty directories older than 'N' days.

Usage:
  cleanup <path> [--days=<days>] [--force] [--dryrun]
  cleanup --help

Options:
  -d <days>, --days <days>  the age of the files in days [default: 1]
  -f, --force               force deletion without asking [default: False]
  -D, --dryrun              do not perform delete operations [default: False]
  -h, --help                show description and usage
"""

import argparse
import contextlib
import datetime
import mock
import os
import sys
from docopt import docopt

def is_path_old(path, comparison_date):
    """
    Returns true if `path` is an absolute path, exists and is older than
    `comparison_date`.
    """
    if os.path.isabs(path) == False:
        return False
    if os.path.exists(path) == False:
        return False
    if not isinstance(comparison_date, datetime.datetime):
        raise ValueError('comparison_date should be of type datetime.datetime')
    st = os.stat(path)
    mtime = st.st_mtime
    last_modified = datetime.datetime.fromtimestamp(mtime)
    # return False if the last_modified timestamps
    # is newer than the comparison_date
    if last_modified > comparison_date:
        return False
    return True


def delete_path_check(path):
    """
    Check whether to delete file when force argument has not been entered
    or is False.
    """
    prompt = "Do you want to delete: %s ? y/N " % path
    list_check = get_input(prompt).upper()
    if list_check == 'Y':
        return True
    print("%s has not been removed. "
          "Please run the command again if you want to "
          "remove the file path." % path)


def all_files_old(paths, comparison_date):
    """
    Check whether all 'paths' are older than 'comparison_date'.
    """
    return all([is_path_old(f, comparison_date) for f in paths])


def delete_files(paths, force=False):
    """
    Deletes 'paths' when 'force' returns True.
    """
    for path in paths:
        if force is True or delete_path_check(path):
            print("Deleting:", path)
            os.remove(path)


def delete_dir(dir_, force=False):
    """
    Deletes 'dir_' when 'force' returns True.
    """
    if force is True or delete_path_check(dir_):
        print("Deleting:", dir_)
        os.rmdir(dir_)


def is_empty(dir_):
    """
    Checks whether 'dir_' is a directory and is empty.
    """
    return os.path.isdir(dir_) and not os.listdir(dir_)


def get_input(prompt):
    """
    Assesses python version being used and gets user input using the
    appropriate function.
    """
    if sys.version_info[0] >= 3:
        result = input(prompt)
    else:
        result = raw_input(prompt)
    return str(result).strip()


@contextlib.contextmanager
def as_dryrun(dryrun=False):
    if dryrun:
        patched_remove = mock.patch('os.remove')
        patched_rmdir = mock.patch('os.rmdir')
        patched_remove.start()
        patched_rmdir.start()

    yield

    if dryrun:
        patched_remove.stop()
        patched_rmdir.stop()


def clean_up_files(path, comparison_date, force=False, dryrun=False):
    """
    Lists all the files contained within the 'path' and calls 'all_files_old'
    against the 'comparison_date' to see whether they should be deleted when
    'force' is True.
    """
    for dirpath, subdirs, filenames in os.walk(path, topdown=False):
        filenames = [os.path.join(dirpath, f) for f in filenames]
        if not all_files_old(filenames, comparison_date):
            print("Skipping %s, not empty." % dirpath)
            continue

        with as_dryrun(dryrun):
            delete_files(filenames, force)

        if is_empty(dirpath) and is_path_old(dirpath, comparison_date):
            with as_dryrun(dryrun):
                delete_dir(dirpath, force)
        else:
            print("%s is not empty or old enough." % dirpath)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.3')

    if not os.path.isabs(args['<path>']) or not os.path.exists(args['<path>']):
        """
        checks whether 'path' given is an absolute path and exists.
        """
        print('The file path %s does not exist.' % args['<path>'])
        raise SystemExit()

    now = datetime.datetime.now()
    days = datetime.timedelta(days=int(args['--days']))

    # do the bizniz
    clean_up_files(args['<path>'], now - days, args['--force'], args['--dryrun'])
