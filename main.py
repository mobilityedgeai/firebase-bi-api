#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Firebase BI API - Versão Produção
Versão: 2.0.0 (Produção)
Configurado para Gunicorn WSGI Server
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configuração de logging para produção
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)

# Configuração para produção
app.config['DEBUG'] = False
app.config['TESTING'] = False
app.config['ENV'] = 'production'

# Configuração CORS
CORS(app, 
     allow_origins=["*"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"])

# Importar Firebase (se disponível)
try:
    from firebase_admin_init import db
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase Admin conectado com sucesso")
except ImportError as e:
    FIREBASE_AVAILABLE = False
    logger.warning(f"⚠️ Firebase Admin não disponível: {e}")

def get_firebase_data(collection_name, enterprise_id, limit=100):
    """Busca dados do Firebase"""
    if not FIREBASE_AVAILABLE:
        return []
    
    try:
        query = db.collection(collection_name)
        if enterprise_id:
            query = query.where("enterpriseId", "==", enterprise_id)
        docs = query.limit(limit).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {collection_name}: {e}")
        return []

@app.route('/')
def index():
    """Página inicial da API"""
    return jsonify({
        'name': 'Firebase BI API',
        'version': '2.0.0',
        'environment': 'production',
        'description': 'APIs Firebase para Business Intelligence',
        'firebase_status': 'Connected' if FIREBASE_AVAILABLE else 'Disconnected',
        'endpoints': {
            '/health': 'Health check',
            '/alerts-checkin': 'Alerts Check-In por enterpriseId',
            '/checklist': 'Checklist por enterpriseId',
            '/driver-trips': 'Driver Trips por enterpriseId',
            '/incidents': 'Incidents por enterpriseId'
        },
        'usage': '/{endpoint}?enterpriseId=sA9EmrE3ymtnBqJKcYn7&days=30',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': 'production',
        'firebase': 'connected' if FIREBASE_AVAILABLE else 'disconnected',
        'server': 'gunicorn',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/alerts-checkin')
def alerts_checkin():
    """Alerts Check-In"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('AlertsCheckIn', enterprise_id)
        return jsonify({
            'collection': 'AlertsCheckIn',
            'enterpriseId': enterprise_id,
            'count': len(data),
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Erro na API alerts-checkin: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/checklist')
def checklist():
    """Checklist"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Checklist', enterprise_id)
        return jsonify({
            'collection': 'Checklist',
            'enterpriseId': enterprise_id,
            'count': len(data),
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Erro na API checklist: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/driver-trips')
def driver_trips():
    """Driver Trips"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('DriverTrips', enterprise_id)
        return jsonify({
            'collection': 'DriverTrips',
            'enterpriseId': enterprise_id,
            'count': len(data),
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Erro na API driver-trips: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/incidents')
def incidents():
    """Incidents"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Incidents', enterprise_id)
        return jsonify({
            'collection': 'Incidents',
            'enterpriseId': enterprise_id,
            'count': len(data),
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Erro na API incidents: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(404)
def not_found(error):
    """Tratamento de erro 404"""
    return jsonify({
        'error': 'Endpoint não encontrado',
        'available_endpoints': ['/', '/health', '/alerts-checkin', '/checklist', '/driver-trips', '/incidents'],
        'usage': '/{endpoint}?enterpriseId=sA9EmrE3ymtnBqJKcYn7'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Tratamento de erro 500"""
    return jsonify({
        'error': 'Erro interno do servidor',
        'timestamp': datetime.now().isoformat()
    }), 500

# Para desenvolvimento local apenas
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.warning("⚠️ Executando em modo desenvolvimento - Use Gunicorn para produção")
    app.run(host='0.0.0.0', port=port, debug=False)

# Configuração para Gunicorn (produção)
# O Gunicorn importará este arquivo e usará a variável 'app'
