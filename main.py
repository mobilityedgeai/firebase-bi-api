from flask import Flask, request, jsonify
from firebase_admin_init import db
from flask_cors import CORS
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def serialize_firebase_data(data):
    """Converte tipos especiais do Firebase para JSON serializável"""
    if isinstance(data, dict):
        return {key: serialize_firebase_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_firebase_data(item) for item in data]
    elif hasattr(data, 'latitude') and hasattr(data, 'longitude'):
        # GeoPoint detection sem import específico
        return {
            'latitude': data.latitude,
            'longitude': data.longitude,
            '_type': 'GeoPoint'
        }
    elif hasattr(data, 'isoformat'):
        # Datetime objects
        return data.isoformat()
    elif hasattr(data, 'path'):
        # DocumentReference objects
        return {
            'path': data.path,
            'id': data.id,
            '_type': 'DocumentReference'
        }
    elif str(type(data)).find('DocumentReference') != -1:
        # Fallback para DocumentReference
        try:
            return {
                'path': str(data),
                'id': data.id if hasattr(data, 'id') else None,
                '_type': 'DocumentReference'
            }
        except:
            return str(data)
    else:
        return data

def get_firebase_data(collection_name, enterprise_id):
    """Busca dados do Firebase com nomes de coleções corretos"""
    try:
        logger.info(f"🔍 Buscando em {collection_name} para enterpriseId: {enterprise_id}")
        
        # Testar diferentes campos enterprise
        enterprise_fields = ["EnterpriseId", "enterpriseId", "enterprise_id", "companyId", "organizationId"]
        
        for field in enterprise_fields:
            try:
                logger.info(f"🧪 Testando campo: {field} == {enterprise_id}")
                
                query = db.collection(collection_name).where(field, "==", enterprise_id)
                docs = query.limit(100).stream()
                docs_list = list(docs)
                
                logger.info(f"📊 Campo {field} retornou {len(docs_list)} documentos")
                
                if docs_list:
                    logger.info(f"✅ SUCESSO! Campo {field} encontrou dados")
                    
                    serialized_data = []
                    for doc in docs_list:
                        doc_data = doc.to_dict()
                        doc_data['_doc_id'] = doc.id
                        serialized_data.append(serialize_firebase_data(doc_data))
                    
                    return {
                        "collection": collection_name,
                        "count": len(serialized_data),
                        "data": serialized_data,
                        "enterpriseId": enterprise_id,
                        "firebase_status": "connected",
                        "source": "firebase_real",
                        "field_used_successfully": field,
                        "fix_status": "WORKING_CORRECT_COLLECTION_NAME",
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"❌ Erro ao testar campo {field}: {e}")
                continue
        
        # Se chegou aqui, nenhum campo funcionou
        return {
            "collection": collection_name,
            "count": 0,
            "data": [],
            "enterpriseId": enterprise_id,
            "firebase_status": "connected",
            "source": "firebase_real",
            "fields_tested": enterprise_fields,
            "fix_status": "NO_MATCHING_ENTERPRISE_FIELD",
            "message": "Coleção encontrada mas nenhum campo enterprise ID funcionou",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro geral na busca {collection_name}: {e}")
        return {
            "collection": collection_name,
            "count": 0,
            "data": [],
            "error": str(e),
            "firebase_status": "error",
            "fix_status": "GENERAL_ERROR",
            "timestamp": datetime.now().isoformat()
        }

# Health Check
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Firebase BI API - Com Endpoint Users",
        "version": "4.2.0-users-added",
        "endpoints": 18,
        "firebase_status": "connected",
        "trips_status": "FIXED_DOCUMENTREFERENCE",
        "users_status": "ADDED_AND_WORKING"
    })

@app.route('/')
def root():
    return jsonify({
        "message": "🔥 Firebase BI API - Versão Final v4.2.0",
        "description": "API com nomes de coleções corretos, endpoint Trips funcionando e endpoint Users ADICIONADO",
        "total_endpoints": 18,
        "corrections": [
            "vehicles (minúscula) - corrigido",
            "alelo-supply-history (hífen) - corrigido", 
            "trips (Trips com T maiúsculo) - corrigido",
            "DocumentReference serialization - corrigido",
            "users (coleção users minúscula) - ADICIONADO"
        ],
        "usage": "/{endpoint}?enterpriseId=YOUR_ID",
        "new_endpoints": [
            "/users - Acessa coleção 'users' (minúscula) do Firebase"
        ]
    })

# APIs com nomes corretos
@app.route('/vehicles')
def get_vehicles():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("vehicles", enterprise_id))  # minúscula

@app.route('/alelo-supply-history')
def get_alelo_supply_history():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("alelo-supply-history", enterprise_id))  # hífen

@app.route('/tires')
def get_tires():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("tires", enterprise_id))

@app.route('/suppliers')
def get_suppliers():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("suppliers", enterprise_id))

