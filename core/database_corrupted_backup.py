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
        logger.info("✅ Supabase REST API connected")
    else:
        logger.warning("⚠️ Supabase credentials not set, using mock mode")
except Exception as e:
    logger.error(f"❌ Supabase connection failed: {e}")
    supabase = None

def save_screening_result(screening_data):
    """
    Save screening result to Supabase
    NOTE: Using YOUR table column names: patient_age, recording_url, status
    """
    if supabase is None:
        logger.warning("⚠️ Supabase not connected, using mock save")
        return {
            "success": True,
            "id": "mock_" + str(hash(str(screening_data)))[:8],
            "note": "Mock save - Supabase not connected"
        }
    
    try:
        # Map your screening data to YOUR table columns
        record = {
            "patient_id": screening_data.get("patient_id", ""),
            "patient_name": screening_data.get("patient_name", ""),
            "patient_age": screening_data.get("age"),  # YOUR column: patient_age
            "recording_url": screening_data.get("audio_filename", ""),  # YOUR column: recording_url
            "status": screening_data.get("prediction", ""),  # YOUR column: status
            "confidence": screening_data.get("confidence"),
            "risk_level": screening_data.get("risk_level", ""),
            "created_at": screening_data.get("created_at", datetime.now().isoformat())
        }
        
        # Insert into Supabase
        response = supabase.table("heart_screenings").insert(record).execute()
        
        if hasattr(response, 'data') and response.data:
            record_id = response.data[0].get('id') if response.data else None
            logger.info(f"✅ Screening saved to database: {record_id}")
            return {
                "success": True,
                "id": record_id,
                "message": "Screening saved successfully"
            }
        else:
            logger.error(f"❌ Database save failed: {response}")
            return {
                "success": False,
                "error": "Database insert failed"
            }
            
    except Exception as e:
        logger.error(f"❌ Error saving screening: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_patient_history(patient_id):
    """
    Get screening history for a patient
    """
    if supabase is None:
        logger.warning("⚠️ Supabase not connected, using mock history")
        return {
            "success": True,
            "history": [],
            "count": 0
        }
    
    try:
        # Query Supabase - using YOUR column names
        response = supabase.table("heart_screenings") \
            .select("*") \
            .eq("patient_id", patient_id) \
            .order("created_at", desc=True) \
            .execute()
        
        if hasattr(response, 'data'):
            # Map back to expected format
            history = []
            for item in response.data:
                history.append({
                    "id": item.get("id"),
                    "patient_id": item.get("patient_id"),
                    "patient_name": item.get("patient_name"),
                    "age": item.get("patient_age"),  # Map: patient_age → age
                    "audio_filename": item.get("recording_url"),  # Map: recording_url → audio_filename
                    "prediction": item.get("status"),  # Map: status → prediction
                    "confidence": item.get("confidence"),
                    "risk_level": item.get("risk_level"),
                    "created_at": item.get("created_at")
                })
            
            logger.info(f"✅ Retrieved {len(history)} records for patient {patient_id}")
            return {
                "success": True,
                "history": history,
                "count": len(history)
            }
        else:
            return {
                "success": False,
                "error": "No data returned",
                "history": [],
                "count": 0
            }
            
    except Exception as e:
        logger.error(f"❌ Error fetching history: {e}")
        return {
            "success": False,
            "error": str(e),
            "history": [],
            "count": 0
        }

def get_system_stats():
    """
    Get system statistics
    """
    if supabase is None:
        logger.warning("⚠️ Supabase not connected, using mock stats")
        return {
            "success": True,
            "stats": {
                "total_screenings": 0,
                "normal_count": 0,
                "abnormal_count": 0
            }
        }
    
    try:
        # Get total count
        total_response = supabase.table("heart_screenings") \
            .select("id", count="exact") \
            .execute()
        
        # Get normal/abnormal counts (using status column)
        normal_response = supabase.table("heart_screenings") \
            .select("id", count="exact") \
            .eq("status", "normal") \
            .execute()
        
        abnormal_response = supabase.table("heart_screenings") \
            .select("id", count="exact") \
            .eq("status", "abnormal") \
            .execute()
        
        total = getattr(total_response, 'count', 0) or 0
        normal = getattr(normal_response, 'count', 0) or 0
        abnormal = getattr(abnormal_response, 'count', 0) or 0
        
        stats = {
            "total_screenings": total,
            "normal_count": normal,
            "abnormal_count": abnormal,
            "abnormal_percentage": round(abnormal / max(total, 1) * 100, 1) if total > 0 else 0,
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info(f"✅ System stats retrieved: {stats}")
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching stats: {e}")
        return {
            "success": False,
            "error": str(e),
            "stats": {}
        }

def check_database_connection():
    """
    Check if database is connected
    """
    if supabase is None:
        return {
            "connected": False,
            "message": "Supabase not initialized"
        }
    
    try:
        response = supabase.table("heart_screenings").select("id", count="exact").limit(1).execute()
        return {
            "connected": True,
            "message": "Database connected and responsive"
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Database error: {str(e)[:100]}"
        }
