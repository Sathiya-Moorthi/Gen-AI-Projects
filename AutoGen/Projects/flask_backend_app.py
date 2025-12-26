"""
Flask Backend API for RTCFR Multi-Agent Content Generation
===========================================================
RESTful API with async support and comprehensive error handling
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the workflow
from content_workflow_improved import run_content_workflow, WorkflowResult

# ============================================================================
# Flask App Configuration
# ============================================================================

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Store workflow history
workflow_history: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Helper Functions
# ============================================================================

def generate_workflow_id() -> str:
    """Generate unique workflow ID"""
    return f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"


def workflow_result_to_dict(result: WorkflowResult) -> Dict[str, Any]:
    """Convert WorkflowResult dataclass to dictionary"""
    return {
        "success": result.success,
        "research": result.research,
        "content": result.content,
        "seo_analysis": result.seo_analysis,
        "final_score": result.final_score,
        "error": result.error,
        "execution_time": result.execution_time
    }


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "RTCFR Multi-Agent Content Generation API",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """
    Main endpoint to trigger content generation workflow
    
    Request Body:
    {
        "request": "User's content generation request",
        "options": {
            "save_history": true
        }
    }
    
    Response:
    {
        "status": "success",
        "workflow_id": "wf_20241220_143025_123456",
        "result": {
            "success": true,
            "research": {...},
            "content": {...},
            "seo_analysis": {...},
            "final_score": {...},
            "execution_time": 45.2
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        user_request = data.get('request', '').strip()
        options = data.get('options', {})
        save_history = options.get('save_history', True)
        
        if not user_request:
            return jsonify({
                "status": "error",
                "message": "No content request provided"
            }), 400
        
        # Generate workflow ID
        workflow_id = generate_workflow_id()
        
        print(f"\n{'='*80}")
        print(f"📥 Received request: {workflow_id}")
        print(f"{'='*80}\n")
        
        # Run the workflow
        result = asyncio.run(run_content_workflow(user_request))
        
        # Convert to dictionary
        result_dict = workflow_result_to_dict(result)
        
        # Save to history if requested
        if save_history:
            workflow_history[workflow_id] = {
                "workflow_id": workflow_id,
                "request": user_request,
                "result": result_dict,
                "timestamp": datetime.now().isoformat()
            }
        
        response = {
            "status": "success" if result.success else "error",
            "workflow_id": workflow_id,
            "result": result_dict,
            "message": "Content generation completed successfully" if result.success else result.error
        }
        
        return jsonify(response), 200 if result.success else 500
        
    except json.JSONDecodeError:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON format"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/workflow-status/<workflow_id>', methods=['GET'])
def workflow_status(workflow_id: str):
    """
    Get status of a specific workflow
    
    Response:
    {
        "status": "found",
        "workflow": {
            "workflow_id": "wf_20241220_143025_123456",
            "request": "Original request",
            "result": {...},
            "timestamp": "2024-12-20T14:30:25.123456"
        }
    }
    """
    if workflow_id not in workflow_history:
        return jsonify({
            "status": "not_found",
            "message": f"Workflow {workflow_id} not found"
        }), 404
    
    return jsonify({
        "status": "found",
        "workflow": workflow_history[workflow_id]
    }), 200


@app.route('/api/workflow-history', methods=['GET'])
def get_workflow_history():
    """
    Get all workflow history
    
    Query Parameters:
    - limit: Maximum number of results (default: 10)
    - offset: Offset for pagination (default: 0)
    
    Response:
    {
        "status": "success",
        "total": 25,
        "limit": 10,
        "offset": 0,
        "workflows": [...]
    }
    """
    try:
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        # Get workflows sorted by timestamp (newest first)
        sorted_workflows = sorted(
            workflow_history.values(),
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        # Apply pagination
        paginated = sorted_workflows[offset:offset + limit]
        
        return jsonify({
            "status": "success",
            "total": len(workflow_history),
            "limit": limit,
            "offset": offset,
            "workflows": paginated
        }), 200
        
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid limit or offset parameter"
        }), 400


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """
    Clear workflow history
    
    Response:
    {
        "status": "success",
        "message": "Cleared 15 workflows from history"
    }
    """
    count = len(workflow_history)
    workflow_history.clear()
    
    return jsonify({
        "status": "success",
        "message": f"Cleared {count} workflows from history"
    }), 200


@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    """Debug endpoint to check environment variables"""
    return jsonify({
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "serp_api_key_set": bool(os.getenv("SERP_API_KEY")),
        "openai_key_prefix": os.getenv("OPENAI_API_KEY", "")[:10] + "..." if os.getenv("OPENAI_API_KEY") else None,
        "env_keys": [k for k in os.environ.keys() if "API" in k.upper()]
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get workflow statistics
    
    Response:
    {
        "status": "success",
        "stats": {
            "total_workflows": 25,
            "successful_workflows": 20,
            "failed_workflows": 5,
            "success_rate": 0.8,
            "avg_execution_time": 42.5
        }
    }
    """
    if not workflow_history:
        return jsonify({
            "status": "success",
            "stats": {
                "total_workflows": 0,
                "successful_workflows": 0,
                "failed_workflows": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0
            }
        }), 200
    
    total = len(workflow_history)
    successful = sum(1 for w in workflow_history.values() if w['result']['success'])
    failed = total - successful
    
    execution_times = [
        w['result']['execution_time'] 
        for w in workflow_history.values() 
        if w['result']['execution_time'] > 0
    ]
    avg_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
    
    return jsonify({
        "status": "success",
        "stats": {
            "total_workflows": total,
            "successful_workflows": successful,
            "failed_workflows": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_execution_time": round(avg_time, 2)
        }
    }), 200


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Starting RTCFR Multi-Agent Content Generation API")
    print("="*80)
    print("\nEndpoints:")
    print("  GET  /                          - Health check")
    print("  POST /api/generate-content      - Generate content")
    print("  GET  /api/workflow-status/<id>  - Get workflow status")
    print("  GET  /api/workflow-history      - Get workflow history")
    print("  POST /api/clear-history         - Clear history")
    print("  GET  /api/stats                 - Get statistics")
    print("\n" + "="*80 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )