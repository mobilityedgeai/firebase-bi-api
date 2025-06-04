#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Firebase BI API - Versão Produção com Dados Reais
Versão: 2.0.0 (Produção)
18 APIs: Todas buscando dados reais do Firebase
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
     origins=["*"],
     supports_credentials=True,
     methods=["*"],
     allow_headers=["*"])

# Importar Firebase (obrigatório para dados reais)
try:
    from firebase_admin_init import db
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase Admin conectado com sucesso")
except ImportError as e:
    FIREBASE_AVAILABLE = False
    logger.error(f"❌ Firebase Admin não disponível: {e}")
    logger.error("❌ ERRO CRÍTICO: Firebase é obrigatório para dados reais!")

def get_firebase_data(collection_name, enterprise_id, limit=100):
    """Busca dados reais do Firebase"""
    if not FIREBASE_AVAILABLE:
        logger.error(f"❌ Firebase não disponível para coleção {collection_name}")
        return []
    
    try:
        query = db.collection(collection_name)
        if enterprise_id:
            query = query.where("enterpriseId", "==", enterprise_id)
        docs = query.limit(limit).stream()
        data = [doc.to_dict() for doc in docs]
        logger.info(f"✅ {collection_name}: {len(data)} registros encontrados para enterpriseId {enterprise_id}")
        return data
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {collection_name}: {e}")
        return []

def create_api_response(collection_name, enterprise_id, data):
    """Cria resposta padrão da API"""
    return jsonify({
        'collection': collection_name,
        'enterpriseId': enterprise_id,
        'count': len(data),
        'data': data,
        'source': 'firebase_real',
        'firebase_status': 'connected' if FIREBASE_AVAILABLE else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Página inicial da API"""
    return jsonify({
        'name': 'Firebase BI API',
        'version': '2.0.0',
        'environment': 'production',
        'description': 'APIs Firebase para Business Intelligence - Dados Reais',
        'firebase_status': 'Connected' if FIREBASE_AVAILABLE else 'Disconnected',
        'data_source': 'Firebase Real Data Only',
        'total_endpoints': 18,
        'endpoints': {
            '/health': 'Health check',
            '/alerts-checkin': 'Alerts Check-In por enterpriseId',
            '/checklist': 'Checklist por enterpriseId',
            '/driver-trips': 'Driver Trips por enterpriseId',
            '/incidents': 'Incidents por enterpriseId',
            '/branch': 'Filiais por enterpriseId',
            '/garage': 'Garagens por enterpriseId',
            '/costcenter': 'Centros de Custo por enterpriseId',
            '/vehicles': 'Veículos por enterpriseId',
            '/tires': 'Pneus por enterpriseId',
            '/suppliers': 'Fornecedores por enterpriseId',
            '/userregistration': 'Usuários por enterpriseId',
            '/trips': 'Viagens por enterpriseId',
            '/sensors': 'Sensores por enterpriseId',
            '/organization': 'Organizações por enterpriseId',
            '/fuelregistration': 'Registros de Combustível por enterpriseId',
            '/contractmanagement': 'Gestão de Contratos por enterpriseId',
            '/assettype': 'Tipos de Ativos por enterpriseId',
            '/alelo-supply-history': 'Histórico Alelo por enterpriseId'
        },
        'usage': '/{endpoint}?enterpriseId=sA9EmrE3ymtnBqJKcYn7&days=30',
        'note': 'Todas as APIs retornam dados reais do Firebase',
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
        'data_source': 'firebase_real',
        'total_apis': 18,
        'timestamp': datetime.now().isoformat()
    })

# ===== APIs COM DADOS REAIS DO FIREBASE =====

@app.route('/alerts-checkin')
def alerts_checkin():
    """Alerts Check-In - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('AlertsCheckIn', enterprise_id)
        return create_api_response('AlertsCheckIn', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API alerts-checkin: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/checklist')
def checklist():
    """Checklist - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Checklist', enterprise_id)
        return create_api_response('Checklist', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API checklist: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/driver-trips')
def driver_trips():
    """Driver Trips - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('DriverTrips', enterprise_id)
        return create_api_response('DriverTrips', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API driver-trips: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/incidents')
def incidents():
    """Incidents - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Incidents', enterprise_id)
        return create_api_response('Incidents', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API incidents: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/branch')
def branch():
    """Filiais - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Branch', enterprise_id)
        return create_api_response('Branch', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API branch: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/garage')
def garage():
    """Garagens - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Garage', enterprise_id)
        return create_api_response('Garage', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API garage: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/costcenter')
def costcenter():
    """Centros de Custo - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('CostCenter', enterprise_id)
        return create_api_response('CostCenter', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API costcenter: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/vehicles')
def vehicles():
    """Veículos - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Vehicles', enterprise_id)
        return create_api_response('Vehicles', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API vehicles: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/tires')
def tires():
    """Pneus - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Tires', enterprise_id)
        return create_api_response('Tires', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API tires: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/suppliers')
def suppliers():
    """Fornecedores - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Suppliers', enterprise_id)
        return create_api_response('Suppliers', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API suppliers: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/userregistration')
def userregistration():
    """Usuários - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('UserRegistration', enterprise_id)
        return create_api_response('UserRegistration', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API userregistration: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/trips')
def trips():
    """Viagens - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Trips', enterprise_id)
        return create_api_response('Trips', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API trips: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/sensors')
def sensors():
    """Sensores - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Sensors', enterprise_id)
        return create_api_response('Sensors', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API sensors: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/organization')
def organization():
    """Organizações - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('Organization', enterprise_id)
        return create_api_response('Organization', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API organization: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/fuelregistration')
def fuelregistration():
    """Registros de Combustível - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('FuelRegistration', enterprise_id)
        return create_api_response('FuelRegistration', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API fuelregistration: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/contractmanagement')
def contractmanagement():
    """Gestão de Contratos - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('ContractManagement', enterprise_id)
        return create_api_response('ContractManagement', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API contractmanagement: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/assettype')
def assettype():
    """Tipos de Ativos - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('AssetType', enterprise_id)
        return create_api_response('AssetType', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API assettype: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/alelo-supply-history')
def alelo_supply_history():
    """Histórico Alelo - Dados Reais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data('AleloSupplyHistory', enterprise_id)
        return create_api_response('AleloSupplyHistory', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API alelo-supply-history: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(404)
def not_found(error):
    """Tratamento de erro 404"""
    return jsonify({
        'error': 'Endpoint não encontrado',
        'available_endpoints': [
            '/', '/health', '/alerts-checkin', '/checklist', '/driver-trips', '/incidents',
            '/branch', '/garage', '/costcenter', '/vehicles', '/tires', '/suppliers',
            '/userregistration', '/trips', '/sensors', '/organization', '/fuelregistration',
            '/contractmanagement', '/assettype', '/alelo-supply-history'
        ],
        'usage': '/{endpoint}?enterpriseId=sA9EmrE3ymtnBqJKcYn7',
        'total_endpoints': 18,
        'data_source': 'firebase_real'
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
