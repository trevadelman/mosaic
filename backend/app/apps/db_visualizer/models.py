from pydantic import BaseModel
from typing import List, Optional

class TableInfo(BaseModel):
    name: str
    columns: List[str]
    foreign_keys: List[dict]  # {column: referenced_table.column}
    primary_key: str

class DatabaseStructure(BaseModel):
    tables: List[TableInfo]
    relationships: List[dict]  # {source: table.column, target: table.column}

class GraphNode(BaseModel):
    id: str
    group: str  # 'table' or 'column'
    label: str

class GraphLink(BaseModel):
    source: str
    target: str
    type: str  # 'contains' for table->column, 'references' for foreign keys

class GraphData(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]
