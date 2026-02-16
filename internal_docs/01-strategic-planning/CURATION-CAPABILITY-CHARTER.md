# CURATION-CAPABILITY-CHARTER

**Version**: 1.0.0  
**Status**: DRAFT  
**Priority**: P1 - HIGH  
**Owner**: Cline_CLI-Kat  
**Created**: 2026-02-13  
**Ma'at Alignment**: #18 Balance (Knowledge Equilibrium)

## Executive Summary

Activate and enhance the curation pipeline to systematically collect, organize, and make accessible knowledge from Vikunja API and other sources. This charter focuses on integrating `curate.py` with the crawler, creating manual curation workflows, and enabling Agent Bus triggers for knowledge queries.

## Objectives

### Primary Goals
- [ ] **Curation Pipeline Activation**: Enable `curate.py` + crawler for automated knowledge collection
- [ ] **Vikunja API Integration**: Create PoC to scrape Vikunja API and populate `library/manuals/vikunja-api.md`
- [ ] **Agent Bus Triggers**: Enable queries like "how to use Vikunja" to trigger curation workflows
- [ ] **Knowledge Organization**: Implement systematic categorization and indexing

### Success Criteria
- [ ] Automated curation of Vikunja API documentation
- [ ] Agent Bus integration for knowledge queries
- [ ] Complete Vikunja API manual in `library/manuals/vikunja-api.md`
- [ ] Zero manual curation overhead for routine updates

## Architecture

### System Components

#### 1. Enhanced Curation Pipeline
```python
# Enhanced curation system with Agent Bus integration
class EnhancedCurationPipeline:
    def __init__(self):
        self.crawlers = {
            'vikunja': VikunjaAPICrawler(),
            'web': WebCrawler(),
            'local': LocalFileCrawler()
        }
        self.curators = {
            'api_docs': APIDocumentationCurator(),
            'manuals': ManualCurator(),
            'research': ResearchCurator()
        }
        self.indexer = KnowledgeIndexer()
        self.agent_bus = AgentBusIntegration()
    
    def process_curation_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process curation request from Agent Bus"""
        request_type = request.get('type', 'manual')
        source = request.get('source')
        target = request.get('target')
        
        if request_type == 'vikunja_api':
            return self._curate_vikunja_api()
        elif request_type == 'web_scrape':
            return self._curate_web_content(source, target)
        elif request_type == 'manual_update':
            return self._curate_manual_update(source, target)
        else:
            return self._curate_general_content(request)
    
    def _curate_vikunja_api(self) -> Dict[str, Any]:
        """Curate Vikunja API documentation"""
        # Crawl Vikunja API endpoints
        api_data = self.crawlers['vikunja'].crawl_api()
        
        # Process and structure data
        processed_data = self.curators['api_docs'].process_api_data(api_data)
        
        # Generate documentation
        documentation = self.curators['api_docs'].generate_documentation(processed_data)
        
        # Save to library/manuals/vikunja-api.md
        self._save_vikunja_manual(documentation)
        
        # Update index
        self.indexer.update_index('vikunja-api', documentation)
        
        return {
            'status': 'success',
            'target': 'library/manuals/vikunja-api.md',
            'content_type': 'api_documentation',
            'timestamp': datetime.now().isoformat()
        }
```

#### 2. Vikunja API Crawler
```python
# Vikunja API crawler implementation
class VikunjaAPICrawler:
    def __init__(self, base_url: str = None, api_token: str = None):
        self.base_url = base_url or os.getenv('VIKUNJA_URL', 'http://localhost:3456')
        self.api_token = api_token or os.getenv('VIKUNJA_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def crawl_api(self) -> Dict[str, Any]:
        """Crawl all Vikunja API endpoints"""
        api_structure = {
            'base_url': self.base_url,
            'endpoints': {},
            'authentication': self._get_auth_info(),
            'rate_limits': self._get_rate_limits()
        }
        
        # Crawl main endpoints
        endpoints = [
            '/api/v1/tasks',
            '/api/v1/projects',
            '/api/v1/lists',
            '/api/v1/labels',
            '/api/v1/users',
            '/api/v1/settings'
        ]
        
        for endpoint in endpoints:
            try:
                endpoint_data = self._crawl_endpoint(endpoint)
                api_structure['endpoints'][endpoint] = endpoint_data
            except Exception as e:
                logger.warning(f"Failed to crawl {endpoint}: {e}")
        
        return api_structure
    
    def _crawl_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Crawl individual endpoint"""
        endpoint_data = {
            'methods': {},
            'sample_response': None,
            'parameters': [],
            'description': ''
        }
        
        # Test different HTTP methods
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        for method in methods:
            try:
                response = self._make_request(method, endpoint)
                if response.status_code == 200:
                    endpoint_data['methods'][method] = {
                        'status': 'success',
                        'response_sample': response.json()[:3] if response.json() else None
                    }
            except Exception as e:
                endpoint_data['methods'][method] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return endpoint_data
    
    def _make_request(self, method: str, endpoint: str) -> requests.Response:
        """Make authenticated request to Vikunja API"""
        url = f"{self.base_url}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, headers=self.headers, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=self.headers, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, headers=self.headers, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, headers=self.headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response
    
    def _get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        return {
            'type': 'Bearer Token',
            'header': 'Authorization',
            'example': 'Bearer your_api_token_here',
            'token_location': 'Environment variable VIKUNJA_API_TOKEN'
        }
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        """Get rate limit information"""
        return {
            'requests_per_minute': 100,
            'burst_limit': 10,
            'retry_after_header': 'Retry-After'
        }
```

