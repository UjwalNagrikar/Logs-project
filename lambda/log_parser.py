import json
import boto3
import base64
import gzip
import re
from datetime import datetime
from typing import Dict, Any, List
import os

# Initialize AWS clients
opensearch_client = boto3.client('opensearchserverless')
s3_client = boto3.client('s3')

# Environment variables
OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
S3_BUCKET = os.environ['S3_BUCKET']
INDEX_NAME = os.environ['INDEX_NAME']

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for processing Kinesis log events
    """
    try:
        processed_records = []
        
        for record in event['Records']:
            # Decode Kinesis data
            payload = base64.b64decode(record['kinesis']['data'])
            
            # Handle gzipped logs
            if payload.startswith(b'\x1f\x8b'):
                payload = gzip.decompress(payload)
            
            log_data = json.loads(payload.decode('utf-8'))
            
            # Process each log entry
            processed_log = process_log_entry(log_data)
            
            if processed_log:
                # Index to OpenSearch
                index_to_opensearch(processed_log)
                
                # Archive to S3
                archive_to_s3(processed_log)
                
                processed_records.append(processed_log)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Processed {len(processed_records)} records',
                'processed_count': len(processed_records)
            })
        }
    
    except Exception as e:
        print(f"Error processing records: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def process_log_entry(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and enrich log entries
    """
    try:
        # Extract common log patterns
        log_patterns = {
            'apache': r'(\S+) \S+ \S+ \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)',
            'nginx': r'(\S+) - - \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)',
            'application': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)',
            'json': None  # Already structured
        }
        
        processed_log = {
            'timestamp': datetime.utcnow().isoformat(),
            'source': log_data.get('source', 'unknown'),
            'level': 'INFO',
            'message': '',
            'parsed_fields': {},
            'metadata': {}
        }
        
        # Determine log type and parse accordingly
        raw_message = log_data.get('message', '')
        
        if 'level' in log_data:
            # Structured log
            processed_log.update({
                'level': log_data.get('level', 'INFO'),
                'message': raw_message,
                'parsed_fields': log_data.get('fields', {}),
                'service': log_data.get('service', 'unknown'),
                'host': log_data.get('host', 'unknown')
            })
        else:
            # Parse unstructured logs
            parsed = parse_unstructured_log(raw_message)
            processed_log.update(parsed)
        
        # Add enrichment data
        processed_log['metadata'] = {
            'processing_time': datetime.utcnow().isoformat(),
            'processor': 'logx-lambda',
            'version': '1.0'
        }
        
        # Security: Remove sensitive data
        processed_log = sanitize_log(processed_log)
        
        return processed_log
        
    except Exception as e:
        print(f"Error processing log entry: {str(e)}")
        return None

def parse_unstructured_log(message: str) -> Dict[str, Any]:
    """
    Parse unstructured log messages using regex patterns
    """
    # Apache/Nginx access log pattern
    apache_pattern = r'(\S+) \S+ \S+ \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)'
    match = re.match(apache_pattern, message)
    
    if match:
        return {
            'level': 'INFO',
            'message': message,
            'parsed_fields': {
                'client_ip': match.group(1),
                'timestamp': match.group(2),
                'method': match.group(3),
                'path': match.group(4),
                'protocol': match.group(5),
                'status_code': int(match.group(6)),
                'response_size': int(match.group(7))
            },
            'log_type': 'access_log'
        }
    
    # Application log pattern
    app_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)'
    match = re.match(app_pattern, message)
    
    if match:
        return {
            'level': match.group(2),
            'message': match.group(3),
            'parsed_fields': {
                'original_timestamp': match.group(1)
            },
            'log_type': 'application_log'
        }
    
    # Default fallback
    return {
        'level': 'INFO',
        'message': message,
        'parsed_fields': {},
        'log_type': 'unstructured'
    }

def sanitize_log(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove sensitive information from logs
    """
    sensitive_patterns = [
        r'password["\s]*[:=]["\s]*[^"\s,}]+',
        r'token["\s]*[:=]["\s]*[^"\s,}]+',
        r'key["\s]*[:=]["\s]*[^"\s,}]+',
        r'secret["\s]*[:=]["\s]*[^"\s,}]+',
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'  # Credit card
    ]
    
    message = log_entry.get('message', '')
    
    for pattern in sensitive_patterns:
        message = re.sub(pattern, '[REDACTED]', message, flags=re.IGNORECASE)
    
    log_entry['message'] = message
    return log_entry

def index_to_opensearch(log_entry: Dict[str, Any]) -> None:
    """
    Index log entry to OpenSearch
    """
    try:
        # Create index if it doesn't exist
        index_name = f"{INDEX_NAME}-{datetime.utcnow().strftime('%Y-%m')}"
        
        # Index document (implement actual OpenSearch indexing)
        # This is a placeholder - you'll need to implement actual OpenSearch client
        print(f"Indexing to OpenSearch: {index_name}")
        
    except Exception as e:
        print(f"Error indexing to OpenSearch: {str(e)}")

def archive_to_s3(log_entry: Dict[str, Any]) -> None:
    """
    Archive log entry to S3
    """
    try:
        # Create S3 key with date partitioning
        date_partition = datetime.utcnow().strftime('%Y/%m/%d')
        key = f"logs/{date_partition}/{datetime.utcnow().timestamp()}.json"
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(log_entry),
            ContentType='application/json'
        )
        
    except Exception as e:
        print(f"Error archiving to S3: {str(e)}")