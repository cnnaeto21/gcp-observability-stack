from flask import Flask, jsonify
from flask import Flask, jsonify, request
import datetime
import socket
import logging
import time
import logging
from logging.handlers import RotatingFileHandler
import os
from datadog import initialize, statsd
import random

# Import Google Cloud Logging
import google.cloud.logging

# Import Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Set up Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

app = Flask(__name__)

# Initialize Datadog statsd for custom metrics
initialize(statsd_host='localhost', statsd_port=8125)

# Configure logging to file
log_file = '/var/log/flask-app.log'
if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file))

file_handler = RotatingFileHandler(log_file, maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
app.logger.addHandler(console_handler)

app.logger.info('Flask app startup')

# Define metrics
REQUEST_COUNT = Counter(
    'flask_request_count', 
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'flask_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'flask_active_requests',
    'Number of requests currently being processed'
)

# Middleware to track metrics automatically
@app.before_request
def before_request():
    request.start_time = time.time()
    ACTIVE_REQUESTS.inc()

@app.after_request
def after_request(response):
    # Calculate request latency
    request_latency = time.time() - request.start_time
    
    # Record metrics
    REQUEST_LATENCY.labels(endpoint=request.path).observe(request_latency)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    
    ACTIVE_REQUESTS.dec()
    
    return response

@app.route('/')
def home():
    logging.info('Home endpoint accessed', extra={
        'endpoint': '/',
        'method': 'GET'
    })
    
    return jsonify({
        'message': 'Hello from GCP!',
        'timestamp': datetime.datetime.now().isoformat(),
        'hostname': socket.gethostname(),
        'status': 'running'
    })

@app.route('/health')
def health():
    logging.info('Health check', extra={'status': 'healthy'})
    return jsonify({'status': 'healthy'}), 200

@app.route('/slow')
def slow():
    """Simulate a slow endpoint for testing"""
    time.sleep(2)  # Sleep for 2 seconds
    return jsonify({'message': 'This was slow!'}), 200

@app.route('/error')
def error():
    """Simulate an error for testing"""
    logging.error('Intentional error triggered')
    return jsonify({'error': 'Something went wrong!'}), 500

# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/signup', methods=['POST'])
def signup():
    app.logger.info('User signup endpoint accessed')
    
    # Simulate signup logic
    user_type = random.choice(['free', 'premium', 'enterprise'])
    
    # Send custom metric to Datadog
    statsd.increment('app.signup.count', tags=[f'tier:{user_type}'])
    statsd.histogram('app.signup.value', random.randint(0, 100), tags=[f'tier:{user_type}'])
    
    app.logger.info(f'User signed up - tier: {user_type}')
    
    return jsonify({
        'message': 'Signup successful!',
        'tier': user_type
    }), 201
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