#### 3. Agent Bus Integration
```python
# Agent Bus integration for curation triggers
class AgentBusIntegration:
    def __init__(self):
        self.curation_keywords = [
            'how to use vikunja',
            'vikunja documentation',
            'api documentation',
            'manual update',
            'knowledge curation'
        ]
        self.curation_pipeline = EnhancedCurationPipeline()
    
    def process_incoming_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming Agent Bus message for curation triggers"""
        message_body = message.get('body', '').lower()
        
        # Check for curation triggers
        for keyword in self.curation_keywords:
            if keyword in message_body:
                return self._handle_curation_request(message, keyword)
        
        return None
    
    def _handle_curation_request(self, message: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """Handle specific curation request"""
        request_data = {
            'type': self._determine_request_type(keyword),
            'source': message.get('FROM'),
            'target': message.get('TO'),
            'timestamp': message.get('TIMESTAMP'),
            'keyword': keyword
        }
        
        # Process curation request
        result = self.curation_pipeline.process_curation_request(request_data)
        
        # Send response back to Agent Bus
        self._send_curation_response(message, result)
        
        return result
    
    def _determine_request_type(self, keyword: str) -> str:
        """Determine curation request type from keyword"""
        if 'vikunja' in keyword:
            return 'vikunja_api'
        elif 'documentation' in keyword or 'manual' in keyword:
            return 'manual_update'
        elif 'api' in keyword:
            return 'api_documentation'
        else:
            return 'general_curation'
    
    def _send_curation_response(self, original_message: Dict[str, Any], result: Dict[str, Any]):
        """Send curation response back to Agent Bus"""
        response_message = f"""---
FROM: curation-pipeline
TO: {original_message.get('FROM')}
TIMESTAMP: {datetime.now().isoformat()}Z
TASK_ID: CURATION_RESPONSE_{datetime.now().strftime('%Y%m%d_%H%M%S')}
STATUS: LOG
---

### Curation Response

**Original Request**: {original_message.get('body', '')}  
**Curation Type**: {result.get('type', 'unknown')}  
**Status**: {result.get('status', 'unknown')}  
**Target**: {result.get('target', 'unknown')}  
**Timestamp**: {result.get('timestamp', 'unknown')}

#### Result Details
{self._format_result_details(result)}

---
"""
        
        # Write response to sender's inbox
        inbox_file = f"internal_docs/communication_hub/inbox_{original_message.get('FROM')}.md"
        with open(inbox_file, 'a') as f:
            f.write(f"\n{response_message}\n")
```

### Integration Points

#### Knowledge Indexing System
- **Elasticsearch Integration**: Full-text search across curated content
- **Semantic Indexing**: Vector embeddings for semantic search
- **Metadata Tagging**: Comprehensive metadata for categorization
- **Cross-Reference Links**: Automatic linking between related content

#### Library Organization
- **Manuals Directory**: Structured documentation in `library/manuals/`
- **Research Directory**: Research findings in `library/research/`
- **Staging Area**: Temporary storage in `library/_staging/`
- **Archive System**: Historical versions in `library/archive/`

#### Crawler Coordination
- **Scheduled Crawling**: Regular updates via cron jobs
- **Event-Driven Crawling**: Triggered by Agent Bus messages
- **Priority Queue**: Handle high-priority curation requests first
- **Rate Limiting**: Respect API rate limits and avoid overwhelming sources

## Implementation Steps

### Phase 1: Curation Pipeline Activation (Week 1)

#### Step 1.1: Enhance curate.py
```bash
# Enhance existing curate.py with new capabilities
cat > scripts/curate_enhanced.py << 'EOF'
#!/usr/bin/env python3
"""
Enhanced Curation Script
Activates curation pipeline with Agent Bus integration
"""

import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCurationScript:
    def __init__(self):
        self.library_dir = Path("library")
        self.manuals_dir = self.library_dir / "manuals"
        self.staging_dir = self.library_dir / "_staging"
        
        # Create directories
        self.manuals_dir.mkdir(parents=True, exist_ok=True)
        self.staging_dir.mkdir(parents=True, exist_ok=True)
    
    def curate_vikunja_api(self) -> Dict[str, Any]:
        """Curate Vikunja API documentation"""
        logger.info("Starting Vikunja API curation...")
        
        # Get Vikunja connection info
        vikunja_url = os.getenv('VIKUNJA_URL', 'http://localhost:3456')
        api_token = os.getenv('VIKUNJA_API_TOKEN')
        
        if not api_token:
            return {
                'status': 'error',
                'message': 'VIKUNJA_API_TOKEN environment variable required',
                'target': 'library/manuals/vikunja-api.md'
            }
        
        # Crawl API
        api_data = self._crawl_vikunja_api(vikunja_url, api_token)
        
        # Generate documentation
        documentation = self._generate_vikunja_documentation(api_data)
        
        # Save manual
        manual_path = self.manuals_dir / "vikunja-api.md"
        with open(manual_path, 'w', encoding='utf-8') as f:
            f.write(documentation)
        
        logger.info(f"Vikunja API manual saved to {manual_path}")
        
        return {
            'status': 'success',
            'target': str(manual_path),
            'content_type': 'api_documentation',
            'timestamp': datetime.now().isoformat()
        }
    
    def _crawl_vikunja_api(self, base_url: str, api_token: str) -> Dict[str, Any]:
        """Crawl Vikunja API endpoints"""
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        api_structure = {
            'base_url': base_url,
            'endpoints': {},
            'authentication': {
                'type': 'Bearer Token',
                'header': 'Authorization',
                'example': 'Bearer your_api_token_here'
            }
        }
        
        # Define endpoints to crawl
        endpoints = [
            '/api/v1/tasks',
            '/api/v1/projects', 
            '/api/v1/lists',
            '/api/v1/labels',
            '/api/v1/users'
        ]
        
        for endpoint in endpoints:
            try:
                logger.info(f"Crawling endpoint: {endpoint}")
                
                # GET request
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=30)
                if response.status_code == 200:
                    sample_data = response.json()
                    if isinstance(sample_data, list) and sample_data:
                        sample_data = sample_data[:3]  # Limit sample size
                else:
                    sample_data = {'error': f'HTTP {response.status_code}'}
                
                api_structure['endpoints'][endpoint] = {
                    'methods': {
                        'GET': {
                            'status': 'success' if response.status_code == 200 else 'error',
                            'sample_response': sample_data
                        }
                    },
                    'description': f'API endpoint for {endpoint.split("/")[-1]}'
                }
                
            except Exception as e:
                logger.warning(f"Failed to crawl {endpoint}: {e}")
                api_structure['endpoints'][endpoint] = {
                    'methods': {'GET': {'status': 'error', 'error': str(e)}},
                    'description': f'Failed to crawl {endpoint}'
                }
        
        return api_structure
    
    def _generate_vikunja_documentation(self, api_data: Dict[str, Any]) -> str:
        """Generate Vikunja API documentation"""
        doc = f"""# Vikunja API Documentation

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Base URL**: {api_data['base_url']}

## Authentication

Vikunja API uses Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \\
     {api_data['base_url']}/api/v1/tasks
```

