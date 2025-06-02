"""
File-based Ranking Storage - Dự phòng cho MongoDB
Lưu trữ dữ liệu ranking vào file JSON để tránh mất dữ liệu khi restart
"""

import json
import os
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
import pytz

# Vietnam timezone
VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

class FileRankingStorage:
    def __init__(self):
        self.data_dir = "data"
        self.ranking_file = os.path.join(self.data_dir, "ranking_data.json")
        self.backup_file = os.path.join(self.data_dir, "ranking_backup.json")
        self.stats_file = os.path.join(self.data_dir, "ranking_stats.json")
        self.auto_save_task = None
        self.save_interval = 30  # Save every 30 seconds
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
    def get_vietnam_time(self):
        """Get current Vietnam time"""
        return datetime.now(VIETNAM_TZ)
    
    def get_vietnam_datetime_str(self):
        """Get Vietnam datetime string"""
        return self.get_vietnam_time().strftime("%d/%m/%Y %H:%M:%S")
    
    def _serialize_datetime(self, obj):
        """Custom JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return {
                "__datetime__": True,
                "timestamp": obj.timestamp(),
                "timezone": str(obj.tzinfo) if obj.tzinfo else None
            }
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _deserialize_datetime(self, obj):
        """Custom JSON deserializer for datetime objects"""
        if isinstance(obj, dict) and obj.get("__datetime__"):
            dt = datetime.fromtimestamp(obj["timestamp"])
            if obj.get("timezone") == "Asia/Ho_Chi_Minh":
                dt = VIETNAM_TZ.localize(dt.replace(tzinfo=None))
            return dt
        return obj
    
    def _process_data_for_save(self, data):
        """Process data to handle datetime objects before saving"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, datetime):
                    result[key] = self._serialize_datetime(value)
                elif isinstance(value, dict):
                    result[key] = self._process_data_for_save(value)
                elif isinstance(value, list):
                    result[key] = [self._process_data_for_save(item) for item in value]
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            return [self._process_data_for_save(item) for item in data]
        elif isinstance(data, datetime):
            return self._serialize_datetime(data)
        else:
            return data
    
    def _process_data_after_load(self, data):
        """Process data to restore datetime objects after loading"""
        if isinstance(data, dict):
            if data.get("__datetime__"):
                return self._deserialize_datetime(data)
            result = {}
            for key, value in data.items():
                result[key] = self._process_data_after_load(value)
            return result
        elif isinstance(data, list):
            return [self._process_data_after_load(item) for item in data]
        else:
            return data
    
    async def save_ranking_data(self, current_data: Dict):
        """Save ranking data to JSON file"""
        try:
            # Add metadata
            save_data = {
                "timestamp": self.get_vietnam_time(),
                "vietnam_datetime": self.get_vietnam_datetime_str(),
                "version": "1.0",
                "data": current_data
            }
            
            # Process datetime objects
            processed_data = self._process_data_for_save(save_data)
            
            # Save to main file
            with open(self.ranking_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Create backup
            if os.path.exists(self.ranking_file):
                with open(self.backup_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ Saved ranking data to file at {self.get_vietnam_datetime_str()}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving ranking data to file: {e}")
            return False
    
    async def load_ranking_data(self):
        """Load ranking data from JSON file"""
        try:
            file_to_load = self.ranking_file
            
            # Try backup if main file doesn't exist or is corrupted
            if not os.path.exists(file_to_load):
                if os.path.exists(self.backup_file):
                    file_to_load = self.backup_file
                    print("📁 Loading from backup file")
                else:
                    print("📭 No existing ranking data found")
                    return {}
            
            with open(file_to_load, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Process datetime objects
            processed_data = self._process_data_after_load(raw_data)
            
            # Extract the actual ranking data
            ranking_data = processed_data.get("data", {})
            
            # Validate data structure
            expected_keys = ["today", "week", "month", "daily_7days"]
            for key in expected_keys:
                if key not in ranking_data:
                    ranking_data[key] = {}
            
            print(f"✅ Loaded ranking data from file ({file_to_load})")
            print(f"📊 Data stats: today={len(ranking_data['today'])}, week={len(ranking_data['week'])}, month={len(ranking_data['month'])}")
            
            return ranking_data
            
        except Exception as e:
            print(f"❌ Error loading ranking data from file: {e}")
            return {}
    
    async def save_stats(self, stats_data: Dict):
        """Save statistics to file"""
        try:
            stats_with_metadata = {
                "timestamp": self.get_vietnam_time(),
                "vietnam_datetime": self.get_vietnam_datetime_str(),
                "stats": stats_data
            }
            
            processed_stats = self._process_data_for_save(stats_with_metadata)
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(processed_stats, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving stats: {e}")
            return False
    
    async def load_stats(self):
        """Load statistics from file"""
        try:
            if not os.path.exists(self.stats_file):
                return {}
            
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            processed_data = self._process_data_after_load(raw_data)
            return processed_data.get("stats", {})
            
        except Exception as e:
            print(f"❌ Error loading stats: {e}")
            return {}
    
    def start_auto_save(self, current_data_ref):
        """Start automatic saving"""
        if self.auto_save_task is None or self.auto_save_task.done():
            self.auto_save_task = asyncio.create_task(
                self._auto_save_loop(current_data_ref)
            )
            print(f"🔄 File auto-save started (interval: {self.save_interval}s)")
    
    async def _auto_save_loop(self, current_data_ref):
        """Auto-save loop"""
        while True:
            try:
                await asyncio.sleep(self.save_interval)
                
                # Save current data
                await self.save_ranking_data(current_data_ref)
                
                # Cleanup old backups
                await self._cleanup_old_files()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ File auto-save error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_files(self):
        """Cleanup old backup files"""
        try:
            # Keep only recent files
            backup_pattern = "ranking_backup_"
            data_files = [f for f in os.listdir(self.data_dir) if f.startswith(backup_pattern)]
            
            if len(data_files) > 5:  # Keep only 5 recent backups
                data_files.sort()
                for old_file in data_files[:-5]:
                    old_path = os.path.join(self.data_dir, old_file)
                    os.remove(old_path)
                    
        except Exception as e:
            print(f"⚠️ Error cleaning up old files: {e}")
    
    async def create_manual_backup(self, current_data: Dict, backup_name: str = None):
        """Create manual backup with custom name"""
        try:
            if not backup_name:
                backup_name = f"ranking_backup_{self.get_vietnam_time().strftime('%Y%m%d_%H%M%S')}.json"
            
            backup_path = os.path.join(self.data_dir, backup_name)
            
            backup_data = {
                "timestamp": self.get_vietnam_time(),
                "vietnam_datetime": self.get_vietnam_datetime_str(),
                "backup_type": "manual",
                "data": current_data
            }
            
            processed_data = self._process_data_for_save(backup_data)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ Created manual backup: {backup_name}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Error creating manual backup: {e}")
            return None
    
    def get_file_info(self):
        """Get information about stored files"""
        info = {
            "data_directory": self.data_dir,
            "files": {},
            "vietnam_time": self.get_vietnam_datetime_str()
        }
        
        files_to_check = [
            ("ranking_data", self.ranking_file),
            ("ranking_backup", self.backup_file),
            ("ranking_stats", self.stats_file)
        ]
        
        for name, filepath in files_to_check:
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                info["files"][name] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
                }
            else:
                info["files"][name] = {"exists": False}
        
        return info
    
    async def shutdown(self):
        """Graceful shutdown"""
        try:
            if self.auto_save_task:
                self.auto_save_task.cancel()
            
            print(f"✅ File ranking storage shutdown complete at {self.get_vietnam_datetime_str()}")
            
        except Exception as e:
            print(f"❌ Error during file storage shutdown: {e}")

# Global instance
file_storage = FileRankingStorage()

# Public functions
async def save_ranking_to_file(current_data: Dict):
    """Save ranking data to file"""
    return await file_storage.save_ranking_data(current_data)

async def load_ranking_from_file():
    """Load ranking data from file"""
    return await file_storage.load_ranking_data()

async def create_ranking_backup(current_data: Dict, backup_name: str = None):
    """Create manual backup"""
    return await file_storage.create_manual_backup(current_data, backup_name)

def start_file_auto_save(current_data_ref):
    """Start automatic file saving"""
    file_storage.start_auto_save(current_data_ref)

def get_file_storage_info():
    """Get file storage information"""
    return file_storage.get_file_info()

async def shutdown_file_storage():
    """Shutdown file storage"""
    await file_storage.shutdown()

print("✅ File ranking storage loaded (JSON backup system)")