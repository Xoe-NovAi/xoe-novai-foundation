"""
Template Engine for Documentation Generation

Handles Jinja2 template processing, template management, and dynamic content generation.
Provides enterprise-grade template validation and caching capabilities.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import jinja2
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError

from .models import TemplateMetadata, GenerationResponse
from .utils import validate_output_path, ensure_directory

logger = logging.getLogger(__name__)


class TemplateEngine:
    """Enterprise-grade template engine for documentation generation."""
    
    def __init__(self, template_dir: str = "docs/templates"):
        """
        Initialize the template engine.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment with security and performance optimizations
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,  # Enable auto-escaping for security
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols']
        )
        
        # Add custom filters
        self._add_custom_filters()
        
        # Template cache
        self._template_cache = {}
        self._template_metadata = {}
        
        logger.info(f"Template engine initialized with directory: {self.template_dir}")
    
    def _add_custom_filters(self):
        """Add custom Jinja2 filters for documentation generation."""
        
        def markdown_safe(text: str) -> str:
            """Escape text for safe use in Markdown."""
            if not text:
                return ""
            # Escape Markdown special characters
            replacements = {
                '\\': '\\\\',
                '`': '\\`',
                '*': '\\*',
                '_': '\\_',
                '{': '\\{',
                '}': '\\}',
                '[': '\\[',
                ']': '\\]',
                '(': '\\(',
                ')': '\\)',
                '#': '\\#',
                '+': '\\+',
                '-': '\\-',
                '.': '\\.',
                '!': '\\!',
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            return text
        
        def to_title_case(text: str) -> str:
            """Convert text to title case."""
            return text.title() if text else ""
        
        def format_date(date_obj: Any, format_str: str = "%Y-%m-%d") -> str:
            """Format date object."""
            if isinstance(date_obj, datetime):
                return date_obj.strftime(format_str)
            return str(date_obj)
        
        def truncate_words(text: str, length: int = 50) -> str:
            """Truncate text to specified number of words."""
            if not text:
                return ""
            words = text.split()
            if len(words) <= length:
                return text
            return ' '.join(words[:length]) + "..."
        
        # Register filters
        self.env.filters['markdown_safe'] = markdown_safe
        self.env.filters['title_case'] = to_title_case
        self.env.filters['format_date'] = format_date
        self.env.filters['truncate_words'] = truncate_words
    
    async def generate(
        self, 
        template_name: str, 
        context: Dict[str, Any], 
        output_path: str
    ) -> GenerationResponse:
        """
        Generate documentation from a template.
        
        Args:
            template_name: Name of the template file
            context: Context variables for template rendering
            output_path: Output file path
            
        Returns:
            GenerationResponse with result information
        """
        start_time = datetime.now()
        
        try:
            # Validate inputs
            validate_output_path(output_path)
            ensure_directory(Path(output_path).parent)
            
            # Get or load template
            template = await self._get_template(template_name)
            
            # Add metadata to context
            context = self._enrich_context(context, template_name)
            
            # Render template
            rendered_content = template.render(context)
            
            # Write output file
            output_file = Path(output_path)
            output_file.write_text(rendered_content, encoding='utf-8')
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return GenerationResponse(
                success=True,
                message=f"Template '{template_name}' generated successfully",
                output_path=str(output_file),
                processing_time=processing_time,
                ai_model_used=None
            )
            
        except TemplateNotFound as e:
            raise ValueError(f"Template '{template_name}' not found in {self.template_dir}")
        except TemplateSyntaxError as e:
            raise ValueError(f"Template syntax error in '{template_name}': {e.message}")
        except Exception as e:
            logger.error(f"Template generation failed: {str(e)}")
            raise
    
    async def _get_template(self, template_name: str):
        """Get template from cache or load from file."""
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        try:
            template = self.env.get_template(template_name)
            self._template_cache[template_name] = template
            return template
        except TemplateNotFound:
            raise
    
    def _enrich_context(self, context: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """Add metadata and utility functions to template context."""
        enriched_context = context.copy()
        
        # Add metadata
        enriched_context.update({
            'generation_time': datetime.now(),
            'template_name': template_name,
            'template_dir': str(self.template_dir),
            'project_name': os.getenv('PROJECT_NAME', 'Xoe-NovAi'),
            'project_version': os.getenv('PROJECT_VERSION', '1.0.0'),
            'author': os.getenv('DOC_AUTHOR', 'Documentation System'),
        })
        
        # Add utility functions
        enriched_context.update({
            'now': datetime.now,
            'today': datetime.now().date(),
            'year': datetime.now().year,
        })
        
        return enriched_context
    
    def list_templates(self) -> List[TemplateMetadata]:
        """List all available templates with metadata."""
        templates = []
        
        for template_file in self.template_dir.rglob('*.md'):
            if template_file.is_file():
                metadata = self._get_template_metadata(template_file)
                templates.append(metadata)
        
        # Sort by creation time
        templates.sort(key=lambda x: x.created_at, reverse=True)
        return templates
    
    def _get_template_metadata(self, template_path: Path) -> TemplateMetadata:
        """Extract metadata from template file."""
        stat = template_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime)
        updated_at = datetime.fromtimestamp(stat.st_mtime)
        
        # Try to extract description from template comments
        description = None
        category = "general"
        
        try:
            content = template_path.read_text(encoding='utf-8')
            lines = content.split('\n')[:10]  # Check first 10 lines
            
            for line in lines:
                line = line.strip()
                if line.startswith('{#') and line.endswith('#}'):
                    comment = line[2:-2].strip()
                    if 'description:' in comment.lower():
                        description = comment.split(':', 1)[1].strip()
                    elif 'category:' in comment.lower():
                        category = comment.split(':', 1)[1].strip()
        except Exception:
            pass
        
        # Extract variables from template
        variables = self._extract_template_variables(template_path)
        
        return TemplateMetadata(
            name=template_path.name,
            path=str(template_path),
            description=description,
            category=category,
            created_at=created_at,
            updated_at=updated_at,
            variables=variables
        )
    
    def _extract_template_variables(self, template_path: Path) -> List[str]:
        """Extract variable names from template."""
        try:
            template_content = template_path.read_text(encoding='utf-8')
            template = self.env.from_string(template_content)
            
            # Get template variables
            variables = list(template.make_module().__dict__.keys())
            
            # Filter out Jinja2 built-ins
            builtins = {'self', 'super', 'loop', 'cycler', 'joiner', 'namespace'}
            variables = [v for v in variables if v not in builtins and not v.startswith('_')]
            
            return variables
        except Exception:
            return []
    
    def validate_template(self, template_name: str) -> bool:
        """Validate template syntax and structure."""
        try:
            template = self.env.get_template(template_name)
            
            # Test render with empty context
            template.render({})
            return True
        except Exception as e:
            logger.error(f"Template validation failed for '{template_name}': {str(e)}")
            return False
    
    def create_template(
        self, 
        name: str, 
        content: str, 
        description: Optional[str] = None,
        category: str = "general"
    ) -> bool:
        """Create a new template file."""
        try:
            template_file = self.template_dir / name
            
            # Add metadata comment
            metadata_comment = f"{{#\n"
            if description:
                metadata_comment += f"  description: {description}\n"
            metadata_comment += f"  category: {category}\n"
            metadata_comment += f"  created: {datetime.now().isoformat()}\n"
            metadata_comment += f"  author: Documentation System\n"
            metadata_comment += f"#}}\n\n"
            
            full_content = metadata_comment + content
            template_file.write_text(full_content, encoding='utf-8')
            
            # Clear cache to include new template
            self._template_cache.clear()
            
            logger.info(f"Template '{name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template '{name}': {str(e)}")
            return False
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a template file."""
        try:
            template_file = self.template_dir / template_name
            if template_file.exists():
                template_file.unlink()
                # Clear cache
                self._template_cache.pop(template_name, None)
                logger.info(f"Template '{template_name}' deleted successfully")
                return True
            else:
                logger.warning(f"Template '{template_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Failed to delete template '{template_name}': {str(e)}")
            return False
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get statistics about templates."""
        templates = self.list_templates()
        
        stats = {
            'total_templates': len(templates),
            'categories': {},
            'recent_templates': [],
            'largest_templates': []
        }
        
        # Count by category
        for template in templates:
            category = template.category
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
        
        # Get recent templates
        stats['recent_templates'] = [
            {'name': t.name, 'updated': t.updated_at.isoformat()}
            for t in sorted(templates, key=lambda x: x.updated_at, reverse=True)[:5]
        ]
        
        # Get largest templates (by file size)
        template_sizes = []
        for template in templates:
            try:
                size = (self.template_dir / template.name).stat().st_size
                template_sizes.append({'name': template.name, 'size': size})
            except Exception:
                pass
        
        stats['largest_templates'] = sorted(template_sizes, key=lambda x: x['size'], reverse=True)[:5]
        
        return stats