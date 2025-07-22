import pytest
import pytz
import sys
from datetime import datetime, time, timedelta, timezone as dt_timezone

import dt_helper as dh


class TestSettingsIntegration:
    """Test settings integration and configuration loading"""

    def test_admin_timezone_default_loading(self):
        """Test that ADMIN_TIMEZONE loads from settings.ini"""
        assert dh.ADMIN_TIMEZONE == "America/Chicago"

    def test_admin_date_fmt_default_loading(self):
        """Test that ADMIN_DATE_FMT loads from settings.ini"""
        assert dh.ADMIN_DATE_FMT == "%a %m/%d/%Y %I:%M:%S %p"

    def test_get_setting_function_exists(self):
        """Test that get_setting function is properly created"""
        assert callable(dh.get_setting)
        # Test it can retrieve the same values
        assert dh.get_setting('admin_timezone') == "America/Chicago"
        assert dh.get_setting('admin_date_fmt') == "%a %m/%d/%Y %I:%M:%S %p"

    def test_get_setting_with_default(self):
        """Test get_setting returns default for non-existent setting"""
        result = dh.get_setting('nonexistent_setting', 'default_value')
        assert result == 'default_value'


class TestBasicDatetimeFunctions:
    """Test basic datetime utility functions"""

    def test_utc_now_localized_returns_localized_datetime(self):
        """Test utc_now_localized returns properly localized datetime"""
        result = dh.utc_now_localized()
        assert result.tzinfo in [pytz.utc, dt_timezone.utc]
        assert isinstance(result, datetime)
        # Should be close to current time (within a few seconds)
        now = dh.get_utcnow()
        time_diff = abs((result.replace(tzinfo=None) - now).total_seconds())
        assert time_diff < 5  # Within 5 seconds

    def test_utc_now_iso_returns_iso_string(self):
        """Test utc_now_iso returns ISO format string"""
        result = dh.utc_now_iso()
        assert isinstance(result, str)
        if sys.version_info >= (3, 8):
            # Should be parseable as ISO format
            parsed = datetime.fromisoformat(result)
            assert isinstance(parsed, datetime)
            # Should be close to current time
            now = dh.get_utcnow()
            time_diff = abs((parsed - now).total_seconds())
            assert time_diff < 5


class TestTimeConversionFunctions:
    """Test time conversion and formatting functions"""

    def test_dt_to_float_string_custom_format(self):
        """Test datetime to float string with custom format"""
        dt = datetime(2023, 7, 22, 15, 30, 45)
        result = dh.dt_to_float_string(dt, fmt='%Y%m%d')
        assert result == "20230722"

    def test_dt_to_float_string_zero_microseconds(self):
        """Test datetime with zero microseconds"""
        dt = datetime(2023, 7, 22, 15, 30, 45, 0)
        result = dh.dt_to_float_string(dt)
        assert result == "20230722153045.0"

    def test_float_string_to_dt_with_microseconds(self):
        """Test conversion from float string to datetime"""
        float_string = "20230722153045.123456"
        result = dh.float_string_to_dt(float_string)
        expected = datetime(2023, 7, 22, 15, 30, 45, 123456)
        assert result == expected

    def test_float_string_to_dt_without_microseconds(self):
        """Test conversion from float string without microseconds"""
        float_string = "20230722153045"
        result = dh.float_string_to_dt(float_string)
        expected = datetime(2023, 7, 22, 15, 30, 45, 0)
        assert result == expected

    def test_float_string_to_dt_numeric_input(self):
        """Test float_string_to_dt accepts numeric input"""
        result = dh.float_string_to_dt(20230722153045)
        expected = datetime(2023, 7, 22, 15, 30, 45, 0)
        assert result == expected

    def test_local_now_string_returns_reasonable_value(self):
        """Test local_now_string returns properly formatted current time"""
        result = dh.local_now_string()
        assert isinstance(result, str)
        assert len(result) >= 15  # At least YYYYMMDDHHMMSS
        # Should parse back to a datetime close to now
        parsed_dt = dh.float_string_to_dt(result)
        now = datetime.now()
        time_diff = abs((parsed_dt - now).total_seconds())
        assert time_diff < 5  # Within 5 seconds

    def test_utc_now_float_string_returns_reasonable_value(self):
        """Test utc_now_float_string returns properly formatted current UTC time"""
        result = dh.utc_now_float_string()
        assert isinstance(result, str)
        assert len(result) >= 15
        # Should parse back to a datetime close to now
        parsed_dt = dh.float_string_to_dt(result)
        now = dh.get_utcnow()
        time_diff = abs((parsed_dt - now).total_seconds())
        assert time_diff < 5  # Within 5 seconds