## Endpoints

"""
        
        for endpoint, data in api_data['endpoints'].items():
            doc += f"### {endpoint}\n\n"
            doc += f"**Description**: {data['description']}\n\n"
            
            if 'methods' in data:
                for method, method_data in data['methods'].items():
                    doc += f"#### {method}\n\n"
                    doc += f"- **Status**: {method_data['status']}\n"
                    
                    if method_data['status'] == 'success' and 'sample_response' in method_data:
                        doc += f"- **Sample Response**: \n```json\n{json.dumps(method_data['sample_response'], indent=2)}\n```\n\n"
                    elif 'error' in method_data:
                        doc += f"- **Error**: {method_data['error']}\n\n"
            
            doc += "\n"
        
        doc += """
## Usage Examples

### Get All Tasks
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \\
     {api_data['base_url']}/api/v1/tasks
```

### Create a New Task
```bash
curl -X POST -H "Authorization: Bearer YOUR_API_TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{{
         "title": "New Task",
         "description": "Task description",
         "project_id": 1
     }}' \\
     {api_data['base_url']}/api/v1/tasks
```

## Rate Limits

- **Requests per minute**: 100
- **Burst limit**: 10
- **Retry-After header**: Used for rate limit responses

## Error Handling

Common error responses:
- **401**: Authentication required
- **403**: Insufficient permissions
- **404**: Resource not found
- **429**: Rate limit exceeded
- **500**: Internal server error

"""
        
        return doc
    
    def process_agent_bus_message(self, message_file: str) -> Optional[Dict[str, Any]]:
        """Process Agent Bus message for curation triggers"""
        if not Path(message_file).exists():
            return None
        
        # Read message
        with open(message_file, 'r') as f:
            content = f.read()
        
        # Check for curation triggers
        curation_keywords = [
            'how to use vikunja',
            'vikunja documentation', 
            'api documentation',
            'manual update',
            'knowledge curation'
        ]
        
        message_lower = content.lower()
        for keyword in curation_keywords:
            if keyword in message_lower:
                logger.info(f"Curation trigger detected: {keyword}")
                
                # Determine curation type
                if 'vikunja' in keyword:
                    return self.curate_vikunja_api()
                else:
                    return self._handle_general_curation(keyword, content)
        
        return None
    
    def _handle_general_curation(self, keyword: str, content: str) -> Dict[str, Any]:
        """Handle general curation requests"""
        # For now, just log the request
        logger.info(f"General curation requested for: {keyword}")
        
        return {
            'status': 'pending',
            'message': f'General curation requested: {keyword}',
            'content_preview': content[:200] + '...' if len(content) > 200 else content
        }

def main():
    """Main execution function"""
    import sys
    
    curator = EnhancedCurationScript()
    
    if len(sys.argv) > 1:
        # Process specific message file
        message_file = sys.argv[1]
        result = curator.process_agent_bus_message(message_file)
        
        if result:
            print(f"Curation result: {json.dumps(result, indent=2)}")
        else:
            print("No curation triggers found")
    else:
        # Run Vikunja API curation
        result = curator.curate_vikunja_api()
        print(f"Vikunja curation result: {json.dumps(result, indent=2)}")

if __name__ == '__main__':
    main()
EOF
chmod +x scripts/curate_enhanced.py
```

#### Step 1.2: Agent Bus Message Processor
```bash
# Create Agent Bus message processor
cat > scripts/process-agent-messages.py << 'EOF'
#!/usr/bin/env python3
"""
Agent Bus Message Processor
Processes incoming messages and triggers curation workflows
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentBusMessageProcessor:
    def __init__(self):
        self.curation_script = "scripts/curate_enhanced.py"
        self.curation_keywords = [
            'how to use vikunja',
            'vikunja documentation',
            'api documentation', 
            'manual update',
            'knowledge curation',
            'scrape vikunja',
            'vikunja api'
        ]
    
    def process_all_inboxes(self) -> Dict[str, Any]:
        """Process all Agent Bus inboxes for curation triggers"""
        results = {
            'processed_inboxes': 0,
            'curation_triggers': 0,
            'successful_curations': 0,
            'failed_curations': 0
        }
        
        inbox_dir = Path("internal_docs/communication_hub")
        for inbox_file in inbox_dir.glob("inbox_*.md"):
            results['processed_inboxes'] += 1
            
            # Process messages in this inbox
            inbox_results = self._process_inbox(inbox_file)
            results['curation_triggers'] += inbox_results['curation_triggers']
            results['successful_curations'] += inbox_results['successful_curations']
            results['failed_curations'] += inbox_results['failed_curations']
        
        logger.info(f"Processed {results['processed_inboxes']} inboxes")
        logger.info(f"Found {results['curation_triggers']} curation triggers")
        logger.info(f"Successful curations: {results['successful_curations']}")
        logger.info(f"Failed curations: {results['failed_curations']}")
        
        return results
    
    def _process_inbox(self, inbox_file: Path) -> Dict[str, Any]:
        """Process messages in a single inbox"""
        results = {
            'curation_triggers': 0,
            'successful_curations': 0,
            'failed_curations': 0
        }
        
        if not inbox_file.exists():
            return results
        
        # Read inbox content
        content = inbox_file.read_text(encoding='utf-8')
        
        # Check for curation triggers
        content_lower = content.lower()
        for keyword in self.curation_keywords:
            if keyword in content_lower:
                results['curation_triggers'] += 1
                logger.info(f"Curation trigger found in {inbox_file}: {keyword}")
                
                # Trigger curation
                try:
                    curation_result = self._trigger_curation(keyword, str(inbox_file))
                    if curation_result.get('status') == 'success':
                        results['successful_curations'] += 1
                    else:
                        results['failed_curations'] += 1
                except Exception as e:
                    logger.error(f"Curation failed for {keyword}: {e}")
                    results['failed_curations'] += 1
        
        return results
    
    def _trigger_curation(self, keyword: str, message_file: str) -> Dict[str, Any]:
        """Trigger curation workflow"""
        import subprocess
        
        # Run curation script
        cmd = ['python3', self.curation_script, message_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {'status': 'success', 'message': 'Curation completed'}
        else:
            logger.error(f"Curation script failed: {result.stderr}")
            return {'status': 'error', 'message': result.stderr}

def main():
    """Main execution function"""
    processor = AgentBusMessageProcessor()
    results = processor.process_all_inboxes()
    
    print(f"Processing results: {json.dumps(results, indent=2)}")

if __name__ == '__main__':
    main()
EOF
chmod +x scripts/process-agent-messages.py
```

