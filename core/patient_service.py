import os
import json
from supabase import create_client, Client
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Client = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        logger.warning("⚠️ Supabase credentials not set, using mock mode")
except Exception as e:
    logger.error(f"❌ Supabase connection failed: {e}")
    supabase = None

def register_patient(patient_data):
    """
    Register a new patient
    Accepts either 'name' or 'full_name' field
    """
    if supabase is None:
        logger.warning("⚠️ Using mock patient registration")
        return {
            "success": True,
            "patient_id": patient_data.get("patient_id", "mock_patient"),
            "message": "Mock registration - database not connected"
        }
    
    try:
        # Handle both 'name' and 'full_name' fields
        full_name = patient_data.get("full_name") or patient_data.get("name") or ""
        
        if not full_name:
            return {
                "success": False,
                "error": "Missing required fields: full_name or name"
            }
        
        # Prepare patient record
        record = {
            "patient_id": patient_data.get("patient_id", ""),
            "name": full_name,
            "age": patient_data.get("age"),
            "gender": patient_data.get("gender", ""),
            "phone": patient_data.get("phone", ""),
            "created_at": datetime.now().isoformat()
        }
        
        # Insert into Supabase
        response = supabase.table("patients").insert(record).execute()
        
        if hasattr(response, 'data') and response.data:
            logger.info(f"✅ Patient registered: {record['patient_id']}")
            return {
                "success": True,
                "patient_id": record["patient_id"],
                "name": full_name,
                "message": "Patient registered successfully"
            }
        else:
            logger.error(f"❌ Patient registration failed")
            return {
                "success": False,
                "error": "Database insert failed"
            }
            
    except Exception as e:
        logger.error(f"❌ Error registering patient: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def check_patient_exists(patient_id):
    """
    Check if patient exists
    """
    if supabase is None:
        return {
            "exists": False,
            "patient_id": patient_id,
            "note": "Mock check - database not connected"
        }
    
    try:
        response = supabase.table("patients") \
            .select("patient_id", "name") \
            .eq("patient_id", patient_id) \
            .execute()
        
        exists = len(response.data) > 0 if hasattr(response, 'data') else False
        
        return {
            "exists": exists,
            "patient_id": patient_id,
            "name": response.data[0].get("name") if exists and response.data else None
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking patient: {e}")
        return {
            "exists": False,
            "patient_id": patient_id,
            "error": str(e)
        }

def get_patient_details(patient_id):
    """
    Get patient details
    """
    if supabase is None:
        return {
            "success": False,
            "error": "Database not connected",
            "patient_id": patient_id
        }
    
    try:
        response = supabase.table("patients") \
            .select("*") \
            .eq("patient_id", patient_id) \
            .execute()
        
        if hasattr(response, 'data') and response.data:
            patient = response.data[0]
            return {
                "success": True,
                "patient": patient
            }
        else:
            return {
                "success": False,
                "error": "Patient not found",
                "patient_id": patient_id
            }
            
    except Exception as e:
        logger.error(f"❌ Error getting patient details: {e}")
        return {
            "success": False,
            "error": str(e),
            "patient_id": patient_id
        }
