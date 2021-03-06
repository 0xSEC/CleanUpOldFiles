# Clean up old files

[![Build Status](https://travis-ci.org/0xSEC/CleanUpOldFiles.svg?branch=master)](https://travis-ci.org/0xSEC/CleanUpOldFiles)

This is a script which allows you to delete files and empty directories which are older than *N* days.

## Usage

To use, call the script as such:

    python cleanup.py <path> [--days=<days>] [--force] [--dryrun]

### Options

    -d <days>, --days <days>  the age of the files in days [default: 1]
    -f, --force               force deletion without asking [default: False]
    -D, --dryrun              do not perform delete operations [default: False]
    -h, --help                show description and usage

## Notes

I used this as an exercise to help me learn python in general and also unit testing.

Code reviews, comments, and pull requests are all very welcome.