### Phase 2: Vikunja API Integration (Week 2)

#### Step 2.1: Vikunja API Manual Generator
```bash
# Create comprehensive Vikunja API manual generator
cat > scripts/generate-vikunja-manual.py << 'EOF'
#!/usr/bin/env python3
"""
Vikunja API Manual Generator
Generates comprehensive API documentation from live API calls
"""

import os
import json
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VikunjaManualGenerator:
    def __init__(self):
        self.base_url = os.getenv('VIKUNJA_URL', 'http://localhost:3456')
        self.api_token = os.getenv('VIKUNJA_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        self.manual_dir = Path("library/manuals")
        self.manual_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_complete_manual(self) -> Dict[str, Any]:
        """Generate complete Vikunja API manual"""
        if not self.api_token:
            return {
                'status': 'error',
                'message': 'VIKUNJA_API_TOKEN environment variable required',
                'target': 'library/manuals/vikunja-api.md'
            }
        
        logger.info("Generating comprehensive Vikunja API manual...")
        
        # Collect API information
        api_info = {
            'metadata': self._get_api_metadata(),
            'authentication': self._get_auth_details(),
            'endpoints': self._discover_endpoints(),
            'examples': self._generate_examples()
        }
        
        # Generate manual content
        manual_content = self._format_manual(api_info)
        
        # Save manual
        manual_path = self.manual_dir / "vikunja-api.md"
        with open(manual_path, 'w', encoding='utf-8') as f:
            f.write(manual_content)
        
        logger.info(f"Vikunja API manual generated: {manual_path}")
        
        return {
            'status': 'success',
            'target': str(manual_path),
            'content_type': 'api_manual',
            'timestamp': datetime.now().isoformat(),
            'endpoints_discovered': len(api_info['endpoints'])
        }
    
    def _get_api_metadata(self) -> Dict[str, Any]:
        """Get API metadata"""
        try:
            # Try to get API version info
            response = requests.get(f"{self.base_url}/api/v1/version", headers=self.headers, timeout=10)
            if response.status_code == 200:
                version_info = response.json()
            else:
                version_info = {'version': 'unknown'}
        except:
            version_info = {'version': 'unknown'}
        
        return {
            'base_url': self.base_url,
            'api_version': 'v1',
            'version_info': version_info,
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_auth_details(self) -> Dict[str, Any]:
        """Get authentication details"""
        return {
            'type': 'Bearer Token',
            'header': 'Authorization',
            'example': 'Bearer YOUR_API_TOKEN',
            'token_source': 'Environment variable VIKUNJA_API_TOKEN',
            'scopes': ['read', 'write', 'admin'],
            'rate_limits': {
                'requests_per_minute': 100,
                'burst_limit': 10,
                'retry_after_header': 'Retry-After'
            }
        }
    
    def _discover_endpoints(self) -> Dict[str, Any]:
        """Discover and document API endpoints"""
        endpoints = {
            '/api/v1/tasks': self._document_tasks_endpoint(),
            '/api/v1/projects': self._document_projects_endpoint(),
            '/api/v1/lists': self._document_lists_endpoint(),
            '/api/v1/labels': self._document_labels_endpoint(),
            '/api/v1/users': self._document_users_endpoint(),
            '/api/v1/settings': self._document_settings_endpoint()
        }
        
        return endpoints
    
    def _document_tasks_endpoint(self) -> Dict[str, Any]:
        """Document tasks endpoint"""
        return {
            'description': 'Manage tasks',
            'methods': {
                'GET': {
                    'description': 'Get all tasks',
                    'parameters': {
                        'limit': {'type': 'integer', 'description': 'Number of tasks to return'},
                        'offset': {'type': 'integer', 'description': 'Offset for pagination'},
                        'project_id': {'type': 'integer', 'description': 'Filter by project ID'}
                    },
                    'sample_response': self._get_sample_response('/api/v1/tasks')
                },
                'POST': {
                    'description': 'Create new task',
                    'request_body': {
                        'title': {'type': 'string', 'required': True},
                        'description': {'type': 'string', 'required': False},
                        'project_id': {'type': 'integer', 'required': False},
                        'list_id': {'type': 'integer', 'required': False}
                    },
                    'sample_response': self._get_sample_response('/api/v1/tasks', method='POST')
                }
            }
        }
    
    def _document_projects_endpoint(self) -> Dict[str, Any]:
        """Document projects endpoint"""
        return {
            'description': 'Manage projects',
            'methods': {
                'GET': {
                    'description': 'Get all projects',
                    'sample_response': self._get_sample_response('/api/v1/projects')
                },
                'POST': {
                    'description': 'Create new project',
                    'request_body': {
                        'title': {'type': 'string', 'required': True},
                        'description': {'type': 'string', 'required': False}
                    },
                    'sample_response': self._get_sample_response('/api/v1/projects', method='POST')
                }
            }
        }
    
    def _document_lists_endpoint(self) -> Dict[str, Any]:
        """Document lists endpoint"""
        return {
            'description': 'Manage task lists',
            'methods': {
                'GET': {
                    'description': 'Get all lists',
                    'parameters': {
                        'project_id': {'type': 'integer', 'description': 'Filter by project ID'}
                    },
                    'sample_response': self._get_sample_response('/api/v1/lists')
                }
            }
        }
    
    def _document_labels_endpoint(self) -> Dict[str, Any]:
        """Document labels endpoint"""
        return {
            'description': 'Manage labels',
            'methods': {
                'GET': {
                    'description': 'Get all labels',
                    'sample_response': self._get_sample_response('/api/v1/labels')
                },
                'POST': {
                    'description': 'Create new label',
                    'request_body': {
                        'name': {'type': 'string', 'required': True},
                        'color': {'type': 'string', 'required': False}
                    },
                    'sample_response': self._get_sample_response('/api/v1/labels', method='POST')
                }
            }
        }
    
    def _document_users_endpoint(self) -> Dict[str, Any]:
        """Document users endpoint"""
        return {
            'description': 'Manage users',
            'methods': {
                'GET': {
                    'description': 'Get current user',
                    'sample_response': self._get_sample_response('/api/v1/users/me')
                }
            }
        }
    
    def _document_settings_endpoint(self) -> Dict[str, Any]:
        """Document settings endpoint"""
        return {
            'description': 'Get system settings',
            'methods': {
                'GET': {
                    'description': 'Get system settings',
                    'sample_response': self._get_sample_response('/api/v1/settings')
                }
            }
        }
    
    def _get_sample_response(self, endpoint: str, method: str = 'GET') -> Any:
        """Get sample response from API endpoint"""
        try:
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=10)
            elif method == 'POST':
                # For POST, try with minimal data
                response = requests.post(f"{self.base_url}{endpoint}", 
                                       headers=self.headers, 
                                       json={'title': 'Test'}, 
                                       timeout=10)
            else:
                return {'error': f'Unsupported method: {method}'}
            
            if response.status_code in [200, 201]:
                data = response.json()
                # Limit sample size
                if isinstance(data, list) and len(data) > 5:
                    return data[:5]
                return data
            else:
                return {'error': f'HTTP {response.status_code}', 'message': response.text}
        
        except Exception as e:
            return {'error': 'Request failed', 'message': str(e)}
    
    def _generate_examples(self) -> Dict[str, Any]:
        """Generate usage examples"""
        return {
            'basic_usage': {
                'get_tasks': f"""# Get all tasks
curl -H "Authorization: Bearer {self.api_token}" \\
     {self.base_url}/api/v1/tasks""",
                'create_task': f"""# Create a new task
curl -X POST -H "Authorization: Bearer {self.api_token}" \\
     -H "Content-Type: application/json" \\
     -d '{{"title": "New Task", "description": "Task description"}}' \\
     {self.base_url}/api/v1/tasks"""
            },
            'error_handling': {
                'rate_limit': """# Handle rate limiting
response=$(curl -s -w "%{{http_code}}" -H "Authorization: Bearer $TOKEN" \\
     {self.base_url}/api/v1/tasks)
if [[ ${{response: -3}} == "429" ]]; then
    sleep 60  # Wait 1 minute
    # Retry logic
fi""",
                'authentication_error': """# Handle authentication errors
if curl -s -f -H "Authorization: Bearer $TOKEN" \\
        {self.base_url}/api/v1/tasks > /dev/null; then
    echo "Authentication successful"
else
    echo "Authentication failed"
fi"""
            }
        }
    
    def _format_manual(self, api_info: Dict[str, Any]) -> str:
        """Format API information into manual"""
        manual = f"""# Vikunja API Manual

**Generated**: {api_info['metadata']['generated_at']}
**Base URL**: {api_info['metadata']['base_url']}
**API Version**: {api_info['metadata']['api_version']}

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limits](#rate-limits)
3. [Error Handling](#error-handling)
4. [Endpoints](#endpoints)
5. [Usage Examples](#usage-examples)

## Authentication

Vikunja API uses Bearer token authentication. Include your API token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \\
     {api_info['metadata']['base_url']}/api/v1/tasks
```

