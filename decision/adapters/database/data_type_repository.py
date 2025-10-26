"""PostgreSQL repository implementation for data types."""

from typing import List, Optional, ContextManager
from contextlib import contextmanager
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import json
from datetime import datetime
from domain.data_type_models import DataTypeModel
from domain.data_type_repository import DataTypeRepository

logger = logging.getLogger(__name__)


class PostgreSQLDataTypeRepository(DataTypeRepository):
    """PostgreSQL implementation of data type repository."""
    
    def __init__(self):
        self._pool = None
    
    @property
    def pool(self):
        """Lazy initialization of connection pool."""
        if self._pool is None:
            db_url = os.getenv('DATABASE_URL', 'postgresql://frauduser:fraudpass@postgres:5432/frauddb')
            self._pool = SimpleConnectionPool(1, 10, db_url)
        return self._pool
    
    @contextmanager
    def get_db(self):
        """Get database connection from pool."""
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)
    
    def initialize_schema(self):
        """Initialize database table."""
        try:
            with self.get_db() as conn:
                cur = conn.cursor()
                
                # Create data_types table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_types (
                        data_type VARCHAR(100) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        schema_definition JSONB NOT NULL,
                        sample_data JSONB,
                        status VARCHAR(50) DEFAULT 'ACTIVE',
                        created_by VARCHAR(255) NOT NULL,
                        updated_by VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                logger.info("Data types table initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize data types table: {e}")
            raise
    
    def create(self, data_type: DataTypeModel) -> DataTypeModel:
        """Create a new data type."""
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO data_types (
                    data_type, name, description, schema_definition, sample_data,
                    status, created_by, updated_by, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data_type.data_type,
                data_type.name,
                data_type.description,
                json.dumps(data_type.schema_definition),
                json.dumps(data_type.sample_data) if data_type.sample_data else None,
                data_type.status,
                data_type.created_by,
                data_type.updated_by,
                data_type.created_at,
                data_type.updated_at
            ))
            return data_type
    
    def get_by_id(self, data_type: str) -> Optional[DataTypeModel]:
        """Get data type by identifier."""
        with self.get_db() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT * FROM data_types WHERE data_type = %s
            """, (data_type,))
            row = cur.fetchone()
            if row:
                row['schema_definition'] = json.loads(row['schema_definition'])
                row['sample_data'] = json.loads(row['sample_data']) if row.get('sample_data') else None
                return DataTypeModel(**row)
            return None
    
    def get_all(self) -> List[DataTypeModel]:
        """Get all data types."""
        with self.get_db() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM data_types ORDER BY created_at DESC")
            rows = cur.fetchall()
            result = []
            for row in rows:
                row['schema_definition'] = json.loads(row['schema_definition'])
                row['sample_data'] = json.loads(row['sample_data']) if row.get('sample_data') else None
                result.append(DataTypeModel(**row))
            return result
    
    def update(self, data_type: str, data_type_model: DataTypeModel) -> Optional[DataTypeModel]:
        """Update an existing data type."""
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE data_types
                SET name = %s, description = %s, schema_definition = %s, sample_data = %s,
                    status = %s, updated_by = %s, updated_at = %s
                WHERE data_type = %s
            """, (
                data_type_model.name,
                data_type_model.description,
                json.dumps(data_type_model.schema_definition),
                json.dumps(data_type_model.sample_data) if data_type_model.sample_data else None,
                data_type_model.status,
                data_type_model.updated_by,
                data_type_model.updated_at,
                data_type
            ))
            return self.get_by_id(data_type)
    
    def delete(self, data_type: str) -> bool:
        """Delete a data type."""
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM data_types WHERE data_type = %s", (data_type,))
            return cur.rowcount > 0
    
    def exists(self, data_type: str) -> bool:
        """Check if data type exists."""
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM data_types WHERE data_type = %s", (data_type,))
            return cur.fetchone()[0] > 0