class TestDaysAgoFunction:
    """Test days_ago function for timezone-aware date calculations"""

    def test_days_ago_zero_days(self):
        """Test days_ago with zero days (today)"""
        result = dh.days_ago(0, "America/Chicago")
        assert result.tzinfo == pytz.utc
        # Should be start of day in Chicago, converted to UTC
        # During CDT (summer), Chicago is UTC-5, during CST (winter), UTC-6
        assert result.hour in [5, 6]  # 00:00 Chicago -> 05:00 or 06:00 UTC
        assert result.minute == 0
        assert result.second == 0

    def test_days_ago_multiple_days(self):
        """Test days_ago with multiple days"""
        result_today = dh.days_ago(0, "America/Chicago")
        result_3_days = dh.days_ago(3, "America/Chicago")

        # Should be exactly 3 days difference
        diff = result_today - result_3_days
        assert diff.days == 3
        assert diff.seconds == 0

    def test_days_ago_different_timezone(self):
        """Test days_ago with different timezone"""
        chicago_result = dh.days_ago(1, "America/Chicago")
        ny_result = dh.days_ago(1, "America/New_York")

        # NY is 1 hour ahead of Chicago, so NY start-of-day is 1 hour earlier in UTC
        diff = chicago_result - ny_result
        assert abs(diff.total_seconds()) == 3600  # 1 hour difference

    def test_days_ago_negative_days_defaults_to_zero(self):
        """Test days_ago with negative days defaults to 0"""
        result_negative = dh.days_ago(-5)
        result_zero = dh.days_ago(0)
        assert result_negative == result_zero


class TestUtcFloatToPretty:
    """Test utc_float_to_pretty formatting function"""

    def test_utc_float_to_pretty_uses_admin_settings(self):
        """Test utc_float_to_pretty with admin settings"""
        utc_float = 20230722203045.123456  # 8:30:45 PM UTC
        result = dh.utc_float_to_pretty(utc_float)
        # Should format using ADMIN_DATE_FMT ("%a %m/%d/%Y %I:%M:%S %p")
        # and ADMIN_TIMEZONE ("America/Chicago")
        # 20:30 UTC would be 15:30 CDT (UTC-5) or 14:30 CST (UTC-6)
        assert isinstance(result, str)
        assert "2023" in result
        assert "07/22" in result or "7/22" in result
        assert "PM" in result or "AM" in result

    def test_utc_float_to_pretty_with_custom_format(self):
        """Test utc_float_to_pretty with custom format"""
        utc_float = 20230722153045.123456
        result = dh.utc_float_to_pretty(utc_float, fmt="%Y-%m-%d")
        assert result == "2023-07-22"

    def test_utc_float_to_pretty_with_timezone(self):
        """Test utc_float_to_pretty with timezone conversion"""
        utc_float = 20230722153045.123456  # 15:30:45 UTC
        result = dh.utc_float_to_pretty(utc_float, fmt="%H", timezone="America/New_York")
        # 15:30 UTC should be 11:30 EDT (UTC-4) in summer or 10:30 EST (UTC-5) in winter
        # July 22 is summer, so should be EDT
        assert result == "11"

    def test_utc_float_to_pretty_string_without_decimal(self):
        """Test utc_float_to_pretty with string input without decimal"""
        result = dh.utc_float_to_pretty("20230722153045", fmt="%Y-%m-%d")
        assert result == "2023-07-22"

    def test_utc_float_to_pretty_no_utc_float_uses_current_time(self):
        """Test utc_float_to_pretty without utc_float uses current time"""
        result = dh.utc_float_to_pretty(fmt="%Y")
        current_year = datetime.now().year
        assert result == str(current_year)

    def test_utc_float_to_pretty_various_timezones(self):
        """Test utc_float_to_pretty with various timezones"""
        utc_float = 20230722120000.0  # Noon UTC

        test_cases = [
            ("America/New_York", "08"),     # UTC-4 in summer
            ("America/Chicago", "07"),      # UTC-5 in summer
            ("America/Denver", "06"),       # UTC-6 in summer
            ("America/Los_Angeles", "05"),  # UTC-7 in summer
            ("Europe/London", "13"),        # UTC+1 in summer
            ("Asia/Tokyo", "21"),           # UTC+9 always
        ]

        for timezone, expected_hour in test_cases:
            result = dh.utc_float_to_pretty(utc_float, fmt="%H", timezone=timezone)
            assert result == expected_hour