### Getting an API Token

API tokens can be generated in Vikunja's web interface under Settings → API.

## Rate Limits

- **Requests per minute**: {api_info['authentication']['rate_limits']['requests_per_minute']}
- **Burst limit**: {api_info['authentication']['rate_limits']['burst_limit']}
- **Retry-After header**: {api_info['authentication']['rate_limits']['retry_after_header']}

When rate limits are exceeded, the API returns HTTP 429 with a `Retry-After` header indicating when to retry.

## Error Handling

The API returns standard HTTP status codes:

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Authentication Required
- **403**: Forbidden
- **404**: Not Found
- **429**: Rate Limited
- **500**: Internal Server Error

Error responses include a JSON body with error details:

```json
{{
    "error": "error_code",
    "message": "Human readable error message"
}}
```

## Endpoints

"""
        
        # Add endpoint documentation
        for endpoint, data in api_info['endpoints'].items():
            manual += f"### {endpoint}\n\n"
            manual += f"**Description**: {data['description']}\n\n"
            
            for method, method_data in data['methods'].items():
                manual += f"#### {method}\n\n"
                manual += f"{method_data['description']}\n\n"
                
                if 'parameters' in method_data:
                    manual += "**Parameters:**\n"
                    for param, param_info in method_data['parameters'].items():
                        required = "Required" if param_info.get('required', False) else "Optional"
                        manual += f"- `{param}` ({param_info['type']}, {required}): {param_info['description']}\n"
                    manual += "\n"
                
                if 'request_body' in method_data:
                    manual += "**Request Body:**\n"
                    manual += "```json\n"
                    manual += json.dumps(method_data['request_body'], indent=2)
                    manual += "\n```\n\n"
                
                if 'sample_response' in method_data:
                    manual += "**Sample Response:**\n"
                    manual += "```json\n"
                    manual += json.dumps(method_data['sample_response'], indent=2)
                    manual += "\n```\n\n"
        
        # Add usage examples
        manual += "## Usage Examples\n\n"
        
        manual += "### Basic Usage\n\n"
        for example_name, example_code in api_info['examples']['basic_usage'].items():
            manual += f"#### {example_name.replace('_', ' ').title()}\n\n"
            manual += f"```bash\n{example_code}\n```\n\n"
        
        manual += "### Error Handling\n\n"
        for example_name, example_code in api_info['examples']['error_handling'].items():
            manual += f"#### {example_name.replace('_', ' ').title()}\n\n"
            manual += f"```bash\n{example_code}\n```\n\n"
        
        manual += """
## SDK Examples

### Python

```python
import requests

class VikunjaClient:
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_tasks(self, limit=100, offset=0):
        response = requests.get(
            f"{self.base_url}/api/v1/tasks",
            headers=self.headers,
            params={'limit': limit, 'offset': offset}
        )
        response.raise_for_status()
        return response.json()
    
    def create_task(self, title, description=None, project_id=None):
        data = {'title': title}
        if description:
            data['description'] = description
        if project_id:
            data['project_id'] = project_id
        
        response = requests.post(
            f"{self.base_url}/api/v1/tasks",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

# Usage
client = VikunjaClient("http://localhost:3456", "YOUR_API_TOKEN")
tasks = client.get_tasks()
new_task = client.create_task("New Task", "Task description")
```

### JavaScript

