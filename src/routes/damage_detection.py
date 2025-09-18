from flask import Blueprint, request, jsonify
from PIL import Image
import io
import base64
import numpy as np
from src.services.yolo_service import YOLODamageService

damage_bp = Blueprint('damage', __name__)

# Instância global do serviço YOLO
yolo_service = YOLODamageService()

@damage_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'healthy',
        'service': 'YOLO Damage Detection API',
        'version': '1.0.0',
        'model_loaded': yolo_service.model is not None
    })

@damage_bp.route('/detect', methods=['POST'])
def detect_damage():
    """
    Endpoint principal para detecção de danos em imagens
    
    Aceita:
    - Arquivo de imagem via form-data (key: 'image')
    - Imagem em base64 via JSON (key: 'image_base64')
    - Informações opcionais do veículo
    
    Retorna:
    - Análise completa dos danos detectados
    - Imagem anotada em base64
    - Relatório detalhado
    """
    try:
        image = None
        vehicle_info = {}
        
        # Verifica se é uma requisição com arquivo
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
            
            # Carrega a imagem
            image = Image.open(file.stream).convert('RGB')
            
            # Pega informações do veículo do form-data
            vehicle_info = {
                'plate': request.form.get('plate', 'Não informado'),
                'model': request.form.get('model', 'Não informado'),
                'year': request.form.get('year', 'Não informado'),
                'color': request.form.get('color', 'Não informado')
            }
        
        # Verifica se é uma requisição JSON com base64
        elif request.is_json:
            data = request.get_json()
            
            if 'image_base64' not in data:
                return jsonify({'error': 'Campo image_base64 é obrigatório'}), 400
            
            try:
                # Decodifica a imagem base64
                image_data = base64.b64decode(data['image_base64'])
                image = Image.open(io.BytesIO(image_data)).convert('RGB')
                
                # Pega informações do veículo do JSON
                vehicle_info = data.get('vehicle_info', {})
                if not isinstance(vehicle_info, dict):
                    vehicle_info = {}
                
                # Garante que todos os campos existam
                vehicle_info = {
                    'plate': vehicle_info.get('plate', 'Não informado'),
                    'model': vehicle_info.get('model', 'Não informado'),
                    'year': str(vehicle_info.get('year', 'Não informado')),
                    'color': vehicle_info.get('color', 'Não informado')
                }
                
            except Exception as e:
                return jsonify({'error': f'Erro ao decodificar imagem base64: {str(e)}'}), 400
        
        else:
            return jsonify({'error': 'Formato de requisição inválido. Use form-data com arquivo ou JSON com base64'}), 400
        
        # Verifica se o modelo está carregado
        if yolo_service.model is None:
            return jsonify({'error': 'Modelo YOLO não está carregado'}), 500
        
        # Processa a imagem
        result = yolo_service.process_image(image)
        
        # Converte a imagem anotada para base64
        annotated_img_pil = Image.fromarray(result['annotated_image'])
        img_buffer = io.BytesIO()
        annotated_img_pil.save(img_buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        # Cria o relatório completo
        full_report = yolo_service.create_full_report(result['damage_analysis'], vehicle_info)
        
        # Prepara a resposta
        response = {
            'success': True,
            'detections': result['detections'],
            'damage_analysis': result['damage_analysis'],
            'summary': result['summary'],
            'annotated_image_base64': img_base64,
            'full_report': full_report,
            'processing_info': {
                'total_detections': len(result['detections']),
                'model_version': 'YOLOv8 car_damage_best.pt',
                'confidence_threshold': 0.25
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }), 500

@damage_bp.route('/analyze-batch', methods=['POST'])
def analyze_batch():
    """
    Endpoint para análise em lote de múltiplas imagens
    
    Aceita:
    - Lista de imagens em base64 via JSON
    
    Retorna:
    - Análise de cada imagem
    - Relatório consolidado
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Requisição deve ser JSON'}), 400
        
        data = request.get_json()
        
        if 'images' not in data or not isinstance(data['images'], list):
            return jsonify({'error': 'Campo images deve ser uma lista'}), 400
        
        if len(data['images']) == 0:
            return jsonify({'error': 'Lista de imagens não pode estar vazia'}), 400
        
        if len(data['images']) > 10:
            return jsonify({'error': 'Máximo de 10 imagens por requisição'}), 400
        
        # Verifica se o modelo está carregado
        if yolo_service.model is None:
            return jsonify({'error': 'Modelo YOLO não está carregado'}), 500
        
        results = []
        total_damages = 0
        total_cost = 0
        all_damage_types = set()
        
        vehicle_info = data.get('vehicle_info', {})
        
        for i, image_data in enumerate(data['images']):
            try:
                # Decodifica a imagem
                if isinstance(image_data, dict) and 'image_base64' in image_data:
                    img_b64 = image_data['image_base64']
                else:
                    img_b64 = image_data
                
                image_bytes = base64.b64decode(img_b64)
                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                
                # Processa a imagem
                result = yolo_service.process_image(image)
                
                # Converte imagem anotada para base64
                annotated_img_pil = Image.fromarray(result['annotated_image'])
                img_buffer = io.BytesIO()
                annotated_img_pil.save(img_buffer, format='JPEG', quality=85)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                # Adiciona aos totais
                total_damages += result['summary']['total_damages']
                total_cost += result['summary']['total_cost']
                all_damage_types.update(result['summary']['damage_types'])
                
                results.append({
                    'image_index': i,
                    'detections': result['detections'],
                    'damage_analysis': result['damage_analysis'],
                    'summary': result['summary'],
                    'annotated_image_base64': img_base64
                })
                
            except Exception as e:
                results.append({
                    'image_index': i,
                    'error': f'Erro ao processar imagem {i}: {str(e)}'
                })
        
        # Cria relatório consolidado
        consolidated_report = {
            'total_images': len(data['images']),
            'processed_images': len([r for r in results if 'error' not in r]),
            'failed_images': len([r for r in results if 'error' in r]),
            'total_damages_found': total_damages,
            'total_estimated_cost': round(total_cost, 2),
            'unique_damage_types': sorted(list(all_damage_types)),
            'vehicle_info': vehicle_info
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'consolidated_report': consolidated_report
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }), 500

@damage_bp.route('/model-info', methods=['GET'])
def model_info():
    """Retorna informações sobre o modelo carregado"""
    if yolo_service.model is None:
        return jsonify({
            'model_loaded': False,
            'error': 'Modelo não carregado'
        })
    
    try:
        return jsonify({
            'model_loaded': True,
            'model_path': yolo_service.model_path,
            'class_names': yolo_service.damage_config['class_names'],
            'supported_damage_types': list(yolo_service.damage_config['class_names'].keys()),
            'severity_levels': ['Leve', 'Moderado', 'Severo'],
            'model_version': 'YOLOv8',
            'input_formats': ['JPG', 'JPEG', 'PNG'],
            'max_image_size': '4096x4096'
        })
    except Exception as e:
        return jsonify({
            'model_loaded': False,
            'error': f'Erro ao obter informações do modelo: {str(e)}'
        }), 500