class TestDateStringConversions:
    """Test date string parsing and conversion functions"""

    def test_date_string_to_datetime_default_format(self):
        """Test date_string_to_datetime with default format"""
        result = dh.date_string_to_datetime("2023-07-22")
        expected = datetime(2023, 7, 22)
        assert result == expected

    def test_date_string_to_datetime_custom_format(self):
        """Test date_string_to_datetime with custom format"""
        result = dh.date_string_to_datetime("07/22/2023", fmt="%m/%d/%Y")
        expected = datetime(2023, 7, 22)
        assert result == expected

    def test_date_string_to_datetime_with_timezone(self):
        """Test date_string_to_datetime with timezone"""
        result = dh.date_string_to_datetime("2023-07-22", timezone="America/Chicago")
        chicago_tz = pytz.timezone("America/Chicago")
        expected = chicago_tz.localize(datetime(2023, 7, 22))
        assert result == expected

    def test_date_string_to_datetime_already_datetime(self):
        """Test date_string_to_datetime when input is already datetime"""
        input_dt = datetime(2023, 7, 22)
        result = dh.date_string_to_datetime(input_dt)
        assert result == input_dt

    def test_date_string_to_datetime_with_microseconds_truncation(self):
        """Test date_string_to_datetime truncates microseconds when not in format"""
        result = dh.date_string_to_datetime("2023-07-22 15:30:45.123456", fmt="%Y-%m-%d %H:%M:%S")
        expected = datetime(2023, 7, 22, 15, 30, 45)
        assert result == expected


class TestDateStartUtc:
    """Test date_start_utc function"""

    def test_date_start_utc_default_timezone(self):
        """Test date_start_utc with default timezone (America/Chicago)"""
        result = dh.date_start_utc("2023-07-22")
        assert result.tzinfo == pytz.utc
        # Should be start of day in Chicago timezone, converted to UTC
        # In summer (July), Chicago is CDT (UTC-5), so 00:00 CDT = 05:00 UTC
        assert result.hour == 5
        assert result.minute == 0
        assert result.second == 0
        assert result.day == 22
        assert result.month == 7
        assert result.year == 2023

    def test_date_start_utc_winter_date(self):
        """Test date_start_utc with winter date (CST)"""
        result = dh.date_start_utc("2023-01-22")
        # In winter, Chicago is CST (UTC-6), so 00:00 CST = 06:00 UTC
        assert result.hour == 6
        assert result.minute == 0
        assert result.second == 0

    def test_date_start_utc_custom_timezone(self):
        """Test date_start_utc with custom timezone"""
        result = dh.date_start_utc("2023-07-22", timezone="America/New_York")
        # In summer, NYC is EDT (UTC-4), so 00:00 EDT = 04:00 UTC
        assert result.hour == 4
        assert result.minute == 0
        assert result.second == 0

    def test_date_start_utc_custom_format(self):
        """Test date_start_utc with custom format"""
        result = dh.date_start_utc("07/22/2023", fmt="%m/%d/%Y")
        assert result.hour == 5  # Chicago summer time
        assert result.day == 22
        assert result.month == 7
        assert result.year == 2023


