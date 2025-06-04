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

def debug_collection_access(collection_name):
    """Debug ultra-detalhado para verificar acesso à coleção"""
    try:
        logger.info(f"🔍 DEBUG: Testando acesso à coleção {collection_name}")
        
        # Teste 1: Verificar se a coleção existe
        try:
            collection_ref = db.collection(collection_name)
            logger.info(f"✅ Coleção {collection_name} referenciada com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao referenciar coleção {collection_name}: {e}")
            return {"error": f"Não foi possível referenciar a coleção {collection_name}"}
        
        # Teste 2: Buscar documentos sem filtro
        try:
            docs = collection_ref.limit(3).stream()
            docs_list = list(docs)
            logger.info(f"📊 Encontrados {len(docs_list)} documentos na coleção {collection_name}")
            
            if not docs_list:
                logger.warning(f"⚠️ Coleção {collection_name} está vazia ou não acessível")
                return {
                    "collection_accessible": True,
                    "documents_found": 0,
                    "message": "Coleção acessível mas vazia"
                }
            
            # Teste 3: Analisar estrutura dos documentos
            debug_docs = []
            for i, doc in enumerate(docs_list):
                try:
                    doc_data = doc.to_dict()
                    
                    # Procurar campos enterprise
                    enterprise_fields = {}
                    all_fields = list(doc_data.keys())
                    
                    for key, value in doc_data.items():
                        if "enterprise" in key.lower():
                            enterprise_fields[key] = value
                    
                    debug_docs.append({
                        "doc_index": i,
                        "doc_id": doc.id,
                        "total_fields": len(all_fields),
                        "all_field_names": all_fields,
                        "enterprise_fields": enterprise_fields
                    })
                    
                    logger.info(f"📄 Doc {i}: ID={doc.id}, Enterprise fields: {enterprise_fields}")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar documento {i}: {e}")
                    debug_docs.append({
                        "doc_index": i,
                        "doc_id": doc.id if hasattr(doc, 'id') else 'unknown',
                        "error": str(e)
                    })
            
            return {
                "collection_accessible": True,
                "documents_found": len(docs_list),
                "debug_documents": debug_docs,
                "message": "Coleção acessível com dados"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar documentos em {collection_name}: {e}")
            return {
                "collection_accessible": True,
                "documents_found": 0,
                "error": str(e),
                "message": "Coleção acessível mas erro na busca"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro geral no debug da coleção {collection_name}: {e}")
        return {
            "collection_accessible": False,
            "error": str(e),
            "message": "Erro geral no acesso à coleção"
        }

def get_firebase_data_ultra_debug(collection_name, enterprise_id):
    """Versão com debug ultra-detalhado"""
    try:
        logger.info(f"🔍 ULTRA DEBUG: Buscando em {collection_name} para enterpriseId: {enterprise_id}")
        
        # Primeiro: Debug completo da coleção
        debug_info = debug_collection_access(collection_name)
        
        if not debug_info.get("collection_accessible", False):
            return {
                "collection": collection_name,
                "count": 0,
                "data": [],
                "enterpriseId": enterprise_id,
                "firebase_status": "error",
                "debug_info": debug_info,
                "fix_status": "COLLECTION_NOT_ACCESSIBLE",
                "timestamp": datetime.now().isoformat()
            }
        
        if debug_info.get("documents_found", 0) == 0:
            return {
                "collection": collection_name,
                "count": 0,
                "data": [],
                "enterpriseId": enterprise_id,
                "firebase_status": "connected",
                "debug_info": debug_info,
                "fix_status": "COLLECTION_EMPTY",
                "timestamp": datetime.now().isoformat()
            }
        
        # Segundo: Tentar buscar com diferentes campos enterprise
        enterprise_fields = ["EnterpriseId", "enterpriseId", "enterprise_id", "companyId", "organizationId"]
        
        for field in enterprise_fields:
            try:
                logger.info(f"🧪 ULTRA DEBUG: Testando campo {field} == {enterprise_id}")
                
                query = db.collection(collection_name).where(field, "==", enterprise_id)
                docs = query.limit(100).stream()
                docs_list = list(docs)
                
                logger.info(f"📊 ULTRA DEBUG: Campo {field} retornou {len(docs_list)} documentos")
                
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
                        "debug_info": debug_info,
                        "fix_status": "WORKING_ULTRA_DEBUG",
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"❌ ULTRA DEBUG: Erro ao testar campo {field}: {e}")
                continue
        
        # Se chegou aqui, nenhum campo funcionou
        return {
            "collection": collection_name,
            "count": 0,
            "data": [],
            "enterpriseId": enterprise_id,
            "firebase_status": "connected",
            "source": "firebase_real",
            "debug_info": debug_info,
            "fields_tested": enterprise_fields,
            "fix_status": "NO_MATCHING_ENTERPRISE_FIELD",
            "message": "Coleção acessível, dados existem, mas nenhum campo enterprise ID funcionou",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ ULTRA DEBUG: Erro geral na busca {collection_name}: {e}")
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
        "message": "Firebase BI API - Ultra Debug",
        "version": "3.7.0-ultra-debug",
        "endpoints": 17,
        "firebase_status": "connected"
    })

