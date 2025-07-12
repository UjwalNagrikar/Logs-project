import unittest
import pytest
import json
from lambda.log_parser import process_log_entry, parse_unstructured_log, sanitize_log

class TestLogParser:

    def test_process_structured_log(self):
        """Test processing of structured log entries"""
        log_data = {
            "level": "ERROR",
            "message": "Database connection failed",
            "service": "api-server",
            "host": "server-001",
            "fields": {
                "error_code": "DB001",
                "retry_count": 3
            }
        }

        result = process_log_entry(log_data)

        assert result is not None
        assert result['level'] == 'ERROR'
        assert result['message'] == 'Database connection failed'
        assert result['service'] == 'api-server'
        assert result['parsed_fields']['error_code'] == 'DB001'

    def test_parse_apache_log(self):
        """Test parsing Apache access logs"""
        apache_log = '192.168.1.100 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1024'

        result = parse_unstructured_log(apache_log)

        assert result['log_type'] == 'access_log'
        assert result['parsed_fields']['client_ip'] == '192.168.1.100'
        assert result['parsed_fields']['method'] == 'GET'
        assert result['parsed_fields']['path'] == '/api/users'
        assert result['parsed_fields']['status_code'] == 200

    def test_sanitize_sensitive_data(self):
        """Test removal of sensitive information"""
        log_entry = {
            'message': 'User login with password=secret123 and token=abc123def',
            'level': 'INFO'
        }

        result = sanitize_log(log_entry)

        assert '[REDACTED]' in result['message']
        assert 'secret123' not in result['message']
        assert 'abc123def' not in result['message']

    def test_credit_card_sanitization(self):
        """Test credit card number sanitization"""
        log_entry = {
            'message': 'Payment processed for card 4532-1234-5678-9012',
            'level': 'INFO'
        }

        result = sanitize_log(log_entry)

        assert '[REDACTED]' in result['message']
        assert '4532-1234-5678-9012' not in result['message']

    def test_parse_logs_valid(self):
        # Test with a valid log input
        log_data = "INFO: User logged in\nERROR: Failed to load resource"
        expected_output = [
            {"level": "INFO", "message": "User logged in"},
            {"level": "ERROR", "message": "Failed to load resource"}
        ]
        self.assertEqual(parse_logs(log_data), expected_output)

    def test_parse_logs_empty(self):
        # Test with empty log input
        log_data = ""
        expected_output = []
        self.assertEqual(parse_logs(log_data), expected_output)

    def test_parse_logs_invalid_format(self):
        # Test with invalid log input
        log_data = "INVALID LOG FORMAT"
        with self.assertRaises(ValueError):
            parse_logs(log_data)

if __name__ == '__main__':
    unittest.main()