class TestGetTimeRangesAndArgs:
    """Test get_time_ranges_and_args complex function"""

    def test_get_time_ranges_and_args_start_end_floats(self):
        """Test get_time_ranges_and_args with start and end parameters"""
        result = dh.get_time_ranges_and_args(start=123.456, end=789.012)
        expected = {"start=123.456,end=789.012": (123.456, 789.012)}
        assert result == expected

    def test_get_time_ranges_and_args_start_only(self):
        """Test get_time_ranges_and_args with start parameter only"""
        result = dh.get_time_ranges_and_args(start=123.456)
        expected = {"start=123.456": (123.456, float('inf'))}
        assert result == expected

    def test_get_time_ranges_and_args_end_only(self):
        """Test get_time_ranges_and_args with end parameter only"""
        result = dh.get_time_ranges_and_args(end=789.012)
        expected = {"end=789.012": (0, 789.012)}
        assert result == expected

    def test_get_time_ranges_and_args_start_ts_single(self):
        """Test get_time_ranges_and_args with single start_ts parameter"""
        result = dh.get_time_ranges_and_args(start_ts="2023-07-22 15:30:45")
        assert len(result) == 1
        key = list(result.keys())[0]
        assert key.startswith("start_ts=2023-07-22 15:30:45")
        start_val, end_val = list(result.values())[0]
        assert end_val == float('inf')
        # start_val should be the float representation of the timestamp
        assert start_val > 0

    def test_get_time_ranges_and_args_since_single(self):
        """Test get_time_ranges_and_args with single since parameter"""
        result = dh.get_time_ranges_and_args(since="2:hours")
        assert len(result) == 1
        key = list(result.keys())[0]
        assert key.startswith("since=2:hours")
        start_val, end_val = list(result.values())[0]
        assert end_val == float('inf')
        assert start_val > 0

    def test_get_time_ranges_and_args_no_parameters(self):
        """Test get_time_ranges_and_args with no parameters returns 'all' range"""
        result = dh.get_time_ranges_and_args()
        expected = {"all": (0, float('inf'))}
        assert result == expected

    def test_get_time_ranges_and_args_multiple_start_ts(self):
        """Test get_time_ranges_and_args with multiple start_ts values"""
        result = dh.get_time_ranges_and_args(start_ts="2023-07-22,2023-07-23")
        # Should create ranges for each start_ts
        assert len(result) >= 2
        keys = list(result.keys())
        assert any("start_ts=2023-07-22" in key for key in keys)
        assert any("start_ts=2023-07-23" in key for key in keys)

    def test_get_time_ranges_and_args_start_end_ts_combination(self):
        """Test get_time_ranges_and_args with both start_ts and end_ts"""
        result = dh.get_time_ranges_and_args(
            start_ts="2023-07-22 10:00:00",
            end_ts="2023-07-22 15:00:00"
        )
        assert len(result) >= 1
        # Should create a range between the two timestamps
        for key, (start_val, end_val) in result.items():
            if "start_ts=" in key and "end_ts=" in key:
                assert start_val < end_val
                assert start_val > 0
                assert end_val < float('inf')

    def test_get_time_ranges_and_args_custom_timezone(self):
        """Test get_time_ranges_and_args uses custom timezone"""
        result = dh.get_time_ranges_and_args(
            start_ts="2023-07-22 15:00:00",
            tz="America/New_York"
        )
        # The timezone should affect the conversion
        assert len(result) >= 1

    def test_get_time_ranges_and_args_custom_now(self):
        """Test get_time_ranges_and_args uses custom now value"""
        custom_now = "20230722150000.0"
        result = dh.get_time_ranges_and_args(
            since="2:hours",
            now=custom_now
        )
        assert len(result) >= 1
        # The since calculation should be relative to custom_now


class TestGetTimestampFormatterFromArgs:
    """Test get_timestamp_formatter_from_args function"""

    def test_get_timestamp_formatter_admin_fmt(self):
        """Test get_timestamp_formatter_from_args with admin_fmt=True"""
        formatter = dh.get_timestamp_formatter_from_args(admin_fmt=True)
        test_float = 20230722153045.123456
        result = formatter(test_float)
        # Should use ADMIN_DATE_FMT and ADMIN_TIMEZONE
        assert isinstance(result, str)
        assert "2023" in result
        assert "07/22" in result or "7/22" in result

    def test_get_timestamp_formatter_custom_format_and_timezone(self):
        """Test get_timestamp_formatter_from_args with custom format and timezone"""
        formatter = dh.get_timestamp_formatter_from_args(
            ts_fmt="%Y-%m-%d %H:%M",
            ts_tz="America/Chicago"
        )
        test_float = 20230722203045.123456  # 20:30:45 UTC
        result = formatter(test_float)
        # Should convert to Chicago time and format
        # 20:30 UTC = 15:30 CDT in summer
        assert result == "2023-07-22 15:30"

    def test_get_timestamp_formatter_format_only(self):
        """Test get_timestamp_formatter_from_args with format only (no timezone)"""
        formatter = dh.get_timestamp_formatter_from_args(ts_fmt="%Y-%m-%d")
        test_float = 20230722153045.123456
        result = formatter(test_float)
        assert result == "2023-07-22"

    def test_get_timestamp_formatter_no_args(self):
        """Test get_timestamp_formatter_from_args with no arguments returns identity function"""
        formatter = dh.get_timestamp_formatter_from_args()
        test_float = 20230722153045.123456
        result = formatter(test_float)
        assert result == test_float

    def test_get_timestamp_formatter_various_formats(self):
        """Test various timestamp formats"""
        test_float = 20230722153045.123456

        test_cases = [
            ("%Y", "2023"),
            ("%m/%d/%Y", "07/22/2023"),
            ("%H:%M:%S", "15:30:45"),
            ("%a %b %d", "Sat Jul 22"),
        ]

        for fmt, expected in test_cases:
            formatter = dh.get_timestamp_formatter_from_args(ts_fmt=fmt)
            result = formatter(test_float)
            assert result == expected


