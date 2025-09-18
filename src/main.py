import os
import sys

os.environ['OPENCV_HEADLESS'] = '1'
os.environ['DISPLAY'] = ''
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from src.models.user import db
from src.routes.user import user_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

@app.route('/api/damage/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'YOLO Damage Detection API',
        'version': '1.0.0',
        'model_loaded': False
    })

try:
    from src.routes.damage_detection import damage_bp
    app.register_blueprint(damage_bp, url_prefix='/api/damage')
    print("Blueprint damage_detection carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar damage_detection: {e}")
    
    @app.route('/api/damage/<path:path>', methods=['GET', 'POST'])
    def damage_fallback(path):
        return jsonify({
            'error': 'Serviço de detecção indisponível',
            'details': str(e)
        }), 503

app.register_blueprint(user_bp, url_prefix='/api')

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

try:
    with app.app_context():
        os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)
        db.create_all()
except Exception as e:
    print(f"Erro ao criar banco de dados: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
