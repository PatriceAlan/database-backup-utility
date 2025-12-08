from pydantic import BaseModel, Field, SecretStr, field_validator
from typing import Optional, List, Dict, Literal
from enum import Enum
from pathlib import Path


# Enums for type safety
class DatabaseType(str, Enum):
    """Supported database types"""
    MYSQL = "mysql"
    POSTGRES = "postgres"
    MONGODB = "mongodb"
    SQLITE = "sqlite"


class StorageType(str, Enum):
    """Supported storage backends"""
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"


class BackupType(str, Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


# Configuration models (nested structure)

class DatabaseConfig(BaseModel):
    """Database connection configuration"""
    type: DatabaseType
    host: str = "localhost"
    port: int = Field(gt=0, le=65535)  # Port validation
    username: str
    password: Optional[SecretStr] = None  # SecretStr hides value in logs
    database: str
    
    # Custom validation
    @field_validator('host')
    @classmethod
    def validate_host(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError('Host cannot be empty')
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "username": "backup_user",
                "database": "production"
            }
        }
    }


class LocalStorageConfig(BaseModel):
    """Local storage configuration"""
    type: Literal[StorageType.LOCAL] = StorageType.LOCAL
    path: Path
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        # Ensure absolute path
        return v.expanduser().resolve()


class S3StorageConfig(BaseModel):
    """AWS S3 storage configuration"""
    type: Literal[StorageType.S3] = StorageType.S3
    bucket: str
    region: str = "us-east-1"
    prefix: str = ""
    access_key_id: Optional[SecretStr] = None  # From env or AWS CLI
    secret_access_key: Optional[SecretStr] = None


class StorageConfig(BaseModel):
    """Storage configuration with multiple backends"""
    default: StorageType
    local: Optional[LocalStorageConfig] = None
    s3: Optional[S3StorageConfig] = None
    # gcs: Optional[GCSStorageConfig] = None  # Add later
    # azure: Optional[AzureStorageConfig] = None


class BackupConfig(BaseModel):
    """Default backup settings"""
    type: BackupType = BackupType.FULL
    compression: Literal["gzip", "bzip2", "xz", "none"] = "gzip"
    retention_days: int = Field(default=30, gt=0)
    timeout_seconds: int = Field(default=3600, gt=0)


class ScheduleConfig(BaseModel):
    """Backup schedule configuration"""
    name: str
    database: str  # Reference to database in databases dict
    cron: str  # Cron expression
    storage: StorageType
    enabled: bool = True
    backup_type: BackupType = BackupType.FULL
    
    @field_validator('cron')
    @classmethod
    def validate_cron(cls, v: str) -> str:
        # TODO: Add cron validation using croniter library
        # For now, basic check
        parts = v.split()
        if len(parts) != 5:
            raise ValueError('Cron must have 5 fields: minute hour day month weekday')
        return v


class SlackNotificationConfig(BaseModel):
    """Slack notification settings"""
    enabled: bool = False
    webhook_url: Optional[SecretStr] = None  # From env
    notify_on: List[Literal["success", "error", "warning"]] = ["error"]


class NotificationConfig(BaseModel):
    """Notification configuration"""
    slack: Optional[SlackNotificationConfig] = None
    # email: Optional[EmailNotificationConfig] = None  # Add later


class AppConfig(BaseModel):
    """Application-level settings"""
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_dir: Path = Path("./logs")
    temp_dir: Path = Path("/tmp/backup-utility")
    max_parallel_backups: int = Field(default=3, gt=0, le=10)


class Config(BaseModel):
    """Root configuration model"""
    databases: Dict[str, DatabaseConfig]
    storage: StorageConfig
    backup: BackupConfig = BackupConfig()  # Default values
    schedules: Optional[List[ScheduleConfig]] = None
    notifications: Optional[NotificationConfig] = None
    app: AppConfig = AppConfig()  # Default values
    
    @field_validator('databases')
    @classmethod
    def validate_databases(cls, v: Dict[str, DatabaseConfig]) -> Dict[str, DatabaseConfig]:
        if not v:
            raise ValueError('At least one database must be configured')
        return v
    
    def get_database(self, name: str) -> DatabaseConfig:
        """Get database config by name"""
        if name not in self.databases:
            raise ValueError(f"Database '{name}' not found in configuration")
        return self.databases[name]
    
    def get_storage(self, storage_type: StorageType) -> BaseModel:
        """Get storage config by type"""
        if storage_type == StorageType.LOCAL:
            if not self.storage.local:
                raise ValueError("Local storage not configured")
            return self.storage.local
        elif storage_type == StorageType.S3:
            if not self.storage.s3:
                raise ValueError("S3 storage not configured")
            return self.storage.s3
        # Add other storage types
        raise ValueError(f"Unsupported storage type: {storage_type}")