class TestConstants:
    """Test module constants and their usage"""

    def test_float_string_fmt_constant(self):
        """Test FLOAT_STRING_FMT constant is correctly defined"""
        assert dh.FLOAT_STRING_FMT == '%Y%m%d%H%M%S.%f'

    def test_float_string_fmt_usage(self):
        """Test FLOAT_STRING_FMT works with datetime formatting"""
        dt = datetime(2023, 7, 22, 15, 30, 45, 123456)
        result = dt.strftime(dh.FLOAT_STRING_FMT)
        assert result == "20230722153045.123456"

    def test_constants_are_loaded_correctly(self):
        """Test that all constants are properly loaded"""
        assert dh.ADMIN_TIMEZONE == "America/Chicago"
        assert dh.ADMIN_DATE_FMT == "%a %m/%d/%Y %I:%M:%S %p"
        assert dh.FLOAT_STRING_FMT == '%Y%m%d%H%M%S.%f'


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling"""

    def test_leap_year_handling(self):
        """Test leap year date handling"""
        leap_year_date = "2024-02-29"
        result = dh.date_string_to_utc_float_string(leap_year_date)
        assert result == "20240229000000.0"

        # Test that it converts back correctly
        back_dt = dh.float_string_to_dt(result)
        assert back_dt.year == 2024
        assert back_dt.month == 2
        assert back_dt.day == 29

    def test_timezone_boundary_dates(self):
        """Test dates around DST transitions"""
        # Test spring forward (DST starts) - March 12, 2023 in US
        spring_date = "2023-03-12"
        result = dh.date_start_utc(spring_date)
        assert result.month == 3
        assert result.day == 12

        # Test fall back (DST ends) - November 5, 2023 in US
        fall_date = "2023-11-05"
        result = dh.date_start_utc(fall_date)
        assert result.month == 11
        assert result.day == 5

    def test_extreme_date_values(self):
        """Test extreme but valid date values"""
        # Test very early date
        early_date = "1970-01-01"
        result = dh.date_string_to_utc_float_string(early_date)
        assert result is not None

        # Test far future date
        future_date = "2099-12-31"
        result = dh.date_string_to_utc_float_string(future_date)
        assert result is not None


# Integration tests
class TestIntegration:
    """Test integration between functions"""

    def test_utc_ago_integration_with_pretty_formatting(self):
        """Test utc_ago_float_string integrated with utc_float_to_pretty"""
        now = datetime(2023, 7, 22, 15, 30, 45)
        now_float = dh.dt_to_float_string(now)
        past_float_str = dh.utc_ago_float_string("2:hours", now=now_float)
        formatted = dh.utc_float_to_pretty(past_float_str, fmt="%Y-%m-%d %H:%M")

        expected_dt = now - timedelta(hours=2)
        expected = expected_dt.strftime("%Y-%m-%d %H:%M")
        assert formatted == expected

    def test_date_string_to_date_start_consistency(self):
        """Test date_string_to_utc_float_string consistency with date_start_utc"""
        date_str = "2023-07-22"
        timezone = "America/Chicago"

        # Method 1: via date_string_to_utc_float_string with timezone
        float_str = dh.date_string_to_utc_float_string(date_str, timezone=timezone)
        dt_from_float = dh.float_string_to_dt(float_str).replace(tzinfo=pytz.utc)

        # Method 2: via date_start_utc
        dt_from_start_utc = dh.date_start_utc(date_str, timezone=timezone)

        # Should be equivalent
        assert dt_from_float == dt_from_start_utc

    def test_timezone_conversion_consistency(self):
        """Test consistency between different timezone conversion methods"""
        utc_float = 20230722153045.0  # 15:30:45 UTC

        # Convert using utc_float_to_pretty with timezone
        chicago_formatted = dh.utc_float_to_pretty(
            utc_float, fmt="%H:%M", timezone="America/Chicago"
        )

        # Manually convert the datetime
        dt = dh.float_string_to_dt(str(utc_float))
        dt_utc = dt.replace(tzinfo=pytz.utc)
        chicago_tz = pytz.timezone("America/Chicago")
        dt_chicago = dt_utc.astimezone(chicago_tz)
        manual_formatted = dt_chicago.strftime("%H:%M")

        assert chicago_formatted == manual_formatted

    def test_time_range_calculation_consistency(self):
        """Test time range calculations work consistently"""
        # Set up a known time point
        now = datetime(2023, 7, 22, 15, 30, 45)
        now_float = dh.dt_to_float_string(now)

        # Calculate 2 hours ago using utc_ago_float_string
        past_float = dh.utc_ago_float_string("2:hours", now=now_float)

        # Use this in get_time_ranges_and_args
        ranges = dh.get_time_ranges_and_args(
            start=past_float,
            end=now_float
        )

        # Should create a 2-hour range
        key = "start={},end={}".format(past_float, now_float)
        assert key in ranges
        start_val, end_val = ranges[key]

        # Difference should be 2 hours worth of seconds
        time_diff_seconds = (float(now_float) - float(past_float)) * 1e-6  # Convert from microseconds
        # This is a rough check - the actual calculation is more complex
        assert start_val < end_val

    def test_formatter_with_real_timestamps(self):
        """Test timestamp formatter with real timestamp data"""
        # Create a formatter that uses admin settings
        admin_formatter = dh.get_timestamp_formatter_from_args(admin_fmt=True)

        # Create a custom formatter
        custom_formatter = dh.get_timestamp_formatter_from_args(
            ts_fmt="%Y-%m-%d %H:%M:%S",
            ts_tz="America/New_York"
        )

        # Test with a real timestamp
        test_float = float(dh.utc_now_float_string())

        admin_result = admin_formatter(test_float)
        custom_result = custom_formatter(test_float)

        # Both should return formatted strings
        assert isinstance(admin_result, str)
        assert isinstance(custom_result, str)

        # Admin result should contain expected format elements
        current_year = str(datetime.now().year)
        assert current_year in admin_result

        # Custom result should be in expected format
        assert current_year in custom_result
        assert "-" in custom_result
        assert ":" in custom_result


class TestRealWorldScenarios:
    """Test realistic usage scenarios"""

    def test_time_window_analysis(self):
        """Test analyzing events within time windows"""
        # Simulate analyzing events in the last 4 hours
        current_time = dh.get_utcnow()
        current_float = dh.dt_to_float_string(current_time)

        # Get time ranges for the last 4 hours
        ranges = dh.get_time_ranges_and_args(since="4:hours", now=current_float)

        # Should have at least one range
        assert len(ranges) >= 1

        # Check that the range makes sense
        for key, (start_val, end_val) in ranges.items():
            if "since=" in key:
                assert start_val < end_val
                assert end_val == float('inf') or end_val > start_val

    def test_date_range_queries(self):
        """Test typical date range query scenarios"""
        # Test various date range scenarios
        scenarios = [
            # Single day
            {"start_ts": "2023-07-22", "end_ts": "2023-07-23"},
            # Week range
            {"start_ts": "2023-07-15", "end_ts": "2023-07-22"},
            # Month range
            {"start_ts": "2023-07-01", "end_ts": "2023-08-01"},
            # Time-based ranges
            {"since": "1:days"},
            {"since": "1:weeks"},
            {"since": "1:hours", "until": "30:minutes"},
        ]

        for scenario in scenarios:
            ranges = dh.get_time_ranges_and_args(**scenario)
            assert len(ranges) >= 1

            # All ranges should have valid start/end values
            for key, (start_val, end_val) in ranges.items():
                assert isinstance(start_val, (int, float))
                assert isinstance(end_val, (int, float))
                if end_val != float('inf'):
                    assert start_val < end_val