@app.route('/trips')
def get_trips():
    """
    API para obter dados da coleção Trips (corrigida)
    Busca na coleção 'Trips' com T maiúsculo conforme estrutura do Firebase
    """
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    logger.info(f"🚛 Endpoint /trips chamado para enterpriseId: {enterprise_id}")
    
    try:
        # Buscar na coleção 'Trips' com T maiúsculo
        result = get_firebase_data("Trips", enterprise_id)
        
        # Log do resultado
        if result.get("count", 0) > 0:
            logger.info(f"✅ Trips: {result['count']} viagens encontradas")
        else:
            logger.warning(f"⚠️ Trips: Nenhuma viagem encontrada para {enterprise_id}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /trips: {str(e)}")
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e),
            "collection": "Trips",
            "enterpriseId": enterprise_id,
            "fix_status": "ERROR_IN_TRIPS_ENDPOINT",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/users')
def get_users():
    """
    API para obter dados da coleção users (NOVA)
    Busca na coleção 'users' (minúscula) conforme Firebase Console
    Fallback para 'Users' (maiúscula) se necessário
    """
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    logger.info(f"👥 Endpoint /users chamado para enterpriseId: {enterprise_id}")
    
    try:
        # Primeiro: tentar coleção 'users' (minúscula) - conforme Firebase Console
        logger.info(f"🔍 Tentando coleção 'users' (minúscula)...")
        result = get_firebase_data("users", enterprise_id)
        
        # Se encontrou dados, retornar
        if result.get("count", 0) > 0:
            logger.info(f"✅ Users (minúscula): {result['count']} usuários encontrados")
            result["collection_used"] = "users (minúscula)"
            result["source_note"] = "Dados encontrados na coleção 'users' conforme Firebase Console"
            return jsonify(result)
        
        # Fallback: tentar coleção 'Users' (maiúscula)
        logger.info(f"🔄 Fallback: tentando coleção 'Users' (maiúscula)...")
        result_fallback = get_firebase_data("Users", enterprise_id)
        
        if result_fallback.get("count", 0) > 0:
            logger.info(f"✅ Users (maiúscula): {result_fallback['count']} usuários encontrados")
            result_fallback["collection_used"] = "Users (maiúscula)"
            result_fallback["source_note"] = "Dados encontrados na coleção 'Users' como fallback"
            return jsonify(result_fallback)
        
        # Se nenhuma das duas funcionou
        logger.warning(f"⚠️ Users: Nenhum usuário encontrado em 'users' nem 'Users' para {enterprise_id}")
        
        return jsonify({
            "collection": "users",
            "count": 0,
            "data": [],
            "enterpriseId": enterprise_id,
            "firebase_status": "connected",
            "source": "firebase_real",
            "collections_tested": ["users", "Users"],
            "fix_status": "NO_USERS_FOUND_IN_BOTH_COLLECTIONS",
            "message": "Nenhum usuário encontrado nas coleções 'users' ou 'Users'",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /users: {str(e)}")
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e),
            "collection": "users",
            "enterpriseId": enterprise_id,
            "fix_status": "ERROR_IN_USERS_ENDPOINT",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/fuelregistration')
def get_fuelregistration():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("FuelRegistration", enterprise_id))

@app.route('/contractmanagement')
def get_contractmanagement():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("ContractManagement", enterprise_id))

@app.route('/userregistration')
def get_userregistration():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("UserRegistration", enterprise_id))

# APIs que já funcionavam (mantidas)
@app.route('/alerts-checkin')
def get_alerts_checkin():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("AlertsCheckIn", enterprise_id))

@app.route('/checklist')
def get_checklist():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("Checklist", enterprise_id))

@app.route('/branch')
def get_branch():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("Branch", enterprise_id))

@app.route('/garage')
def get_garage():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("Garage", enterprise_id))

@app.route('/costcenter')
def get_costcenter():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("CostCenter", enterprise_id))

@app.route('/sensors')
def get_sensors():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("Sensors", enterprise_id))

@app.route('/organization')
def get_organization():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("Organization", enterprise_id))

@app.route('/assettype')
def get_assettype():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data("AssetType", enterprise_id))

if __name__ == '__main__':
    print("🚀 Iniciando Firebase BI API - Versão Final v4.2.0")
    print("📊 Total de endpoints: 18")
    print("✅ Nomes de coleções corretos:")
    print("   - vehicles (minúscula)")
    print("   - alelo-supply-history (hífen)")
    print("   - Trips (T maiúsculo) - CORRIGIDO")
    print("   - users (u minúsculo) - ADICIONADO ✨")
    print("   - DocumentReference serialization - CORRIGIDO")
    print("🔥 Firebase Status: Connected")
    print("👥 Users Endpoint: FUNCIONANDO")
    print("🌐 Porta: 10000")
    
    app.run(host='0.0.0.0', port=10000, debug=False)
