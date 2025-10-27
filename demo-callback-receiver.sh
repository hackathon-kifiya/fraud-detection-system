#!/bin/bash

# Demo Callback Receiver Server
# This simulates a financial services callback endpoint that receives evaluation results

set -e

CALLBACK_PORT="${CALLBACK_PORT:-9000}"

echo "================================================================"
echo "Financial Services Callback Receiver Demo"
echo "================================================================"
echo ""
echo "This server simulates a financial services callback endpoint"
echo "that receives fraud detection evaluation results asynchronously."
echo ""
echo "Listening on port: $CALLBACK_PORT"
echo ""

# Create a simple HTTP server using Python
# This will receive POST requests from the fraud detection system

python3 << 'PYTHON_SCRIPT'
import http.server
import socketserver
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = int("${CALLBACK_PORT:-9000}")

class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Custom logging to show timestamps and formatted output
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")
    
    def do_POST(self):
        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # Print formatted callback data
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            print("\n" + "="*80)
            print("CALLBACK RECEIVED")
            print("="*80)
            print(f"Entity ID: {data.get('entity_id', 'N/A')}")
            print(f"Data Type: {data.get('data_type', 'N/A')}")
            print(f"Timestamp: {data.get('timestamp', 'N/A')}")
            print("")
            
            eval_data = data.get('evaluation', {})
            if eval_data:
                print("Evaluation Results:")
                print(f"  Decision: {eval_data.get('decision', 'N/A')}")
                print(f"  Final Score: {eval_data.get('final_score', 'N/A')}")
                print(f"  Confidence: {eval_data.get('confidence', 'N/A')}")
                print("")
                print("Risk Scores:")
                print(f"  Rule Engine: {eval_data.get('rule_engine_score', 'N/A')}")
                print(f"  Anomaly Detection: {eval_data.get('anomaly_score', 'N/A')}")
                print(f"  ML Score: {eval_data.get('ml_score', 'N/A')}")
                print("")
            
            # Business logic simulation
            decision = eval_data.get('decision', '')
            if decision == 'auto_approve':
                print("✅ ACTION: AUTO APPROVED")
                print("   Transaction will proceed automatically")
            elif decision == 'auto_reject':
                print("❌ ACTION: AUTO REJECTED")
                print("   Transaction has been blocked")
            elif decision == 'human_review':
                print("⚠️  ACTION: REQUIRES HUMAN REVIEW")
                print("   Transaction queued for analyst review")
                print("   A flagged case has been created for investigation")
            
            print("="*80)
            print("")
            
            # Send acknowledgment
            response = {
                "status": "received",
                "message": "Callback processed successfully",
                "received_at": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error processing callback: {e}")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Callback receiver is running. Send POST requests with evaluation results.")
    
    # Suppress default logging
    def log_request(self, code='-', size='-'):
        pass

print(f"Starting callback receiver on port {PORT}...")
print("Press Ctrl+C to stop")
print("")

with socketserver.TCPServer(("", PORT), CallbackHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down callback receiver...")
        httpd.shutdown()
PYTHON_SCRIPT