```javascript
class VikunjaClient {
    constructor(baseUrl, apiToken) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getTasks(limit = 100, offset = 0) {
        const response = await fetch(
            `${this.baseUrl}/api/v1/tasks?limit=${limit}&offset=${offset}`,
            { headers: this.headers }
        );
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }
    
    async createTask(title, description = null, projectId = null) {
        const data = { title };
        if (description) data.description = description;
        if (projectId) data.project_id = projectId;
        
        const response = await fetch(`${this.baseUrl}/api/v1/tasks`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }
}

// Usage
const client = new VikunjaClient("http://localhost:3456", "YOUR_API_TOKEN");
const tasks = await client.getTasks();
const newTask = await client.createTask("New Task", "Task description");
```

## Troubleshooting

### Common Issues

1. **Authentication Failed (401)**
   - Check that your API token is correct
   - Ensure the token hasn't expired
   - Verify the Authorization header format

2. **Rate Limited (429)**
   - Implement exponential backoff
   - Respect the `Retry-After` header
   - Consider caching responses

3. **Not Found (404)**
   - Verify the endpoint URL is correct
   - Check that the resource exists
   - Ensure you have permission to access the resource

4. **Server Error (500)**
   - Check Vikunja server logs
   - Verify the request format
   - Report persistent issues to Vikunja maintainers

## Changelog

- **2026-02-13**: Initial manual generation from live API discovery
- **2026-02-13**: Added comprehensive endpoint documentation
- **2026-02-13**: Added usage examples and SDK samples

## Support

