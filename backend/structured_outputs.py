from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional

class Lib(BaseModel):
    """Library information extraction model for identifying relevant libraries and documentation"""
    
    react: Optional[str] = Field(
        default=None,
        description="React library search query for component-based UI development"
    )
    nodejs: Optional[str] = Field(
        default=None,
        description="Node.js library search query for server-side JavaScript development"
    )
    python: Optional[str] = Field(
        default=None,
        description="Python library search query for Python programming"
    )
    javascript: Optional[str] = Field(
        default=None,
        description="JavaScript library search query for client-side development"
    )
    typescript: Optional[str] = Field(
        default=None,
        description="TypeScript library search query for typed JavaScript development"
    )
    fastapi: Optional[str] = Field(
        default=None,
        description="FastAPI library search query for Python web API development"
    )
    flask: Optional[str] = Field(
        default=None,
        description="Flask library search query for Python web development"
    )
    django: Optional[str] = Field(
        default=None,
        description="Django library search query for Python web framework"
    )
    vue: Optional[str] = Field(
        default=None,
        description="Vue.js library search query for progressive JavaScript framework"
    )
    angular: Optional[str] = Field(
        default=None,
        description="Angular library search query for TypeScript-based web framework"
    )
    express: Optional[str] = Field(
        default=None,
        description="Express.js library search query for Node.js web framework"
    )
    mongodb: Optional[str] = Field(
        default=None,
        description="MongoDB library search query for NoSQL database operations"
    )
    postgresql: Optional[str] = Field(
        default=None,
        description="PostgreSQL library search query for relational database operations"
    )
    docker: Optional[str] = Field(
        default=None,
        description="Docker library search query for containerization"
    )
    kubernetes: Optional[str] = Field(
        default=None,
        description="Kubernetes library search query for container orchestration"
    )
    aws: Optional[str] = Field(
        default=None,
        description="AWS library search query for cloud services"
    )
    azure: Optional[str] = Field(
        default=None,
        description="Azure library search query for Microsoft cloud services"
    )
    gcp: Optional[str] = Field(
        default=None,
        description="Google Cloud Platform library search query for Google cloud services"
    )
    redis: Optional[str] = Field(
        default=None,
        description="Redis library search query for in-memory data structure store"
    )
    elasticsearch: Optional[str] = Field(
        default=None,
        description="Elasticsearch library search query for search and analytics engine"
    )
    
    def to_dict_public(self):
        """Convert to dictionary of public libraries"""
        from libs import lib_names, private_libs
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None and field_name in lib_names and field_name not in private_libs:
                result[field_name] = field_value
        return result
    
    def to_dict_private(self):
        """Convert to dictionary of private libraries"""
        from libs import private_libs
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None and field_name in private_libs:
                result[field_name] = field_value
        return result

class CodeTextSep(BaseModel):
    """Model for separating code and text content"""
    
    code: str = Field(
        description="Extracted code content from the input"
    )
    text: str = Field(
        description="Extracted text/documentation content from the input"
    )
    language: Optional[str] = Field(
        default=None,
        description="Programming language of the extracted code"
    )
    code_type: Optional[str] = Field(
        default=None,
        description="Type of code (e.g., function, class, script, configuration)"
    )

class CodeAnalysis(BaseModel):
    """Model for structured code analysis results"""
    
    corrected_code: str = Field(
        description="Improved version of the code with best practices applied"
    )
    explanation: str = Field(
        description="Detailed explanation of what the code does and improvements made"
    )
    suggestions: list[str] = Field(
        description="List of specific improvement suggestions"
    )
    warnings: list[str] = Field(
        description="List of potential issues or performance concerns"
    )
    complexity_score: Optional[int] = Field(
        default=None,
        description="Complexity score from 1-10 (1 = simple, 10 = very complex)"
    )
    performance_notes: Optional[str] = Field(
        default=None,
        description="Performance optimization notes"
    )
    security_notes: Optional[str] = Field(
        default=None,
        description="Security considerations and recommendations"
    )

class DocumentationQuery(BaseModel):
    """Model for documentation search queries"""
    
    library_name: str = Field(
        description="Name of the library or framework"
    )
    search_terms: list[str] = Field(
        description="List of search terms for documentation lookup"
    )
    version: Optional[str] = Field(
        default=None,
        description="Specific version of the library if relevant"
    )
    context: Optional[str] = Field(
        default=None,
        description="Additional context for the documentation search"
    )