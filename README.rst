A Python library for datetime operations optimized for **human
comprehension** and **operational clarity**. Built around a universal
timestamp format that prioritizes instant readability over technical
standards, dt-helper reduces cognitive load in production workflows
where time matters most. Complex datetime operations become naturally
composable through pure functions designed for reliability, debugging
ease, and cross-system compatibility.

The ``'%Y%m%d%H%M%S.%f'`` format for “UTC float strings” enables instant
visual parsing, lexicographic sorting, and cross-system compatibility
while remaining debugger-friendly. It is also a great “score” for values
in Redis sorted sets.

**Who benefits from dt-helper:** - DevOps engineers managing time-series
data across multiple systems - Data pipeline developers who need
predictable, fault-tolerant timestamp handling - Teams building CLI
tools and automation scripts that require human-readable time formats -
Developers working with Redis, APIs, and databases who want consistent
timestamp representation

**Core workflows it optimizes:** - Interactive timestamp validation and
conversion in REPLs - Time range queries for Redis sorted sets and
database operations - Log analysis and debugging with instantly readable
timestamps - Cross-system data integration where timestamp format
consistency matters

Tested for Python 3.5 - 3.13.

Install
-------

Install with ``pip``

::

   pip install dt-helper

Configuration
-------------

dt-helper uses a settings.ini file for configuration:

.. code:: ini

   [default]
   admin_timezone = America/Chicago
   admin_date_fmt = %a %m/%d/%Y %I:%M:%S %p

..

   On first use, the default settings.ini file is copied to
   ``~/.config/dt-helper/settings.ini``

QuickStart
----------

.. code:: python

   import dt_helper as dh

   # Generate human-readable timestamps
   now = dh.utc_now_float_string()
   print(now)  # '20231215142530.123456' - instantly readable

   # Convert to pretty formats
   pretty = dh.utc_float_to_pretty(now)
   print(pretty)  # 'Fri 12/15/2023 02:25:30 PM'  - admin_date_fmt from settings

   # Time arithmetic made simple
   five_minutes_ago = dh.utc_ago_float_string('5:minutes', now=now)
   print(five_minutes_ago)  # '20231215142030.123456'

   # Complex time range generation for database queries
   ranges = dh.get_time_ranges_and_args(
       start_ts='2023-12-01',
       end_ts='2023-12-15',
       tz='America/Chicago'
   )
   print(ranges)
   # {'start_ts=2023-12-01,end_ts=2023-12-15': (20231201060000.0, 20231215060000.0), 'start_ts=2023-12-01': (20231201060000.0, inf), 'end_ts=2023-12-15': (0, 20231215060000.0)}

**What you gain:** Timestamps that sort correctly lexicographically,
work seamlessly across Redis/databases/APIs, and remain human-readable
during production debugging.

API Overview
------------

Core Timestamp Generation
~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``utc_now_float_string(fmt=FLOAT_STRING_FMT)``** - Current UTC
   timestamp as human-readable string

   -  Returns: String timestamp like ‘20231215142530.123456’
   -  Internal calls: ``dt_to_float_string()``

-  **``get_utcnow()``** - Current UTC time as non-localized datetime
   object

   -  Returns: datetime object in UTC
   -  Internal calls: None

-  **``utc_now_localized()``** - Current UTC time as timezone-aware
   datetime object

   -  Returns: pytz-localized datetime object in UTC
   -  Internal calls: None

-  **``local_now_string(fmt=FLOAT_STRING_FMT)``** - Current local time
   as string

   -  ``fmt`` - strftime format (defaults to FLOAT_STRING_FMT)
   -  Returns: String timestamp in local timezone
   -  Internal calls: ``dt_to_float_string()``

Time Arithmetic and History
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``utc_ago_float_string(num_unit, now=None, fmt=FLOAT_STRING_FMT)``**
   - Timestamp from the past

   -  ``num_unit`` - String like ‘15:seconds’, ‘1.5:weeks’, ‘3:hours’
      ((se)conds, (mi)nutes, (ho)urs, (da)ys, (we)eks, hr, wk)
   -  ``now`` - Reference time (utc_float string or None for current
      time)
   -  ``fmt`` - Output format
   -  Returns: String timestamp or None if invalid input
   -  Internal calls: ``float_string_to_dt()``,
      ``dt_to_float_string()``, ``get_utcnow()``

-  **``days_ago(days=0, timezone="America/Chicago")``** - Start of day N
   days ago in timezone

   -  ``days`` - Number of days back (non-negative)
   -  ``timezone`` - Target timezone string
   -  Returns: UTC datetime object for start of specified day
   -  Internal calls: ``utc_now_localized()``

