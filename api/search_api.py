from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
from datetime import datetime, timedelta
import os
from typing import Dict, Any, List
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)

# Configuration
OPENSEARCH_ENDPOINT = os.environ.get('OPENSEARCH_ENDPOINT')
OPENSEARCH_USERNAME = os.environ.get('OPENSEARCH_USERNAME', 'admin')
OPENSEARCH_PASSWORD = os.environ.get('OPENSEARCH_PASSWORD')

class LogSearchAPI:
    def __init__(self):
        self.opensearch_url = f"https://{OPENSEARCH_ENDPOINT}"
        self.auth = HTTPBasicAuth(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD)
    
    def search_logs(self, query: str, start_time: str = None, end_time: str = None, 
                   log_level: str = None, source: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Search logs with various filters
        """
        try:
            # Build Elasticsearch query
            es_query = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": []
                    }
                },
                "sort": [
                    {"timestamp": {"order": "desc"}}
                ],
                "size": limit
            }
            
            # Add text search
            if query:
                es_query["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query,
                        "fields": ["message", "parsed_fields.*"],
                        "type": "best_fields"
                    }
                })
            
            # Add time range filter
            if start_time or end_time:
                time_filter = {"range": {"timestamp": {}}}
                if start_time:
                    time_filter["range"]["timestamp"]["gte"] = start_time
                if end_time:
                    time_filter["range"]["timestamp"]["lte"] = end_time
                es_query["query"]["bool"]["filter"].append(time_filter)
            
            # Add log level filter
            if log_level:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"level.keyword": log_level}
                })
            
            # Add source filter
            if source:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"source.keyword": source}
                })
            
            # Execute search
            index_name = "logs-*"  # Search across all monthly indices
            response = requests.post(
                f"{self.opensearch_url}/{index_name}/_search",
                json=es_query,
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Search failed: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_aggregations(self, field: str, start_time: str = None, end_time: str = None) -> Dict[str, Any]:
        """
        Get aggregations for analytics
        """
        try:
            es_query = {
                "size": 0,
                "aggs": {
                    "field_values": {
                        "terms": {
                            "field": f"{field}.keyword",
                            "size": 20
                        }
                    },
                    "timeline": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "1h"
                        }
                    }
                }
            }
            
            # Add time range filter if provided
            if start_time or end_time:
                es_query["query"] = {
                    "bool": {
                        "filter": [{
                            "range": {
                                "timestamp": {
                                    "gte": start_time,
                                    "lte": end_time
                                }
                            }
                        }]
                    }
                }
            
            response = requests.post(
                f"{self.opensearch_url}/logs-*/_search",
                json=es_query,
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Aggregation failed: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}

# Initialize search API
search_api = LogSearchAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/search', methods=['GET'])
def search_logs():
    """
    Search logs endpoint
    Query parameters:
    - q: search query
    - start_time: start time (ISO format)
    - end_time: end time (ISO format)
    - level: log level filter
    - source: source filter
    - limit: maximum number of results
    """
    try:
        query = request.args.get('q', '')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        log_level = request.args.get('level')
        source = request.args.get('source')
        limit = int(request.args.get('limit', 100))
        
        results = search_api.search_logs(
            query=query,
            start_time=start_time,
            end_time=end_time,
            log_level=log_level,
            source=source,
            limit=limit
        )
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/aggregations/<field>', methods=['GET'])
def get_aggregations(field):
    """
    Get aggregations for a specific field
    """
    try:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        results = search_api.get_aggregations(
            field=field,
            start_time=start_time,
            end_time=end_time
        )
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get overall log statistics
    """
    try:
        # Get stats for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        stats = {
            "total_logs": 0,
            "error_logs": 0,
            "warning_logs": 0,
            "sources": [],
            "timeline": []
        }
        
        # Get level aggregations
        level_aggs = search_api.get_aggregations(
            field="level",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat()
        )
        
        if "aggregations" in level_aggs:
            for bucket in level_aggs["aggregations"]["field_values"]["buckets"]:
                if bucket["key"] == "ERROR":
                    stats["error_logs"] = bucket["doc_count"]
                elif bucket["key"] == "WARNING":
                    stats["warning_logs"] = bucket["doc_count"]
                stats["total_logs"] += bucket["doc_count"]
        
        # Get source aggregations
        source_aggs = search_api.get_aggregations(
            field="source",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat()
        )
        
        if "aggregations" in source_aggs:
            stats["sources"] = [
                {"name": bucket["key"], "count": bucket["doc_count"]}
                for bucket in source_aggs["aggregations"]["field_values"]["buckets"]
            ]
            
            # Timeline data
            stats["timeline"] = [
                {"time": bucket["key_as_string"], "count": bucket["doc_count"]}
                for bucket in source_aggs["aggregations"]["timeline"]["buckets"]
            ]
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)