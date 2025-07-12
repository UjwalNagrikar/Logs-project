#!/usr/bin/env python3
"""
Log Generator Script for Testing LogX Platform
Generates realistic log entries and sends them to Kinesis
"""

import json
import random
import time
from datetime import datetime
import boto3
from faker import Faker
import argparse

fake = Faker()

class LogGenerator:
    def __init__(self, stream_name: str, region: str = 'us-east-1'):
        self.kinesis_client = boto3.client('kinesis', region_name=region)
        self.stream_name = stream_name
        
        # Log templates
        self.log_templates = {
            'apache': self._generate_apache_log,
            'application': self._generate_application_log,
            'error': self._generate_error_log,
            'api': self._generate_api_log
        }
    
    def _generate_apache_log(self) -> dict:
        """Generate Apache access log"""
        ip = fake.ipv4()
        timestamp = datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')
        method = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
        path = random.choice(['/api/users', '/api/orders', '/health', '/metrics'])
        status = random.choice([200, 404, 500, 301, 403])
        size = random.randint(100, 5000)
        
        message = f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status} {size}'
        
        return {
            'source': 'apache',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_application_log(self) -> dict:
        """Generate structured application log"""
        levels = ['INFO', 'DEBUG', 'WARNING']
        services = ['user-service', 'order-service', 'payment-service']
        
        return {
            'source': 'application',
            'level': random.choice(levels),
            'service': random.choice(services),
            'host': fake.hostname(),
            'message': fake.sentence(),
            'timestamp': datetime.now().isoformat(),
            'fields': {
                'request_id': fake.uuid4(),
                'user_id': fake.random_int(min=1, max=10000),
                'duration_ms': fake.random_int(min=10, max=1000)
            }
        }
    
    def _generate_error_log(self) -> dict:
        """Generate error log"""
        errors = [
            'Database connection timeout',
            'Authentication failed',
            'Memory allocation error',
            'Network connection refused',
            'File not found'
        ]
        
        return {
            'source': 'application',
            'level': 'ERROR',
            'service': random.choice(['api-server', 'database', 'cache']),
            'host': fake.hostname(),
            'message': random.choice(errors),
            'timestamp': datetime.now().isoformat(),
            'fields': {
                'error_code': f'ERR{fake.random_int(min=1000, max=9999)}',
                'stack_trace': fake.text(max_nb_chars=200)
            }
        }
    
    def _generate_api_log(self) -> dict:
        """Generate API log"""
        endpoints = ['/api/v1/users', '/api/v1/orders', '/api/v1/products']
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        
        return {
            'source': 'api-gateway',
            'level': 'INFO',
            'message': f'API Request processed',
            'timestamp': datetime.now().isoformat(),
            'fields': {
                'endpoint': random.choice(endpoints),
                'method': random.choice(methods),
                'response_time': fake.random_int(min=10, max=2000),
                'status_code': random.choice([200, 201, 400, 404, 500]),
                'client_ip': fake.ipv4(),
                'user_agent': fake.user_agent()
            }
        }
    
    def generate_log(self, log_type: str = None) -> dict:
        """Generate a single log entry"""
        if log_type is None:
            log_type = random.choice(list(self.log_templates.keys()))
        
        return self.log_templates[log_type]()
    
    def send_to_kinesis(self, log_entry: dict):
        """Send log entry to Kinesis stream"""
        try:
            response = self.kinesis_client.put_record(
                StreamName=self.stream_name,
                Data=json.dumps(log_entry),
                PartitionKey=str(random.randint(1, 10))
            )
            return response
        except Exception as e:
            print(f"Error sending to Kinesis: {e}")
            return None
    
    def generate_continuous_logs(self, rate: int = 10, duration: int = 60):
        """Generate logs continuously"""
        print(f"Generating logs at {rate} logs/second for {duration} seconds...")
        
        start_time = time.time()
        count = 0
        
        while time.time() - start_time < duration:
            log_entry = self.generate_log()
            response = self.send_to_kinesis(log_entry)
            
            if response:
                count += 1
                print(f"Sent log {count}: {log_entry['source']} - {log_entry.get('level', 'INFO')}")
            
            time.sleep(1 / rate)
        
        print(f"Generated {count} logs in {duration} seconds")

def main():
    parser = argparse.ArgumentParser(description='Generate logs for LogX platform')
    parser.add_argument('--stream', required=True, help='Kinesis stream name')
    parser.add_argument('--rate', type=int, default=10, help='Logs per second')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    generator = LogGenerator(args.stream, args.region)
    generator.generate_continuous_logs(args.rate, args.duration)

if __name__ == '__main__':
    main()