@app.route('/')
def root():
    return jsonify({
        "message": "🔥 Firebase BI API - Ultra Debug v3.7.0",
        "description": "API com debug ultra-detalhado para investigar problema da coleção Vehicles",
        "total_endpoints": 17,
        "debug_features": [
            "Verificação de acesso à coleção",
            "Análise de estrutura dos documentos",
            "Listagem de todos os campos",
            "Debug de campos enterprise"
        ],
        "usage": "/{endpoint}?enterpriseId=YOUR_ID"
    })

# API com ultra debug
@app.route('/vehicles')
def get_vehicles():
    enterprise_id = request.args.get('enterpriseId')
    
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    
    return jsonify(get_firebase_data_ultra_debug("Vehicles", enterprise_id))

# Outras APIs mantidas com função simples
@app.route('/alerts-checkin')
def get_alerts_checkin():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("AlertsCheckIn", enterprise_id))

@app.route('/checklist')
def get_checklist():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("Checklist", enterprise_id))

@app.route('/branch')
def get_branch():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("Branch", enterprise_id))

@app.route('/garage')
def get_garage():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("Garage", enterprise_id))

@app.route('/costcenter')
def get_costcenter():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("CostCenter", enterprise_id))

@app.route('/sensors')
def get_sensors():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("Sensors", enterprise_id))

@app.route('/organization')
def get_organization():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("Organization", enterprise_id))

@app.route('/assettype')
def get_assettype():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("AssetType", enterprise_id))

@app.route('/tires')
def get_tires():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("Tires", enterprise_id))

@app.route('/suppliers')
def get_suppliers():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("Suppliers", enterprise_id))

@app.route('/userregistration')
def get_userregistration():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("UserRegistration", enterprise_id))

@app.route('/trips')
def get_trips():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("Trips", enterprise_id))

@app.route('/fuelregistration')
def get_fuelregistration():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("FuelRegistration", enterprise_id))

@app.route('/contractmanagement')
def get_contractmanagement():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("ContractManagement", enterprise_id))

@app.route('/alelo-supply-history')
def get_alelo_supply_history():
    enterprise_id = request.args.get('enterpriseId')
    if not enterprise_id:
        return jsonify({"error": "enterpriseId é obrigatório"}), 400
    return jsonify(get_firebase_data_ultra_debug("AleloSupplyHistory", enterprise_id))

if __name__ == '__main__':
    print("🚀 Iniciando Firebase BI API - Ultra Debug v3.7.0")
    print("📊 Total de endpoints: 17")
    print("🔍 Debug ultra-detalhado ativado")
    print("🔥 Firebase Status: Connected")
    print("🌐 Porta: 10000")
    
    app.run(host='0.0.0.0', port=10000, debug=False)
