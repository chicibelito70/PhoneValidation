from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import time
from routes.phone_routes import phone_bp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Registro simple de rate limit por IP (en memoria, no persistente)
rate_limit = {}

@app.before_request
def check_rate_limit():
    """
    Rate limit simple: máximo 10 requests por minuto por IP.
    """
    ip = request.remote_addr
    current_time = time.time()
    window_start = current_time - 60  # 1 minuto

    if ip not in rate_limit:
        rate_limit[ip] = []

    # Limpiar requests antiguas
    rate_limit[ip] = [t for t in rate_limit[ip] if t > window_start]

    if len(rate_limit[ip]) >= 10:
        return jsonify({"error": "Rate limit exceeded"}), 429

    rate_limit[ip].append(current_time)

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de health check.
    """
    return jsonify({"status": "healthy"}), 200

# Registrar blueprints
app.register_blueprint(phone_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)