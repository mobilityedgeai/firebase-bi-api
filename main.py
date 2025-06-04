#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Firebase BI API - Versão Corrigida EnterpriseId
Versão: 3.2.0 (Fix EnterpriseId)
17 APIs: Corrige campo EnterpriseId com E maiúsculo
Configurado para Gunicorn WSGI Server
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud.firestore_v1 import GeoPoint
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds

# Configuração de logging
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

# Importar Firebase
try:
    from firebase_admin_init import db
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase Admin conectado com sucesso")
except ImportError as e:
    FIREBASE_AVAILABLE = False
    logger.error(f"❌ Firebase Admin não disponível: {e}")

def serialize_firebase_data(data):
    """Converte tipos especiais do Firebase para JSON serializável"""
    if isinstance(data, dict):
        return {key: serialize_firebase_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_firebase_data(item) for item in data]
    elif isinstance(data, GeoPoint):
        return {
            'latitude': data.latitude,
            'longitude': data.longitude,
            '_type': 'GeoPoint'
        }
    elif isinstance(data, DatetimeWithNanoseconds):
        return data.isoformat()
    elif hasattr(data, 'isoformat'):
        return data.isoformat()
    else:
        return data

def get_firebase_data_fixed(collection_name, enterprise_id, limit=100):
    """Busca dados com correção para EnterpriseId maiúsculo"""
    if not FIREBASE_AVAILABLE:
        logger.error(f"❌ Firebase não disponível")
        return []
    
    try:
        query = db.collection(collection_name)
        if enterprise_id:
            # Testa AMBAS as variações do campo enterpriseId
            enterprise_fields = [
                'EnterpriseId',    # E maiúsculo (correto para APIs amarelas)
                'enterpriseId',    # e minúsculo (padrão atual)
                'enterprise_id',   # snake_case
                'companyId',       # alternativo
                'organizationId'   # alternativo
            ]
            
            for field in enterprise_fields:
                try:
                    logger.info(f"🔍 Testando {collection_name} com {field} = {enterprise_id}")
                    filtered_query = query.where(field, "==", enterprise_id)
                    docs = filtered_query.limit(limit).stream()
                    raw_data = [doc.to_dict() for doc in docs]
                    
                    if raw_data:
                        logger.info(f"✅ {collection_name}: {len(raw_data)} registros encontrados com {field}")
                        serialized_data = [serialize_firebase_data(doc) for doc in raw_data]
                        return serialized_data
                    else:
                        logger.info(f"⚠️ {collection_name}: Nenhum registro com {field} = {enterprise_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao filtrar {collection_name} por {field}: {e}")
                    continue
            
            logger.warning(f"⚠️ {collection_name}: Nenhum campo enterpriseId funcionou")
            return []
        else:
            # Sem filtro
            docs = query.limit(limit).stream()
            raw_data = [doc.to_dict() for doc in docs]
            serialized_data = [serialize_firebase_data(doc) for doc in raw_data]
            logger.info(f"✅ {collection_name}: {len(serialized_data)} registros sem filtro")
            return serialized_data
            
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
        'fix_applied': 'EnterpriseId_uppercase_fix',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Página inicial da API"""
    return jsonify({
        'name': 'Firebase BI API',
        'version': '3.2.0',
        'environment': 'production',
        'description': 'APIs Firebase BI - Fix EnterpriseId maiúsculo',
        'firebase_status': 'Connected' if FIREBASE_AVAILABLE else 'Disconnected',
        'total_endpoints': 17,
        'fix_applied': 'EnterpriseId com E maiúsculo',
        'endpoints': {
            '/health': 'Health check',
            '/alerts-checkin': 'Alerts Check-In',
            '/checklist': 'Checklist',
            '/branch': 'Filiais',
            '/garage': 'Garagens', 
            '/costcenter': 'Centros de Custo',
            '/sensors': 'Sensores',
            '/organization': 'Organizações',
            '/assettype': 'Tipos de Ativos',
            '/vehicles': 'Veículos (CORRIGIDO)',
            '/tires': 'Pneus (CORRIGIDO)',
            '/suppliers': 'Fornecedores (CORRIGIDO)',
            '/userregistration': 'Usuários (CORRIGIDO)',
            '/trips': 'Viagens (CORRIGIDO)',
            '/fuelregistration': 'Combustível (CORRIGIDO)',
            '/contractmanagement': 'Contratos (CORRIGIDO)',
            '/alelo-supply-history': 'Histórico Alelo (CORRIGIDO)'
        },
        'usage': '/{endpoint}?enterpriseId=qzDVZ1jB6IC60baxtsDU',
        'field_tested': ['EnterpriseId', 'enterpriseId', 'enterprise_id', 'companyId', 'organizationId'],
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
        'total_apis': 17,
        'fix_applied': 'EnterpriseId_uppercase',
        'timestamp': datetime.now().isoformat()
    })

# ===== APIs FUNCIONAIS =====

@app.route('/alerts-checkin')
def alerts_checkin():
    """Alerts Check-In"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('AlertsCheckIn', enterprise_id)
        return create_api_response('AlertsCheckIn', enterprise_id, data)
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
        
        data = get_firebase_data_fixed('Checklist', enterprise_id)
        return create_api_response('Checklist', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API checklist: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/branch')
def branch():
    """Filiais"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('Branch', enterprise_id)
        return create_api_response('Branch', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API branch: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/garage')
def garage():
    """Garagens"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('Garage', enterprise_id)
        return create_api_response('Garage', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API garage: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/costcenter')
def costcenter():
    """Centros de Custo"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('CostCenter', enterprise_id)
        return create_api_response('CostCenter', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API costcenter: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/sensors')
def sensors():
    """Sensores"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('Sensors', enterprise_id)
        return create_api_response('Sensors', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API sensors: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/organization')
def organization():
    """Organizações"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('Organization', enterprise_id)
        return create_api_response('Organization', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API organization: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/assettype')
def assettype():
    """Tipos de Ativos"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('AssetType', enterprise_id)
        return create_api_response('AssetType', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API assettype: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ===== APIs CORRIGIDAS (ERAM AMARELAS) =====

@app.route('/vehicles')
def vehicles():
    """Veículos - CORRIGIDO EnterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('Vehicles', enterprise_id)
        return create_api_response('Vehicles', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API vehicles: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/tires')
def tires():
    """Pneus - CORRIGIDO EnterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('Tires', enterprise_id)
        return create_api_response('Tires', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API tires: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/suppliers')
def suppliers():
    """Fornecedores - CORRIGIDO EnterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('Suppliers', enterprise_id)
        return create_api_response('Suppliers', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API suppliers: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/userregistration')
def userregistration():
    """Usuários - CORRIGIDO EnterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('UserRegistration', enterprise_id)
        return create_api_response('UserRegistration', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API userregistration: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/trips')
def trips():
    """Viagens - CORRIGIDO EnterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('Trips', enterprise_id)
        return create_api_response('Trips', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API trips: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/fuelregistration')
def fuelregistration():
    """Combustível - CORRIGIDO EnterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('FuelRegistration', enterprise_id)
        return create_api_response('FuelRegistration', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API fuelregistration: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/contractmanagement')
def contractmanagement():
    """Contratos - CORRIGIDO EnterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('ContractManagement', enterprise_id)
        return create_api_response('ContractManagement', enterprise_id, data)
    except Exception as e:
        logger.error(f"❌ Erro na API contractmanagement: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/alelo-supply-history')
def alelo_supply_history():
    """Histórico Alelo - CORRIGIDO EnterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_data_fixed('AleloSupplyHistory', enterprise_id)
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
            '/', '/health', '/alerts-checkin', '/checklist', '/branch', '/garage', '/costcenter',
            '/sensors', '/organization', '/assettype', '/vehicles', '/tires', '/suppliers',
            '/userregistration', '/trips', '/fuelregistration', '/contractmanagement', '/alelo-supply-history'
        ],
        'total_endpoints': 17,
        'fix_applied': 'EnterpriseId_uppercase'
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
