# Clean up old files

This is a script which allows you to delete files and empty directories which are older than *N* days.

## Usage

To use, call the script as such:

    python cleanup.py <path> [--days=<days>] [--force]

### Options

    -d <days>, --days <days>  the age of the files in days [default: 1]
    -f, --force               force deletion without asking [default: False]
    -h, --help                show description and usage

## Notes

I used this as an exercise to help me learn python in general and also unit testing.

Code reviews, comments, and pull requests are all very welcome.
