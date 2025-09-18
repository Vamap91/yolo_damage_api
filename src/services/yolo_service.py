import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from datetime import datetime
import json

os.environ['OPENCV_HEADLESS'] = '1'
os.environ['DISPLAY'] = ''
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

class YOLODamageService:
    
    def __init__(self):
        self.model = None
        self.model_path = "car_damage_best.pt"
        self.damage_config = {
            'severity_map': {
                'shattered_glass': 'Severo',
                'broken_lamp': 'Severo',
                'flat_tire': 'Severo',
                'dent': 'Moderado',
                'scratch': 'Leve',
                'crack': 'Leve'
            },
            'location_map': {
                'shattered_glass': 'Para-brisa/Vidros',
                'flat_tire': 'Rodas',
                'broken_lamp': 'Faróis/Lanternas',
                'dent': 'Carroceria',
                'scratch': 'Pintura',
                'crack': 'Para-choque/Plásticos'
            },
            'class_names': {
                'shattered_glass': 'Vidro Quebrado',
                'broken_lamp': 'Lâmpada Quebrada',
                'flat_tire': 'Pneu Vazio',
                'dent': 'Amassado',
                'scratch': 'Risco',
                'crack': 'Rachadura'
            },
            'cost_estimates': {
                'shattered_glass': (800, 2500),
                'broken_lamp': (300, 800),
                'flat_tire': (200, 600),
                'dent': (400, 1500),
                'scratch': (150, 800),
                'crack': (200, 1000)
            },
            'colors': {
                'shattered_glass': (255, 0, 0),
                'broken_lamp': (255, 165, 0),
                'flat_tire': (255, 255, 0),
                'dent': (0, 255, 0),
                'scratch': (0, 0, 255),
                'crack': (128, 0, 128)
            }
        }
        self._load_model()
    
    def _download_model(self):
        if os.path.exists(self.model_path):
            return True
            
        model_url = "https://github.com/Vamap91/YOLOProject/releases/download/v2.0.0/car_damage_best.pt"
        
        try:
            print("Baixando modelo YOLO...")
            response = requests.get(model_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(self.model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print("Modelo baixado com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro ao baixar o modelo: {e}")
            return False
    
    def _load_model(self):
        try:
            if not self._download_model():
                raise Exception("Falha ao baixar o modelo")
            
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            print("Modelo YOLO carregado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao carregar o modelo: {e}")
            self.model = None
    
    def _draw_annotations_pil(self, image_array, detections):
        """Desenha anotações usando PIL ao invés do OpenCV"""
        if isinstance(image_array, np.ndarray):
            img = Image.fromarray(image_array.astype('uint8'))
        else:
            img = image_array
        
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            
            color = self.damage_config['colors'].get(class_name, (255, 0, 0))
            
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            label = f"{self.damage_config['class_names'].get(class_name, class_name)}: {confidence:.2f}"
            
            if font:
                bbox_font = draw.textbbox((x1, y1-20), label, font=font)
                draw.rectangle([bbox_font[0], bbox_font[1], bbox_font[2], bbox_font[3]], fill=color)
                draw.text((x1, y1-20), label, fill=(255, 255, 255), font=font)
            else:
                draw.text((x1, y1-15), label, fill=color)
        
        return np.array(img)
    
    def process_image(self, image_data):
        if self.model is None:
            raise Exception("Modelo não carregado")
        
        if isinstance(image_data, Image.Image):
            img_array = np.array(image_data)
        else:
            img_array = image_data
        
        results = self.model(img_array)
        
        detections = []
        if len(results[0].boxes) > 0:
            for box in results[0].boxes:
                class_id = int(box.cls)
                class_name = self.model.names[class_id]
                detection = {
                    'class': class_name,
                    'confidence': float(box.conf),
                    'bbox': box.xyxy[0].cpu().numpy().tolist()
                }
                detections.append(detection)
        
        try:
            annotated_img = self._draw_annotations_pil(img_array, detections)
        except Exception as e:
            print(f"Error generating annotated image: {e}")
            annotated_img = img_array
        
        damage_analysis = self._create_damage_analysis(detections)
        
        return {
            'detections': detections,
            'damage_analysis': damage_analysis,
            'annotated_image': annotated_img,
            'summary': self._create_summary(damage_analysis)
        }
    
    def _create_damage_analysis(self, detections):
        damage_report = []
        
        for i, detection in enumerate(detections):
            class_name = detection['class']
            severity = self.damage_config['severity_map'].get(class_name, 'Indefinido')
            location = self.damage_config['location_map'].get(class_name, 'N/A')
            cost_range = self.damage_config['cost_estimates'].get(class_name, (100, 500))
            
            confidence = detection['confidence']
            min_cost, max_cost = cost_range
            estimated_cost = min_cost + (max_cost - min_cost) * confidence
            
            damage_report.append({
                'damage_id': f"DMG_{i+1:03d}",
                'class': class_name,
                'class_display': self.damage_config['class_names'].get(class_name, class_name.replace('_', ' ').title()),
                'confidence': confidence,
                'severity': severity,
                'location': location,
                'estimated_cost': round(estimated_cost, 2),
                'bbox': detection['bbox']
            })
        
        return damage_report
    
    def _create_summary(self, damage_analysis):
        if not damage_analysis:
            return {
                'total_damages': 0,
                'total_cost': 0,
                'urgency': 'Baixa',
                'severity_count': {'Leve': 0, 'Moderado': 0, 'Severo': 0},
                'damage_types': []
            }
        
        severity_count = {'Leve': 0, 'Moderado': 0, 'Severo': 0}
        damage_types = []
        total_cost = 0
        
        for damage in damage_analysis:
            severity = damage.get('severity', 'Indefinido')
            if severity in severity_count:
                severity_count[severity] += 1
            
            if damage['class_display'] not in damage_types:
                damage_types.append(damage['class_display'])
            
            total_cost += damage['estimated_cost']
        
        urgency = 'Baixa'
        if severity_count['Severo'] > 0:
            urgency = 'Alta'
        elif severity_count['Moderado'] > 0:
            urgency = 'Média'
        
        return {
            'total_damages': len(damage_analysis),
            'total_cost': round(total_cost, 2),
            'urgency': urgency,
            'severity_count': severity_count,
            'damage_types': sorted(damage_types)
        }
    
    def create_full_report(self, damage_analysis, vehicle_info=None):
        summary = self._create_summary(damage_analysis)
        
        report = {
            "inspection_info": {
                "timestamp": datetime.now().isoformat(),
                "inspector": "Sistema IA YOLO",
                "version": "2.0",
                "model": "YOLOv8 (car_damage_best.pt)",
            },
            "vehicle_info": vehicle_info or {
                "plate": "Não informado",
                "model": "Não informado",
                "year": "Não informado",
                "color": "Não informado"
            },
            "damage_analysis": {
                "total_damages": summary['total_damages'],
                "severity_count": summary['severity_count'],
                "damage_types": summary['damage_types'],
                "estimated_total_cost": f"R$ {summary['total_cost']:,.2f}",
                "repair_urgency": summary['urgency'],
            },
            "damages": damage_analysis
        }
        
        return report
