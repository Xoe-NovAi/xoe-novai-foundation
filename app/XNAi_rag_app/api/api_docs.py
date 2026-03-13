"""
Griffe API Documentation Extensions
====================================

Automatic API documentation generation and code-aware retrieval
for intelligent AI assistance with technical code questions.

Week 2 Implementation - January 18-19, 2026
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional, Set, Tuple, TYPE_CHECKING, Union
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Type checking imports - MUST be available at runtime for type hints
if TYPE_CHECKING:
    try:
        from griffe import Module, Function, Class, Attribute
        from griffe.dataclasses import Docstring
    except ImportError:
        # Fallback type hints when griffe is not available
        Module = Any
        Function = Any
        Class = Any
        Attribute = Any
        Docstring = Any

try:
    from griffe import GriffeLoader, Module, Function, Class, Attribute
    from griffe.dataclasses import Docstring
    GRIFFE_AVAILABLE = True
except ImportError:
    # Create dummy classes for runtime when griffe is not available
    class Module:
        pass
    class Function:
        pass
    class Class:
        pass
    class Attribute:
        pass
    class Docstring:
        pass
    GriffeLoader = None
    GRIFFE_AVAILABLE = False
    logger.warning("Griffe not available - API documentation features disabled")

from langchain_core.documents import Document

@dataclass
class APIDocumentation:
    """Structured API documentation for a code element."""
    name: str
    qualified_name: str
    type: str  # 'module', 'class', 'function', 'attribute'
    docstring: str
    signature: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    returns: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    parent_class: Optional[str] = None
    decorators: Optional[List[str]] = None
    base_classes: Optional[List[str]] = None
    methods: Optional[List[str]] = None

    def to_document(self) -> Document:
        """Convert to LangChain Document for RAG indexing."""
        content = f"""
# {self.qualified_name}

**Type:** {self.type}
**File:** {self.file_path or 'Unknown'}
**Line:** {self.line_number or 'Unknown'}

## Documentation

{self.docstring or 'No documentation available.'}

{f"## Signature\\n\\n```python\\n{self.signature}\\n```" if self.signature else ""}

{f"## Parameters\\n\\n" + "\\n".join([f"- `{p.get('name', 'unknown')}`: {p.get('description', 'No description')}" for p in (self.parameters or [])]) if self.parameters else ""}

{f"## Returns\\n\\n{self.returns.get('description', 'No return description') if self.returns else 'No return information'}" if self.returns else ""}

{f"## Methods\\n\\n" + "\\n".join([f"- `{method}`" for method in (self.methods or [])]) if self.methods else ""}

