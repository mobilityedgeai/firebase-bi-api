#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Firebase BI API - Versão Híbrida Otimizada
Versão: 2.0.0
Data: 2025-06-04

Mantém 4 APIs existentes com Firebase real + 14 novas APIs
Total: 18 endpoints com filtro por enterpriseId
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# Importar conexão Firebase existente
try:
    from firebase_admin_init import db
    FIREBASE_AVAILABLE = True
    logging.info("✅ Firebase Admin conectado com sucesso")
except ImportError as e:
    FIREBASE_AVAILABLE = False
    logging.warning(f"⚠️ Firebase Admin não disponível: {e}")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)

# Configuração CORS (mantém compatibilidade com configuração atual)
CORS(app, 
     allow_origins=["*"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"])

# Configurações
app.config['DEBUG'] = False
app.config['TESTING'] = False

# URL da API Firebase BI existente (para APIs de valores únicos)
FIREBASE_BI_API_BASE = "https://firebase-bi-api.onrender.com"

def fetch_data_from_firebase_bi(endpoint, enterprise_id, days=30):
    """
    Busca dados da API Firebase BI existente (para valores únicos)
    """
    try:
        url = f"{FIREBASE_BI_API_BASE}/{endpoint}"
        params = {
            'enterpriseId': enterprise_id,
            'days': days
        }
        
        logger.info(f"🔗 Buscando dados de: {url}")
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Dados recebidos: {len(data) if isinstance(data, list) else 1} registros")
            return data
        else:
            logger.error(f"❌ Erro na API: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados: {str(e)}")
        return []

def extract_unique_values(data, field_name):
    """
    Extrai valores únicos de um campo específico
    """
    if not isinstance(data, list):
        return []
    
    unique_values = set()
    
    for item in data:
        if isinstance(item, dict) and field_name in item:
            value = item[field_name]
            if value and str(value).strip():
                unique_values.add(str(value).strip())
    
    return sorted(list(unique_values))

def get_filtered_unique_values(field_name, enterprise_id, days=30):
    """
    Busca valores únicos de um campo específico das APIs existentes
    """
    endpoints = ['alerts-checkin', 'checklist', 'driver-trips', 'incidents']
    all_values = set()
    
    for endpoint in endpoints:
        try:
            # Usar APIs locais se Firebase disponível
            if FIREBASE_AVAILABLE:
                if endpoint == 'alerts-checkin':
                    data = get_firebase_collection('AlertsCheckIn', enterprise_id)
                elif endpoint == 'checklist':
                    data = get_firebase_collection('Checklist', enterprise_id)
                elif endpoint == 'driver-trips':
                    data = get_firebase_collection('DriverTrips', enterprise_id)
                elif endpoint == 'incidents':
                    data = get_firebase_collection('Incidents', enterprise_id)
                else:
                    data = []
            else:
                # Fallback para API externa
                data = fetch_data_from_firebase_bi(endpoint, enterprise_id, days)
            
            values = extract_unique_values(data, field_name)
            all_values.update(values)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao buscar {endpoint}: {str(e)}")
            continue
    
    return sorted(list(all_values))

def get_firebase_collection(collection_name, enterprise_id, limit=100):
    """
    Busca dados de uma coleção Firebase (mantém lógica original)
    """
    if not FIREBASE_AVAILABLE:
        return []
    
    try:
        query = db.collection(collection_name)
        if enterprise_id:
            query = query.where("enterpriseId", "==", enterprise_id)
        docs = query.limit(limit).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {collection_name}: {str(e)}")
        return []

def get_mock_collection_data(collection_name, enterprise_id, days=30):
    """
    Dados simulados para novas coleções (que não existem ainda no Firebase)
    """
    # Data limite para filtro
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Dados simulados para novas coleções
    mock_data = {
        'vehicles': [
            {
                'id': 'vehicle_001',
                'enterpriseId': enterprise_id,
                'plate': 'ABC1234',
                'model': 'Ford Transit',
                'year': 2022,
                'type': 'Van',
                'status': 'Active',
                'garage': 'São Paulo',
                'branch': 'Filial SP',
                'costCenter': 'LOGISTICA',
                'driver': 'João Silva',
                'mileage': 45000,
                'timestamp': '2025-06-01T08:00:00Z'
            }
        ],
        'tires': [
            {
                'id': 'tire_001',
                'enterpriseId': enterprise_id,
                'vehicleId': 'vehicle_001',
                'vehiclePlate': 'ABC1234',
                'position': 'Front Left',
                'brand': 'Michelin',
                'model': 'XZE2+',
                'size': '225/75R17.5',
                'status': 'Good',
                'timestamp': '2025-06-01T08:00:00Z'
            }
        ],
        'suppliers': [
            {
                'id': 'supplier_001',
                'enterpriseId': enterprise_id,
                'name': 'Auto Peças São Paulo Ltda',
                'cnpj': '12.345.678/0001-90',
                'category': 'Peças e Componentes',
                'status': 'Active',
                'timestamp': '2025-06-01T08:00:00Z'
            }
        ],
        'userregistration': [
            {
                'id': 'user_001',
                'enterpriseId': enterprise_id,
                'name': 'João Silva',
                'email': 'joao.silva@empresa.com.br',
                'role': 'Driver',
                'status': 'Active',
                'timestamp': '2025-06-01T08:00:00Z'
            }
        ],
        'trips': [
            {
                'id': 'trip_001',
                'enterpriseId': enterprise_id,
                'vehicleId': 'vehicle_001',
                'vehiclePlate': 'ABC1234',
                'driverName': 'João Silva',
                'distance': 120.5,
                'status': 'Completed',
                'timestamp': '2025-06-01T08:00:00Z'
            }
        ],
        'sensors': [
            {
                'id': 'sensor_001',
                'enterpriseId': enterprise_id,
                'vehicleId': 'vehicle_001',
                'sensorType': 'GPS',
                'status': 'Active',
                'timestamp': '2025-06-04T13:45:00Z'
            }
        ],
        'organization': [
            {
                'id': 'org_001',
                'enterpriseId': enterprise_id,
                'name': 'Mobility Edge AI',
                'type': 'Matriz',
                'status': 'Active',
                'timestamp': '2025-06-01T08:00:00Z'
            }
        ],
        'fuelregistration': [
            {
                'id': 'fuel_001',
                'enterpriseId': enterprise_id,
                'vehiclePlate': 'ABC1234',
                'fuelType': 'Diesel',
                'quantity': 45.5,
                'totalCost': 266.18,
                'timestamp': '2025-06-01T07:30:00Z'
            }
        ],
        'contractmanagement': [
            {
                'id': 'contract_001',
                'enterpriseId': enterprise_id,
                'contractNumber': 'CTR-2024-001',
                'contractType': 'Manutenção',
                'supplierName': 'Auto Peças São Paulo Ltda',
                'status': 'Active',
                'timestamp': '2025-06-01T08:00:00Z'
            }
        ],
        'assettype': [
            {
                'id': 'assettype_001',
                'enterpriseId': enterprise_id,
                'name': 'Veículos Leves',
                'category': 'Veículos',
                'status': 'Active',
                'timestamp': '2025-06-01T08:00:00Z'
            }
        ],
        'alelo-supply-history': [
            {
                'id': 'alelo_001',
                'enterpriseId': enterprise_id,
                'cardNumber': '**** **** **** 1234',
                'cardHolderName': 'João Silva',
                'vehiclePlate': 'ABC1234',
                'transactionDate': '2025-06-01T12:30:00Z',
                'transactionType': 'Alimentação',
                'establishmentName': 'Restaurante Bom Sabor',
                'amount': 25.50,
                'status': 'Approved',
                'costCenter': 'LOGISTICA',
                'branch': 'Filial SP',
                'garage': 'São Paulo',
                'timestamp': '2025-06-01T12:30:00Z'
            }
        ]
    }
    
    # Retorna dados da coleção solicitada
    collection_data = mock_data.get(collection_name.lower(), [])
    
    # Filtrar por período se necessário
    if days and days > 0:
        filtered_data = []
        for item in collection_data:
            try:
                item_date = datetime.fromisoformat(item.get('timestamp', '2025-06-01T00:00:00Z').replace('Z', '+00:00'))
                if item_date >= start_date:
                    filtered_data.append(item)
            except:
                filtered_data.append(item)  # Incluir se não conseguir parsear data
        collection_data = filtered_data
    
    logger.info(f"📊 Coleção {collection_name}: {len(collection_data)} registros para enterprise {enterprise_id}")
    return collection_data

@app.route('/')
def index():
    """
    Página inicial com informações da API
    """
    return jsonify({
        'name': 'Firebase BI API - Versão Híbrida',
        'version': '2.0.0',
        'description': 'APIs Firebase existentes + 14 novas APIs com filtro por enterpriseId',
        'firebase_status': 'Connected' if FIREBASE_AVAILABLE else 'Simulated',
        'endpoints': {
            # APIs existentes (Firebase real)
            '/alerts-checkin': 'Alerts Check-In (Firebase real)',
            '/checklist': 'Checklist (Firebase real)',
            '/driver-trips': 'Driver Trips (Firebase real)',
            '/incidents': 'Incidents (Firebase real)',
            
            # APIs de valores únicos (extraídos de dados existentes)
            '/branch': 'Lista de filiais únicas por enterpriseId',
            '/garage': 'Lista de garagens únicas por enterpriseId',
            '/costcenter': 'Lista de centros de custo únicos por enterpriseId',
            
            # APIs de novas coleções (simuladas)
            '/vehicles': 'Lista de veículos por enterpriseId',
            '/tires': 'Lista de pneus por enterpriseId',
            '/suppliers': 'Lista de fornecedores por enterpriseId',
            '/userregistration': 'Lista de usuários registrados por enterpriseId',
            '/trips': 'Lista de viagens por enterpriseId',
            '/sensors': 'Lista de sensores por enterpriseId',
            '/organization': 'Dados da organização por enterpriseId',
            '/fuelregistration': 'Registros de combustível por enterpriseId',
            '/contractmanagement': 'Gestão de contratos por enterpriseId',
            '/assettype': 'Tipos de ativos por enterpriseId',
            '/alelo-supply-history': 'Histórico de transações Alelo por enterpriseId'
        },
        'parameters': {
            'enterpriseId': 'ID da empresa (obrigatório)',
            'days': 'Número de dias para análise (opcional, padrão: 30)'
        },
        'examples': {
            'existing_apis': '/checklist?enterpriseId=sA9EmrE3ymtnBqJKcYn7',
            'unique_values': '/branch?enterpriseId=sA9EmrE3ymtnBqJKcYn7&days=30',
            'new_collections': '/vehicles?enterpriseId=sA9EmrE3ymtnBqJKcYn7&days=30'
        },
        'total_endpoints': 18
    })

# ============================================================================
# APIs EXISTENTES (Firebase Real) - Convertidas para Flask
# ============================================================================

@app.route('/alerts-checkin')
def get_alerts_checkin():
    """Alerts Check-In (mantém funcionalidade original)"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_collection('AlertsCheckIn', enterprise_id)
        
        return jsonify({
            'enterpriseId': enterprise_id,
            'collection': 'AlertsCheckIn',
            'count': len(data),
            'data': data,
            'source': 'Firebase Real',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na API alerts-checkin: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@app.route('/checklist')
def get_checklist():
    """Checklist (mantém funcionalidade original)"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_collection('Checklist', enterprise_id)
        
        return jsonify({
            'enterpriseId': enterprise_id,
            'collection': 'Checklist',
            'count': len(data),
            'data': data,
            'source': 'Firebase Real',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na API checklist: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@app.route('/driver-trips')
def get_driver_trips():
    """Driver Trips (mantém funcionalidade original)"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_collection('DriverTrips', enterprise_id)
        
        return jsonify({
            'enterpriseId': enterprise_id,
            'collection': 'DriverTrips',
            'count': len(data),
            'data': data,
            'source': 'Firebase Real',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na API driver-trips: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@app.route('/incidents')
def get_incidents():
    """Incidents (mantém funcionalidade original)"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        data = get_firebase_collection('Incidents', enterprise_id)
        
        return jsonify({
            'enterpriseId': enterprise_id,
            'collection': 'Incidents',
            'count': len(data),
            'data': data,
            'source': 'Firebase Real',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na API incidents: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

# ============================================================================
# APIs DE VALORES ÚNICOS (Extraídos de dados existentes)
# ============================================================================

@app.route('/branch')
def get_branches():
    """API para obter lista de filiais únicas por enterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        days = int(request.args.get('days', 30))
        
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        branches = get_filtered_unique_values('branch', enterprise_id, days)
        
        return jsonify({
            'enterpriseId': enterprise_id,
            'days': days,
            'field': 'branch',
            'count': len(branches),
            'data': branches,
            'source': 'Extracted from existing APIs',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na API branch: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@app.route('/garage')
def get_garages():
    """API para obter lista de garagens únicas por enterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        days = int(request.args.get('days', 30))
        
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        garages = get_filtered_unique_values('garage', enterprise_id, days)
        
        return jsonify({
            'enterpriseId': enterprise_id,
            'days': days,
            'field': 'garage',
            'count': len(garages),
            'data': garages,
            'source': 'Extracted from existing APIs',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na API garage: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@app.route('/costcenter')
def get_cost_centers():
    """API para obter lista de centros de custo únicos por enterpriseId"""
    try:
        enterprise_id = request.args.get('enterpriseId')
        days = int(request.args.get('days', 30))
        
        if not enterprise_id:
            return jsonify({'error': 'enterpriseId é obrigatório'}), 400
        
        cost_centers = get_filtered_unique_values('costCenter', enterprise_id, days)
        
        return jsonify({
            'enterpriseId': enterprise_id,
            'days': days,
            'field': 'costCenter',
            'count': len(cost_centers),
            'data': cost_centers,
            'source': 'Extracted from existing APIs',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na API costcenter: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

# ============================================================================
# APIs DE NOVAS COLEÇÕES (Simuladas)
# ============================================================================

def create_collection_endpoint(collection_name, emoji):
    """Cria endpoint genérico para novas coleções"""
    def endpoint():
        try:
            enterprise_id = request.args.get('enterpriseId')
            days = int(request.args.get('days', 30))
            
            if not enterprise_id:
                return jsonify({'error': 'enterpriseId é obrigatório'}), 400
            
            logger.info(f"{emoji} Buscando {collection_name} para enterprise: {enterprise_id}")
            
            data = get_mock_collection_data(collection_name, enterprise_id, days)
            
            response = {
                'enterpriseId': enterprise_id,
                'days': days,
                'collection': collection_name,
                'count': len(data),
                'data': data,
                'source': 'Simulated (ready for Firebase integration)',
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Retornando {len(data)} registros de {collection_name}")
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"❌ Erro na API {collection_name}: {str(e)}")
            return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500
    
    return endpoint

# Registrar endpoints das novas coleções
new_collections = [
    ('vehicles', '🚗'),
    ('tires', '🛞'),
    ('suppliers', '🏭'),
    ('userregistration', '👥'),
    ('trips', '🚛'),
    ('sensors', '📡'),
    ('organization', '🏢'),
    ('fuelregistration', '⛽'),
    ('contractmanagement', '📋'),
    ('assettype', '🏷️'),
    ('alelo-supply-history', '💳')
]

for collection_name, emoji in new_collections:
    app.add_url_rule(f'/{collection_name}', 
                     f'get_{collection_name.replace("-", "_")}', 
                     create_collection_endpoint(collection_name, emoji))

@app.route('/health')
def health_check():
    """Endpoint de verificação de saúde"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'firebase_status': 'Connected' if FIREBASE_AVAILABLE else 'Simulated',
        'total_apis': 18,
        'existing_apis': ['alerts-checkin', 'checklist', 'driver-trips', 'incidents'],
        'unique_value_apis': ['branch', 'garage', 'costcenter'],
        'new_collection_apis': [name for name, _ in new_collections],
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Tratamento de erro 404"""
    existing_apis = ['alerts-checkin', 'checklist', 'driver-trips', 'incidents']
    unique_apis = ['branch', 'garage', 'costcenter']
    new_apis = [name for name, _ in new_collections]
    all_endpoints = existing_apis + unique_apis + new_apis + ['health']
    
    return jsonify({
        'error': 'Endpoint não encontrado',
        'available_endpoints': all_endpoints,
        'total_endpoints': len(all_endpoints),
        'usage': '/{endpoint}?enterpriseId=sA9EmrE3ymtnBqJKcYn7&days=30'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Tratamento de erro 500"""
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Verifique os logs para mais detalhes',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    logger.info("🚀 Iniciando Firebase BI API - Versão Híbrida v2.0.0")
    logger.info(f"📊 Total de endpoints: 18")
    logger.info(f"🔥 Firebase Status: {'Connected' if FIREBASE_AVAILABLE else 'Simulated'}")
    logger.info(f"🌐 Porta: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
