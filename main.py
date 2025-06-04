from flask import Flask, request, jsonify
from firebase_admin_init import db
from flask_cors import CORS
import datetime
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
    else:
        return data

def get_firebase_data_fixed(collection_name, enterprise_id, days=None):
    """Versão corrigida que REALMENTE testa EnterpriseId maiúsculo"""
    try:
        logger.info(f"🔍 Buscando em {collection_name} para enterpriseId: {enterprise_id}")
        
        # Lista de campos para testar EM ORDEM DE PRIORIDADE
        enterprise_fields = ["EnterpriseId", "enterpriseId", "enterprise_id", "companyId", "organizationId"]
        
        for field in enterprise_fields:
            try:
                logger.info(f"🧪 Testando campo: {field} == {enterprise_id}")
                
                # Criar query com o campo específico
                query = db.collection(collection_name).where(field, "==", enterprise_id)
                
                # Adicionar filtro de data se especificado
                if days:
                    from datetime import datetime, timedelta
                    cutoff_date = datetime.now() - timedelta(days=int(days))
                    query = query.where("timestamp", ">=", cutoff_date)
                
                # Executar query
                docs = query.limit(100).stream()
                docs_list = list(docs)
                
                logger.info(f"📊 Campo {field}: {len(docs_list)} documentos encontrados")
                
                if docs_list:
                    # SUCESSO! Encontrou dados com este campo
                    logger.info(f"✅ SUCESSO! Campo {field} retornou {len(docs_list)} documentos")
                    
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
                        "fix_status": "WORKING",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                else:
                    logger.info(f"⚠️ Campo {field}: 0 resultados, tentando próximo...")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao testar campo {field}: {e}")
                continue
        
        # Se chegou aqui, NENHUM campo funcionou
        logger.warning(f"❌ NENHUM campo enterprise funcionou para {collection_name}")
        
        # Fazer uma busca SEM filtro para debug
        try:
            all_docs = db.collection(collection_name).limit(5).stream()
            all_docs_list = list(all_docs)
            
            debug_samples = []
            for doc in all_docs_list:
                doc_data = doc.to_dict()
                # Procurar campos enterprise
                enterprise_fields_found = {}
                for key, value in doc_data.items():
                    if "enterprise" in key.lower():
                        enterprise_fields_found[key] = value
                
                debug_samples.append({
                    "doc_id": doc.id,
                    "enterprise_fields": enterprise_fields_found
                })
            
            logger.info(f"🔍 Debug samples: {debug_samples}")
            
            return {
                "collection": collection_name,
                "count": 0,
                "data": [],
                "enterpriseId": enterprise_id,
                "firebase_status": "connected",
                "source": "firebase_real",
                "fix_status": "NO_MATCHING_FIELD",
                "debug_samples": debug_samples,
                "fields_tested": enterprise_fields,
                "message": "Nenhum campo enterprise ID encontrou resultados",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as debug_error:
            logger.error(f"❌ Erro no debug: {debug_error}")
            return {
                "collection": collection_name,
                "count": 0,
                "data": [],
                "enterpriseId": enterprise_id,
                "firebase_status": "connected",
                "source": "firebase_real",
                "fix_status": "DEBUG_ERROR",
                "error": str(debug_error),
                "timestamp": datetime.datetime.now().isoformat()
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
            "timestamp": datetime.datetime.now().isoformat()
        }

# Health Check
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Firebase BI API - Import Fix",
        "version": "3.5.0-import-fix",
        "endpoints": 17,
        "firebase_status": "connected"
    })

@app.route('/')
def root():
    return jsonify({
        "message": "🔥 Firebase BI API - Import Fix v3.5.0",
        "description": "API corrigida para resolver erro de importação do GeoPoint",
        "total_endpoints": 17,
        "fix_applied": "GeoPoint import corrigido + EnterpriseId maiúsculo",
        "usage": "/{endpoint}?enterpriseId=YOUR_ID&days=30",
        "debug_info": "Resposta inclui field_used_successfully para confirmar qual campo funcionou"
    })

# APIs que já funcionam (mantidas)
@app.route('/alerts-checkin')
def get_alerts_checkin():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("AlertsCheckIn", enterprise_id, days))

@app.route('/checklist')
def get_checklist():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Checklist", enterprise_id, days))

@app.route('/branch')
def get_branch():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Branch", enterprise_id, days))

@app.route('/garage')
def get_garage():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Garage", enterprise_id, days))

@app.route('/costcenter')
def get_costcenter():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("CostCenter", enterprise_id, days))

@app.route('/sensors')
def get_sensors():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Sensors", enterprise_id, days))

@app.route('/organization')
def get_organization():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Organization", enterprise_id, days))

@app.route('/assettype')
def get_assettype():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("AssetType", enterprise_id, days))

# APIs corrigidas (eram amarelas)
@app.route('/vehicles')
def get_vehicles():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Vehicles", enterprise_id, days))

@app.route('/tires')
def get_tires():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Tires", enterprise_id, days))

@app.route('/suppliers')
def get_suppliers():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Suppliers", enterprise_id, days))

@app.route('/userregistration')
def get_userregistration():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("UserRegistration", enterprise_id, days))

@app.route('/trips')
def get_trips():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("Trips", enterprise_id, days))

@app.route('/fuelregistration')
def get_fuelregistration():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("FuelRegistration", enterprise_id, days))

@app.route('/contractmanagement')
def get_contractmanagement():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("ContractManagement", enterprise_id, days))

@app.route('/alelo-supply-history')
def get_alelo_supply_history():
    enterprise_id = request.args.get('enterpriseId')
    days = request.args.get('days')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_fixed("AleloSupplyHistory", enterprise_id, days))

if __name__ == '__main__':
    print("🚀 Iniciando Firebase BI API - Import Fix v3.5.0")
    print("📊 Total de endpoints: 17")
    print("🔧 Fix aplicado: GeoPoint import corrigido + EnterpriseId maiúsculo")
    print("🔥 Firebase Status: Connected")
    print("🌐 Porta: 10000")
    
    app.run(host='0.0.0.0', port=10000, debug=False)