Format Conversion and Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``dt_to_float_string(dt, fmt=FLOAT_STRING_FMT)``** - Convert
   datetime to string

   -  ``dt`` - datetime object
   -  ``fmt`` - strftime format string
   -  Returns: Formatted timestamp string
   -  Internal calls: ``ih.from_string()``

-  **``float_string_to_dt(float_string, fmt=FLOAT_STRING_FMT)``** -
   Parse string to datetime

   -  ``float_string`` - Timestamp string (auto-adds .0 if no decimal)
   -  ``fmt`` - Expected format
   -  Returns: datetime object
   -  Internal calls: None

-  **``date_string_to_utc_float_string(date_string, timezone=None)``** -
   Flexible date parsing

   -  ``date_string`` - Date in format from ‘YYYY’ to ‘YYYY-MM-DD
      HH:MM:SS.f’
   -  ``timezone`` - Source timezone for localization
   -  Returns: UTC float string or None if unparseable
   -  Internal calls: ``dt_to_float_string()``

Human-Friendly Formatting
~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``utc_float_to_pretty(utc_float=None, fmt=None, timezone=None)``**
   - Format for human display

   -  ``utc_float`` - Timestamp string/float (uses current time if None)
   -  ``fmt`` - strftime format (uses admin settings if None)
   -  ``timezone`` - Target timezone (uses admin settings if None)
   -  Returns: Formatted string or original value if no format specified
   -  Internal calls: ``utc_now_float_string()``

-  **``get_timestamp_formatter_from_args(ts_fmt=None, ts_tz=None, admin_fmt=False)``**
   - Create formatter function

   -  ``ts_fmt`` - strftime format for output
   -  ``ts_tz`` - timezone for conversion
   -  ``admin_fmt`` - boolean to use admin settings from config
   -  Returns: Function that formats utc_float values
   -  Internal calls: ``utc_float_to_pretty()``

ISO and Standard Format Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``utc_now_iso()``** - Current time in ISO format

   -  Returns: ISO format string like ‘2023-12-15T14:25:30.123456’
   -  Internal calls: ``get_utcnow()``

-  **``utc_localized_from_iso_timestamp(date_string)``** - Parse ISO
   timestamp to UTC

   -  ``date_string`` - ISO format timestamp (timezone-aware or UTC
      assumed)
   -  Returns: UTC localized datetime object or None if invalid
   -  Internal calls: ``get_utcnow()``

Advanced Date Operations
~~~~~~~~~~~~~~~~~~~~~~~~

-  **``date_string_to_datetime(date_string, fmt='%Y-%m-%d', timezone=None)``**
   - Flexible date parsing

   -  ``date_string`` - Date string or datetime object (passthrough)
   -  ``fmt`` - Expected format (auto-handles fractional seconds)
   -  ``timezone`` - Target timezone for localization
   -  Returns: datetime object (localized if timezone specified)
   -  Internal calls: None

-  **``date_start_utc(date_string, fmt='%Y-%m-%d', timezone="America/Chicago")``**
   - Day start in UTC

   -  ``date_string`` - Date in specified format
   -  ``fmt`` - Date format string
   -  ``timezone`` - Source timezone
   -  Returns: UTC datetime for start of day
   -  Internal calls: ``date_string_to_datetime()``

Complex Time Range Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``get_time_ranges_and_args(**kwargs)``** - Generate time ranges for
   Redis ZRANGEBYSCORE, ZCOUNT and database queries; multiple values
   separated by ``, ; |``

   -  ``tz`` - timezone for timestamp interpretation
   -  ``now`` - reference time as float_string
   -  ``start`` - direct utc_float start value
   -  ``end`` - direct utc_float end value
   -  ``start_ts`` - timestamp strings (format YYYY to YYYY-MM-DD
      HH:MM:SS.f)
   -  ``end_ts`` - timestamp strings (format YYYY to YYYY-MM-DD
      HH:MM:SS.f)
   -  ``since`` - relative time strings (‘15:minutes’, ‘2:days’, etc.)
   -  ``until`` - relative time strings (‘15:minutes’, ‘2:days’, etc.)
   -  Returns: Dictionary with descriptive keys and (start_float,
      end_float) tuples
   -  Internal calls: ``utc_now_float_string()``,
      ``date_string_to_utc_float_string()``, ``utc_ago_float_string()``,
      ``ih.string_to_set()``