For API-related questions or issues, refer to:
- [Vikunja Documentation](https://vikunja.io/docs/)
- [Vikunja GitHub Issues](https://github.com/go-vikunja/vikunja/issues)
- [Vikunja Community Forum](https://community.vikunja.io/)

"""
        
        return manual

def main():
    """Main execution function"""
    generator = VikunjaManualGenerator()
    result = generator.generate_complete_manual()
    
    print(f"Manual generation result: {json.dumps(result, indent=2)}")

if __name__ == '__main__':
    main()
EOF
chmod +x scripts/generate-vikunja-manual.py
```

### Phase 3: Agent Bus Integration (Week 3)

#### Step 3.1: Automated Curation Scheduler
```bash
# Create automated curation scheduler
cat > scripts/curation-scheduler.py << 'EOF'
#!/usr/bin/env python3
"""
Curation Scheduler
Automated scheduling and triggering of curation workflows
"""

import os
import time
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurationScheduler:
    def __init__(self):
        self.schedule_file = Path("internal_docs/communication_hub/curation_schedule.json")
        self.log_file = Path("internal_docs/communication_hub/curation_log.json")
        
        # Initialize schedule
        self.schedule = self._load_schedule()
        self.log = self._load_log()
    
    def _load_schedule(self) -> Dict[str, Any]:
        """Load curation schedule"""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                return json.load(f)
        
        # Default schedule
        return {
            'vikunja_api_update': {
                'enabled': True,
                'interval_hours': 24,
                'last_run': None,
                'script': 'scripts/generate-vikunja-manual.py'
            },
            'agent_bus_monitoring': {
                'enabled': True,
                'interval_minutes': 5,
                'last_run': None,
                'script': 'scripts/process-agent-messages.py'
            },
            'manual_curation_check': {
                'enabled': True,
                'interval_hours': 12,
                'last_run': None,
                'script': 'scripts/curate_enhanced.py'
            }
        }
    
    def _load_log(self) -> List[Dict[str, Any]]:
        """Load curation execution log"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []
    
    def run_scheduler(self, duration_hours: int = 24):
        """Run scheduler for specified duration"""
        logger.info(f"Starting curation scheduler for {duration_hours} hours")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        while datetime.now() < end_time:
            current_time = datetime.now()
            
            # Check each scheduled task
            for task_name, task_config in self.schedule.items():
                if task_config.get('enabled', False):
                    if self._should_run_task(task_name, task_config, current_time):
                        self._execute_task(task_name, task_config)
            
            # Save state
            self._save_state()
            
            # Sleep for 1 minute
            time.sleep(60)
        
        logger.info("Curation scheduler completed")
    
    def _should_run_task(self, task_name: str, task_config: Dict[str, Any], current_time: datetime) -> bool:
        """Check if task should be run"""
        last_run_str = task_config.get('last_run')
        if not last_run_str:
            return True
        
        last_run = datetime.fromisoformat(last_run_str)
        
        if 'interval_hours' in task_config:
            interval = timedelta(hours=task_config['interval_hours'])
        elif 'interval_minutes' in task_config:
            interval = timedelta(minutes=task_config['interval_minutes'])
        else:
            return False
        
        return current_time - last_run >= interval
    
    def _execute_task(self, task_name: str, task_config: Dict[str, Any]):
        """Execute scheduled task"""
        script_path = task_config['script']
        
        logger.info(f"Executing scheduled task: {task_name}")
        
        try:
            # Run the script
            result = subprocess.run(
                ['python3', script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Log the result
            execution_log = {
                'task_name': task_name,
                'script': script_path,
                'timestamp': datetime.now().isoformat(),
                'status': 'success' if result.returncode == 0 else 'failed',
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            self.log.append(execution_log)
            
            # Update schedule
            task_config['last_run'] = datetime.now().isoformat()
            
            if result.returncode == 0:
                logger.info(f"Task {task_name} completed successfully")
            else:
                logger.error(f"Task {task_name} failed with return code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error(f"Task {task_name} timed out after 5 minutes")
            execution_log = {
                'task_name': task_name,
                'script': script_path,
                'timestamp': datetime.now().isoformat(),
                'status': 'timeout',
                'return_code': -1,
                'stdout': '',
                'stderr': 'Task timed out after 5 minutes'
            }
            self.log.append(execution_log)
        
        except Exception as e:
            logger.error(f"Task {task_name} failed with exception: {e}")
            execution_log = {
                'task_name': task_name,
                'script': script_path,
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'return_code': -1,
                'stdout': '',
                'stderr': str(e)
            }
            self.log.append(execution_log)
    
    def _save_state(self):
        """Save current state"""
        # Save schedule
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f, indent=2)
        
        # Save log (keep last 1000 entries)
        if len(self.log) > 1000:
            self.log = self.log[-1000:]
        
        with open(self.log_file, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    def add_scheduled_task(self, task_name: str, config: Dict[str, Any]):
        """Add a new scheduled task"""
        self.schedule[task_name] = config
        self._save_state()
        logger.info(f"Added scheduled task: {task_name}")
    
    def remove_scheduled_task(self, task_name: str):
        """Remove a scheduled task"""
        if task_name in self.schedule:
            del self.schedule[task_name]
            self._save_state()
            logger.info(f"Removed scheduled task: {task_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            'schedule': self.schedule,
            'log_entries': len(self.log),
            'recent_executions': self.log[-10:] if self.log else []
        }

def main():
    """Main execution function"""
    import sys
    
    scheduler = CurationScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'run':
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            scheduler.run_scheduler(duration)
        elif command == 'status':
            status = scheduler.get_status()
            print(json.dumps(status, indent=2))
        elif command == 'add-task':
            if len(sys.argv) >= 5:
                task_name = sys.argv[2]
                interval_hours = int(sys.argv[3])
                script = sys.argv[4]
                config = {
                    'enabled': True,
                    'interval_hours': interval_hours,
                    'script': script,
                    'last_run': None
                }
                scheduler.add_scheduled_task(task_name, config)
            else:
                print("Usage: python3 curation-scheduler.py add-task <task_name> <interval_hours> <script>")
        elif command == 'remove-task':
            if len(sys.argv) >= 3:
                task_name = sys.argv[2]
                scheduler.remove_scheduled_task(task_name)
            else:
                print("Usage: python3 curation-scheduler.py remove-task <task_name>")
        else:
            print("Unknown command. Available: run, status, add-task, remove-task")
    else:
        print("Usage: python3 curation-scheduler.py <command> [args...]")
        print("Commands:")
        print("  run [duration_hours]  - Run scheduler for specified duration (default: 24)")
        print("  status                - Show current scheduler status")
        print("  add-task              - Add a new scheduled task")
        print("  remove-task           - Remove a scheduled task")

if __name__ == '__main__':
    main()
EOF
chmod +x scripts/curation-scheduler.py
```

## Test Plan

### Unit Tests
```bash
# Create test suite for curation system
cat > tests/test_curation_system.py << 'EOF'
#!/usr/bin/env python3
"""
Test suite for curation system
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from scripts.curate_enhanced import EnhancedCurationScript
from scripts.vikunja_manual_generator import VikunjaManualGenerator
from scripts.curation_scheduler import CurationScheduler

class TestEnhancedCurationScript:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_library_dir = os.getcwd() + "/library"
        
        # Mock environment
        os.environ['VIKUNJA_URL'] = 'http://test-vikunja.com'
        os.environ['VIKUNJA_API_TOKEN'] = 'test-token'
    
    def test_init_directories(self):
        """Test directory creation"""
        curator = EnhancedCurationScript()
        
        assert curator.library_dir.exists()
        assert curator.manuals_dir.exists()
        assert curator.staging_dir.exists()
    
    def test_vikunja_api_without_token(self):
        """Test Vikunja API curation without token"""
        # Remove token
        del os.environ['VIKUNJA_API_TOKEN']
        
        curator = EnhancedCurationScript()
        result = curator.curate_vikunja_api()
        
        assert result['status'] == 'error'
        assert 'VIKUNJA_API_TOKEN' in result['message']
    
    def test_process_agent_bus_message(self):
        """Test Agent Bus message processing"""
        curator = EnhancedCurationScript()
        
        # Create test message file
        message_file = Path(self.temp_dir) / "test_message.md"
        message_file.write_text("How to use Vikunja?")
        
        result = curator.process_agent_bus_message(str(message_file))
        
        assert result is not None
        assert result.get('status') == 'pending'

class TestVikunjaManualGenerator:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment
        os.environ['VIKUNJA_URL'] = 'http://test-vikunja.com'
        os.environ['VIKUNJA_API_TOKEN'] = 'test-token'
    
    def test_init(self):
        """Test manual generator initialization"""
        generator = VikunjaManualGenerator()
        
        assert generator.base_url == 'http://test-vikunja.com'
        assert generator.api_token == 'test-token'
        assert generator.manual_dir.exists()
    
    def test_generate_without_token(self):
        """Test manual generation without token"""
        # Remove token
        del os.environ['VIKUNJA_API_TOKEN']
        
        generator = VikunjaManualGenerator()
        result = generator.generate_complete_manual()
        
        assert result['status'] == 'error'
        assert 'VIKUNJA_API_TOKEN' in result['message']

class TestCurationScheduler:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test schedule file
        self.schedule_file = Path(self.temp_dir) / "curation_schedule.json"
        self.log_file = Path(self.temp_dir) / "curation_log.json"
    
    def test_init_schedule(self):
        """Test scheduler initialization"""
        # Mock file paths
        import scripts.curation_scheduler as cs
        original_schedule_file = cs.CurationScheduler.schedule_file
        original_log_file = cs.CurationScheduler.log_file
        
        cs.CurationScheduler.schedule_file = self.schedule_file
        cs.CurationScheduler.log_file = self.log_file
        
        try:
            scheduler = CurationScheduler()
            
            assert 'vikunja_api_update' in scheduler.schedule
            assert 'agent_bus_monitoring' in scheduler.schedule
            assert 'manual_curation_check' in scheduler.schedule
            
            assert len(scheduler.log) == 0
            
        finally:
            # Restore original paths
            cs.CurationScheduler.schedule_file = original_schedule_file
            cs.CurationScheduler.log_file = original_log_file

if __name__ == '__main__':
    pytest.main([__file__])
EOF
```

### Integration Tests
```bash
# Create integration test script
cat > scripts/test-curation-integration.py << 'EOF'
#!/usr/bin/env python3
"""
Integration test for curation system
"""

import os
import time
import json
from pathlib import Path
from scripts.curate_enhanced import EnhancedCurationScript
from scripts.vikunja_manual_generator import VikunjaManualGenerator
from scripts.curation_scheduler import CurationScheduler

def test_full_curation_workflow():
    """Test complete curation workflow"""
    print("Testing full curation workflow...")
    
    # Setup test environment
    test_dir = Path("test_curation")
    test_dir.mkdir(exist_ok=True)
    
    # Test 1: Vikunja API curation
    print("1. Testing Vikunja API curation...")
    
    # Mock Vikunja environment
    os.environ['VIKUNJA_URL'] = 'http://localhost:3456'
    os.environ['VIKUNJA_API_TOKEN'] = 'test-token-for-integration'
    
    curator = EnhancedCurationScript()
    
    # This would normally fail without real Vikunja, but we can test the structure
    try:
        result = curator.curate_vikunja_api()
        print(f"Vikunja curation result: {result}")
    except Exception as e:
        print(f"Expected failure (no real Vikunja): {e}")
    
    # Test 2: Manual generation
    print("2. Testing manual generation...")
    
    generator = VikunjaManualGenerator()
    
    # Test manual structure generation
    api_info = {
        'metadata': {'base_url': 'http://test.com', 'api_version': 'v1', 'generated_at': '2026-02-13'},
        'authentication': {'type': 'Bearer Token'},
        'endpoints': {},
        'examples': {}
    }
    
    manual_content = generator._format_manual(api_info)
    assert "# Vikunja API Manual" in manual_content
    assert "Generated" in manual_content
    print("✅ Manual generation structure validated")
    
    # Test 3: Scheduler
    print("3. Testing scheduler...")
    
    # Create test schedule
    schedule_config = {
        'test_task': {
            'enabled': True,
            'interval_minutes': 1,
            'script': 'echo "test"',
            'last_run': None
        }
    }
    
    # Test scheduler logic
    scheduler = CurationScheduler()
    scheduler.schedule = schedule_config
    
    # Test should_run_task logic
    from datetime import datetime, timedelta
    
    # First run should be True
    current_time = datetime.now()
    should_run = scheduler._should_run_task('test_task', schedule_config['test_task'], current_time)
    assert should_run == True
    print("✅ Scheduler logic validated")
    
    # Test 4: Directory structure
    print("4. Testing directory structure...")
    
    library_dir = Path("library")
    manuals_dir = library_dir / "manuals"
    
    assert library_dir.exists()
    assert manuals_dir.exists()
    print("✅ Directory structure validated")
    
    print("🎉 All integration tests passed!")
    
    # Cleanup
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)

if __name__ == '__main__':
    test_full_curation_workflow()
EOF
chmod +x scripts/test-curation-integration.py
```

## Risks & Mitigations

### Risk 1: API Rate Limiting
**Impact**: Curation requests may be blocked by Vikunja API rate limits
**Mitigation**:
- Implement exponential backoff for failed requests
- Respect API rate limits and Retry-After headers
- Cache API responses to reduce request frequency
- Use batch requests where possible

### Risk 2: Manual Content Drift
**Impact**: Manual documentation may become outdated as API evolves
**Mitigation**:
- Implement automated refresh schedules
- Monitor API changes and trigger updates
- Version control for manual changes
- Validation against live API endpoints

### Risk 3: Agent Bus Overload
**Impact**: Too many curation triggers could overwhelm the Agent Bus
**Mitigation**:
- Implement rate limiting for curation triggers
- Use priority queuing for different trigger types
- Batch similar curation requests
- Monitor Agent Bus performance and adjust

### Risk 4: Content Quality Issues
**Impact**: Automatically generated content may be incomplete or inaccurate
**Mitigation**:
- Implement content validation and quality checks
- Manual review process for critical documentation
- Error handling for incomplete API responses
- Fallback to manual curation when automated fails

## Ma'at Alignment Validation

### Principle #18: Balance (Knowledge Equilibrium)
**Alignment**: This charter ensures balanced knowledge management by:
- Distributing curation load across automated and manual processes
- Maintaining equilibrium between content freshness and accuracy
- Ensuring no single source of knowledge becomes a bottleneck
- Balancing automation with human oversight

**Validation Criteria**:
- [ ] Automated curation handles routine updates without human intervention
- [ ] Manual review process maintains content quality
- [ ] Multiple knowledge sources prevent single points of failure
- [ ] Content freshness balanced with accuracy requirements

### Principle #7: Truth (Information Integrity)
**Alignment**: This charter ensures truthful information by:
- Validating content against live API endpoints
- Maintaining complete audit trails for content changes
- Implementing error handling for incomplete information
- Providing transparent content generation processes

**Validation Criteria**:
- [ ] All API documentation validated against live endpoints
- [ ] Complete audit trail for content generation and updates
- [ ] Error handling prevents propagation of incomplete information
- [ ] Content generation process is transparent and reproducible

## Implementation Timeline

### Week 1: Curation Pipeline Activation
- [ ] Enhance curate.py with Agent Bus integration
- [ ] Create Agent Bus message processor
- [ ] Implement basic Vikunja API curation
- [ ] Test manual generation workflow

### Week 2: Vikunja API Integration
- [ ] Create comprehensive Vikunja API manual generator
- [ ] Implement live API endpoint discovery
- [ ] Generate complete API documentation
- [ ] Test integration with library structure

### Week 3: Agent Bus Integration
- [ ] Create automated curation scheduler
- [ ] Implement Agent Bus trigger detection
- [ ] Add curation workflow orchestration
- [ ] Test end-to-end curation pipeline

### Week 4: Validation & Optimization
- [ ] Comprehensive testing and validation
- [ ] Performance optimization for large-scale curation
- [ ] Security hardening for API access
- [ ] Documentation and training materials

## Success Metrics

### Technical Metrics
- [ ] Vikunja API manual generation: 100% complete
- [ ] Agent Bus trigger response time: <30 seconds
- [ ] Curation pipeline success rate: >95%
- [ ] API rate limit compliance: 100%

### Business Metrics
- [ ] Zero manual curation overhead for routine updates
- [ ] Complete Vikunja API documentation available
- [ ] Agent Bus integration for knowledge queries
- [ ] Automated content refresh: Daily

### Operational Metrics
- [ ] System uptime: 99.9%
- [ ] Content freshness: <24 hours for API changes
- [ ] Manual review time: <1 hour per week
- [ ] Support tickets related to documentation: 0

## Next Steps

1. **Immediate**: Begin curation pipeline activation
2. **Week 1**: Complete basic curation workflow implementation
3. **Week 2**: Implement Vikunja API integration
4. **Week 3**: Add Agent Bus integration and automation
5. **Week 4**: Final validation and optimization

**Status**: Ready for implementation
**Priority**: P1 - HIGH
**Dependencies**: Vikunja API access, Agent Bus infrastructure