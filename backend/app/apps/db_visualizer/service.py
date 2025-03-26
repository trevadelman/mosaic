import sqlite3
from typing import List, Dict
import logging
from sqlalchemy import inspect, MetaData, create_engine
from sqlalchemy.orm import Session
from .models import TableInfo, DatabaseStructure, GraphData, GraphNode, GraphLink

logger = logging.getLogger(__name__)

class DatabaseVisualizerService:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    def get_database_structure(self) -> DatabaseStructure:
        """Extract database structure including tables, columns, and relationships."""
        tables: List[TableInfo] = []
        relationships: List[dict] = []

        inspector = inspect(self.engine)
        
        for table_name in inspector.get_table_names():
            # Get columns
            columns = [col["name"] for col in inspector.get_columns(table_name)]
            
            # Get primary key
            pk = inspector.get_pk_constraint(table_name)
            primary_key = pk["constrained_columns"][0] if pk["constrained_columns"] else ""
            
            # Get foreign keys
            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                fks.append({
                    "column": fk["constrained_columns"][0],
                    "reference": f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                })
                relationships.append({
                    "source": f"{table_name}.{fk['constrained_columns'][0]}",
                    "target": f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                })
            
            tables.append(TableInfo(
                name=table_name,
                columns=columns,
                foreign_keys=fks,
                primary_key=primary_key
            ))

        return DatabaseStructure(
            tables=tables,
            relationships=relationships
        )

    def get_graph_data(self) -> GraphData:
        """Convert database structure to D3 force graph format."""
        db_structure = self.get_database_structure()
        nodes: List[GraphNode] = []
        links: List[GraphLink] = []
        
        # Add table nodes
        for table in db_structure.tables:
            # Add table node
            nodes.append(GraphNode(
                id=table.name,
                group="table",
                label=table.name
            ))
            
            # Add column nodes
            for column in table.columns:
                column_id = f"{table.name}.{column}"
                nodes.append(GraphNode(
                    id=column_id,
                    group="column",
                    label=column
                ))
                
                # Add link from table to column
                links.append(GraphLink(
                    source=table.name,
                    target=column_id,
                    type="contains"
                ))
        
        # Add relationship links
        for rel in db_structure.relationships:
            links.append(GraphLink(
                source=rel["source"],
                target=rel["target"],
                type="references"
            ))
        
        return GraphData(nodes=nodes, links=links)

    def get_table_details(self, table_name: str) -> Dict:
        """Get detailed information about a specific table."""
        inspector = inspect(self.engine)
        
        if table_name not in inspector.get_table_names():
            raise ValueError(f"Table {table_name} not found")
        
        columns = inspector.get_columns(table_name)
        pk = inspector.get_pk_constraint(table_name)
        fks = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        return {
            "name": table_name,
            "columns": [{
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
                "default": str(col["default"]) if col["default"] else None,
                "is_primary_key": col["name"] in (pk["constrained_columns"] if pk else [])
            } for col in columns],
            "primary_key": pk["constrained_columns"] if pk else [],
            "foreign_keys": [{
                "column": fk["constrained_columns"][0],
                "references": {
                    "table": fk["referred_table"],
                    "column": fk["referred_columns"][0]
                }
            } for fk in fks],
            "indexes": [{
                "name": idx["name"],
                "columns": idx["column_names"],
                "unique": idx["unique"]
            } for idx in indexes]
        }

    def get_table_data(self, table_name: str, page: int = 1, page_size: int = 50) -> Dict:
        """Get paginated data from a specific table."""
        inspector = inspect(self.engine)
        
        if table_name not in inspector.get_table_names():
            raise ValueError(f"Table {table_name} not found")
        
        # Get column information
        columns = inspector.get_columns(table_name)
        column_names = [col["name"] for col in columns]
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Build and execute query
        with self.engine.connect() as connection:
            from sqlalchemy import text
            
            # Get total count
            count_query = text(f"SELECT COUNT(*) FROM \"{table_name}\"")
            count_result = connection.execute(count_query)
            total_count = count_result.scalar()
            
            # Get paginated data
            columns_str = ", ".join(f"\"{col}\"" for col in column_names)
            query = text(f"SELECT {columns_str} FROM \"{table_name}\" LIMIT :limit OFFSET :offset")
            result = connection.execute(query, {"limit": page_size, "offset": offset})
            
            # Convert rows to dictionaries with proper JSON serialization
            def serialize_value(value):
                if hasattr(value, 'isoformat'):  # Handle datetime objects
                    return value.isoformat()
                if isinstance(value, (dict, list)):  # Handle JSON/JSONB fields
                    return value
                return str(value) if value is not None else None

            rows = [
                {col: serialize_value(val) for col, val in zip(column_names, row)}
                for row in result
            ]
            
            return {
                "columns": column_names,
                "rows": rows,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