{f"## Base Classes\\n\\n" + "\\n".join([f"- `{base}`" for base in (self.base_classes or [])]) if self.base_classes else ""}
        """.strip()

        metadata = {
            "source": f"api_docs:{self.qualified_name}",
            "type": "api_documentation",
            "api_type": self.type,
            "qualified_name": self.qualified_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "parent_class": self.parent_class,
            "category": "api_reference",
            "tags": ["api", "code", "documentation", self.type]
        }

        return Document(
            page_content=content,
            metadata=metadata
        )

class APIDocumentationGenerator:
    """
    Griffe-based API documentation generator.

    Automatically extracts API documentation from Python codebases
    and prepares it for RAG indexing and AI assistance.
    """

    def __init__(self, source_paths: List[str] = None):
        if not GRIFFE_AVAILABLE:
            raise ImportError("Griffe is required for API documentation generation")

        self.source_paths = source_paths or ["app"]
        self.loader = GriffeLoader()
        self.modules: Dict[str, Module] = {}
        self.api_docs: List[APIDocumentation] = []

        logger.info(f"API documentation generator initialized for paths: {self.source_paths}")

    def load_modules(self) -> Dict[str, Any]:
        """
        Load and parse Python modules using Griffe.

        Returns:
            Dict of module_name -> Module objects
        """
        for path in self.source_paths:
            try:
                # Load modules from path
                modules = self.loader.load_module(Path(path))
                if modules:
                    self.modules[modules.name] = modules
                    logger.info(f"Loaded module: {modules.name}")
            except Exception as e:
                logger.warning(f"Failed to load module from {path}: {e}")

        return self.modules

    def extract_api_documentation(self) -> List[APIDocumentation]:
        """
        Extract comprehensive API documentation from loaded modules.

        Returns:
            List of APIDocumentation objects
        """
        api_docs = []

        for module_name, module in self.modules.items():
            try:
                # Extract module-level documentation
                api_docs.extend(self._extract_module_docs(module))

                # Extract all functions, classes, and attributes
                api_docs.extend(self._extract_functions(module))
                api_docs.extend(self._extract_classes(module))
                api_docs.extend(self._extract_attributes(module))

            except Exception as e:
                logger.error(f"Failed to extract docs from {module_name}: {e}")

        self.api_docs = api_docs
        logger.info(f"Extracted {len(api_docs)} API documentation items")

        return api_docs

    def _extract_module_docs(self, module: Module) -> List[APIDocumentation]:
        """Extract module-level documentation."""
        docs = []

        try:
            doc = APIDocumentation(
                name=module.name.split('.')[-1],
                qualified_name=module.name,
                type="module",
                docstring=self._extract_docstring(module.docstring),
                file_path=str(module.filepath) if module.filepath else None,
                line_number=getattr(module, 'lineno', None)
            )
            docs.append(doc)
        except Exception as e:
            logger.debug(f"Failed to extract module docs for {module.name}: {e}")

        return docs

    def _extract_functions(self, module: Module) -> List[APIDocumentation]:
        """Extract function documentation."""
        docs = []

        for name, function in module.functions.items():
            try:
                # Get parameters
                parameters = self._extract_parameters(function)

                # Get return info
                returns = self._extract_returns(function)

                doc = APIDocumentation(
                    name=name,
                    qualified_name=function.name,
                    type="function",
                    docstring=self._extract_docstring(function.docstring),
                    signature=self._extract_signature(function),
                    parameters=parameters,
                    returns=returns,
                    file_path=str(module.filepath) if module.filepath else None,
                    line_number=getattr(function, 'lineno', None),
                    decorators=self._extract_decorators(function)
                )
                docs.append(doc)
            except Exception as e:
                logger.debug(f"Failed to extract function docs for {name}: {e}")

        return docs

    def _extract_classes(self, module: Module) -> List[APIDocumentation]:
        """Extract class documentation."""
        docs = []

        for name, cls in module.classes.items():
            try:
                # Get methods
                methods = list(cls.functions.keys()) if hasattr(cls, 'functions') else []

                # Get base classes
                base_classes = [str(base) for base in getattr(cls, 'bases', [])]

                doc = APIDocumentation(
                    name=name,
                    qualified_name=cls.name,
                    type="class",
                    docstring=self._extract_docstring(cls.docstring),
                    signature=self._extract_signature(cls),
                    file_path=str(module.filepath) if module.filepath else None,
                    line_number=getattr(cls, 'lineno', None),
                    base_classes=base_classes,
                    methods=methods,
                    decorators=self._extract_decorators(cls)
                )
                docs.append(doc)

                # Extract method documentation
                docs.extend(self._extract_class_methods(cls, methods))

            except Exception as e:
                logger.debug(f"Failed to extract class docs for {name}: {e}")

        return docs

    def _extract_class_methods(self, cls: Class, method_names: List[str]) -> List[APIDocumentation]:
        """Extract method documentation for a class."""
        docs = []

        if not hasattr(cls, 'functions'):
            return docs

        for method_name in method_names:
            try:
                method = cls.functions[method_name]

                # Get parameters
                parameters = self._extract_parameters(method)

                # Get return info
                returns = self._extract_returns(method)

                doc = APIDocumentation(
                    name=method_name,
                    qualified_name=method.name,
                    type="method",
                    docstring=self._extract_docstring(method.docstring),
                    signature=self._extract_signature(method),
                    parameters=parameters,
                    returns=returns,
                    file_path=str(cls.filepath) if hasattr(cls, 'filepath') and cls.filepath else None,
                    line_number=getattr(method, 'lineno', None),
                    parent_class=cls.name,
                    decorators=self._extract_decorators(method)
                )
                docs.append(doc)

            except Exception as e:
                logger.debug(f"Failed to extract method docs for {method_name}: {e}")

        return docs

    def _extract_attributes(self, module: Module) -> List[APIDocumentation]:
        """Extract attribute documentation."""
        docs = []

        # Extract module-level attributes
        if hasattr(module, 'attributes'):
            for name, attr in module.attributes.items():
                try:
                    doc = APIDocumentation(
                        name=name,
                        qualified_name=attr.name,
                        type="attribute",
                        docstring=self._extract_docstring(attr.docstring),
                        file_path=str(module.filepath) if module.filepath else None,
                        line_number=getattr(attr, 'lineno', None)
                    )
                    docs.append(doc)
                except Exception as e:
                    logger.debug(f"Failed to extract attribute docs for {name}: {e}")

        return docs

    def _extract_docstring(self, docstring: Optional[Docstring]) -> str:
        """Extract text content from Griffe docstring."""
        if not docstring:
            return ""

        try:
            return str(docstring).strip()
        except Exception:
            return ""

    def _extract_signature(self, obj) -> Optional[str]:
        """Extract function/method/class signature."""
        try:
            if hasattr(obj, 'signature'):
                return str(obj.signature)
            return None
        except Exception:
            return None

    def _extract_parameters(self, func: Function) -> Optional[List[Dict[str, Any]]]:
        """Extract parameter information."""
        try:
            if not hasattr(func, 'parameters') or not func.parameters:
                return None

            params = []
            for name, param in func.parameters.items():
                param_info = {
                    "name": name,
                    "annotation": str(param.annotation) if param.annotation else None,
                    "default": str(param.default) if param.default else None,
                    "description": self._extract_param_description(func.docstring, name)
                }
                params.append(param_info)

            return params
        except Exception:
            return None

    def _extract_returns(self, func: Function) -> Optional[Dict[str, Any]]:
        """Extract return type information."""
        try:
            if hasattr(func, 'returns') and func.returns:
                return {
                    "annotation": str(func.returns.annotation) if func.returns.annotation else None,
                    "description": self._extract_return_description(func.docstring)
                }
            return None
        except Exception:
            return None

    def _extract_decorators(self, obj) -> Optional[List[str]]:
        """Extract decorator information."""
        try:
            if hasattr(obj, 'decorators') and obj.decorators:
                return [str(decorator) for decorator in obj.decorators]
            return None
        except Exception:
            return None

    def _extract_param_description(self, docstring: Optional[Docstring], param_name: str) -> str:
        """Extract parameter description from docstring."""
        if not docstring:
            return ""

        try:
            # This is a simplified extraction - in practice you'd use
            # a proper docstring parser like docstring_parser
            docstring_str = str(docstring).lower()
            param_marker = f"{param_name} :"
            if param_marker in docstring_str:
                start = docstring_str.find(param_marker) + len(param_marker)
                end = docstring_str.find("\n", start)
                return docstring_str[start:end].strip()
            return ""
        except Exception:
            return ""

    def _extract_return_description(self, docstring: Optional[Docstring]) -> str:
        """Extract return description from docstring."""
        if not docstring:
            return ""

        try:
            docstring_str = str(docstring).lower()
            return_marker = "returns :"
            if return_marker in docstring_str:
                start = docstring_str.find(return_marker) + len(return_marker)
                end = docstring_str.find("\n", start)
                return docstring_str[start:end].strip()
            return ""
        except Exception:
            return ""

    def generate_langchain_documents(self) -> List[Document]:
        """
        Generate LangChain documents for RAG indexing.

        Returns:
            List of Document objects ready for vectorstore indexing
        """
        return [api_doc.to_document() for api_doc in self.api_docs]

    def save_to_json(self, filepath: str):
        """Save API documentation to JSON file."""
        data = {
            "metadata": {
                "generated_at": str(Path(__file__).parent / "api_docs.py"),  # Current file
                "source_paths": self.source_paths,
                "total_items": len(self.api_docs)
            },
            "api_documentation": [asdict(doc) for doc in self.api_docs]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Saved {len(self.api_docs)} API documentation items to {filepath}")

    def get_stats(self) -> Dict[str, Any]:
        """Get API documentation generation statistics."""
        if not self.api_docs:
            return {"total_items": 0}

        type_counts = {}
        for doc in self.api_docs:
            type_counts[doc.type] = type_counts.get(doc.type, 0) + 1

        return {
            "total_items": len(self.api_docs),
            "by_type": type_counts,
            "modules": len(self.modules),
            "source_paths": self.source_paths
        }

# Global API documentation generator
api_doc_generator = None

def generate_api_documentation(source_paths: List[str] = None) -> List[Document]:
    """
    Generate API documentation for RAG indexing.

    Args:
        source_paths: List of paths to scan for Python modules

    Returns:
        List of Document objects for vectorstore indexing
    """
    global api_doc_generator

    try:
        if api_doc_generator is None:
            if not GRIFFE_AVAILABLE:
                logger.warning("Griffe not available - API documentation generation disabled")
                return []
            api_doc_generator = APIDocumentationGenerator(source_paths)
        elif source_paths:
            # Re-initialize if paths provided
            api_doc_generator = APIDocumentationGenerator(source_paths)

        api_doc_generator.load_modules()
        api_doc_generator.extract_api_documentation()
        documents = api_doc_generator.generate_langchain_documents()

        logger.info(f"Generated {len(documents)} API documentation documents")
        return documents

    except Exception as e:
        logger.error(f"Failed to generate API documentation: {e}")
        return []

def search_api_documentation(query: str, api_docs: List[APIDocumentation]) -> List[APIDocumentation]:
    """
    Search API documentation for relevant items.

    Args:
        query: Search query
        api_docs: List of API documentation items

    Returns:
        Filtered list of relevant API documentation
    """
    query_lower = query.lower()
    relevant_docs = []

    for doc in api_docs:
        # Search in name, qualified name, and docstring
        searchable_text = f"{doc.name} {doc.qualified_name} {doc.docstring or ''}".lower()

        if any(term in searchable_text for term in query_lower.split()):
            relevant_docs.append(doc)

    return relevant_docs[:10]  # Limit to top 10 results

def get_api_documentation_stats() -> Dict[str, Any]:
    """Get API documentation generation statistics."""
    return api_doc_generator.get_stats()

# Integration with MkDocs
def create_mkdocs_api_config() -> Dict[str, Any]:
    """
    Create MkDocs configuration for API documentation.

    Returns:
        MkDocs plugin configuration for API docs
    """
    return {
        "plugins": [
            {
                "griffe": {
                    "packages": ["app"],
                    "ignore_private": True,
                    "ignore_init_method": False,
                    "show_inheritance": True,
                    "show_bases": True,
                    "show_docstring_attributes": True,
                    "show_docstring_functions": True,
                    "show_docstring_classes": True,
                    "show_docstring_modules": True,
                }
            }
        ]
    }