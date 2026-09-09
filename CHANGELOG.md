# Change Log
All enhancements and patches to Django Logtailer will be documented in this file.

## [2.0]
### Changed
- Require Django >= 6.1.1 and Python >= 3.12; adapt admin change form to the Django 6.1 admin layout
- **Breaking**: `LOGTAILER_ALLOWED_ROOTS` setting is mandatory; log files outside the configured directories are denied (path traversal protection, issue #22)
- **Breaking**: filter regexes are now Python regular expressions evaluated server-side with `re.search()`. Filters saved with previous versions were JavaScript regex literals and may no longer match: rewrite e.g. `/pattern/i` as `(?i)pattern`
- Log lines are HTML-escaped server-side before being sent to the browser (fixes stored XSS in the log window)
- Filtering happens server-side: only matching lines are sent to the client; the `eval()`-based client-side filter was removed
- Added test suite 

## [1.3]
### Changed
- Adding download log file link
- Making compatible with Django 5
- Remove jquery colorbox
- Adapt popup for save logs to new django admin dynamic color scheme


## [1.2]
### Changed
- Add form input field to define last lines to read from file
- Making compatible with Django 3

## [1.1]
### Changed
- Making compatible to Django 2.x
- Making compatible with Python 3.7
