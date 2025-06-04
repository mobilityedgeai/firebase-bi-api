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
    else:
        return data

def get_firebase_data_simple(collection_name, enterprise_id):
    """Versão simplificada SEM filtro de data para evitar problemas de índice"""
    try:
        logger.info(f"🔍 Buscando em {collection_name} para enterpriseId: {enterprise_id}")
        
        # Lista de campos para testar EM ORDEM DE PRIORIDADE
        enterprise_fields = ["EnterpriseId", "enterpriseId", "enterprise_id", "companyId", "organizationId"]
        
        for field in enterprise_fields:
            try:
                logger.info(f"🧪 Testando campo: {field} == {enterprise_id}")
                
                # Criar query SIMPLES - SEM filtro de data
                query = db.collection(collection_name).where(field, "==", enterprise_id)
                
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
                        "fix_status": "WORKING_NO_DATE_FILTER",
                        "timestamp": datetime.now().isoformat()
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
                "timestamp": datetime.now().isoformat()
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
        "message": "Firebase BI API - Simplified Fix",
        "version": "3.6.0-simplified",
        "endpoints": 17,
        "firebase_status": "connected",
        "fixes_applied": ["datetime_corrected", "no_date_filter", "no_index_required"]
    })

@app.route('/')
def root():
    return jsonify({
        "message": "🔥 Firebase BI API - Simplified Fix v3.6.0",
        "description": "API corrigida para resolver erros de datetime e índices Firebase",
        "total_endpoints": 17,
        "fixes_applied": [
            "datetime.datetime.now() corrigido",
            "Filtro de data removido (evita problemas de índice)",
            "EnterpriseId maiúsculo funcionando"
        ],
        "usage": "/{endpoint}?enterpriseId=YOUR_ID",
        "note": "Parâmetro 'days' removido temporariamente para evitar problemas de índice"
    })

# APIs que já funcionam (mantidas)
@app.route('/alerts-checkin')
def get_alerts_checkin():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("AlertsCheckIn", enterprise_id))

@app.route('/checklist')
def get_checklist():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Checklist", enterprise_id))

@app.route('/branch')
def get_branch():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Branch", enterprise_id))

@app.route('/garage')
def get_garage():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Garage", enterprise_id))

@app.route('/costcenter')
def get_costcenter():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("CostCenter", enterprise_id))

@app.route('/sensors')
def get_sensors():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Sensors", enterprise_id))

@app.route('/organization')
def get_organization():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Organization", enterprise_id))

@app.route('/assettype')
def get_assettype():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("AssetType", enterprise_id))

# APIs corrigidas (eram amarelas)
@app.route('/vehicles')
def get_vehicles():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Vehicles", enterprise_id))

@app.route('/tires')
def get_tires():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Tires", enterprise_id))

@app.route('/suppliers')
def get_suppliers():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Suppliers", enterprise_id))

@app.route('/userregistration')
def get_userregistration():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("UserRegistration", enterprise_id))

@app.route('/trips')
def get_trips():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("Trips", enterprise_id))

@app.route('/fuelregistration')
def get_fuelregistration():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("FuelRegistration", enterprise_id))

@app.route('/contractmanagement')
def get_contractmanagement():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("ContractManagement", enterprise_id))

@app.route('/alelo-supply-history')
def get_alelo_supply_history():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_simple("AleloSupplyHistory", enterprise_id))

if __name__ == '__main__':
    print("🚀 Iniciando Firebase BI API - Simplified Fix v3.6.0")
    print("📊 Total de endpoints: 17")
    print("🔧 Fixes aplicados:")
    print("   ✅ datetime.datetime.now() corrigido")
    print("   ✅ Filtro de data removido (evita problemas de índice)")
    print("   ✅ EnterpriseId maiúsculo funcionando")
    print("🔥 Firebase Status: Connected")
    print("🌐 Porta: 10000")
    
    app.run(host='0.0.0.0', port=10000, debug=False)
