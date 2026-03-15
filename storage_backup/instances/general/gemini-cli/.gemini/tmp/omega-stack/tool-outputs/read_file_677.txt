# XNAi Foundation Research Environment

A comprehensive JupyterLab-based research environment integrated with Vikunja task management and intelligent model routing for advanced research workflows.

## Overview

This research environment provides:

- **JupyterLab Integration**: Full-featured JupyterLab environment with classical studies support
- **Vikunja Task Management**: Seamless integration with XNAi Foundation's task management system
- **Intelligent Model Routing**: Automatic model selection based on task type and content
- **Research Queue System**: Asynchronous processing of research tasks
- **Classical Studies Support**: Specialized tools for ancient Greek and Latin text analysis

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   JupyterLab    │    │   Vikunja API    │    │   Model Router  │
│   Notebooks     │◄──►│   Task Mgmt      │◄──►│   Selection     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Classical       │    │ Research Queue   │    │ Redis Cache     │
│ Text Processor  │    │ Worker           │    │ & Pub/Sub       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Documentation   │    │ PostgreSQL DB    │    │ Async Workers   │
│ Generator       │    │ (Tasks & Data)   │    │ (Processing)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the XNAi Foundation repository
git clone https://github.com/Xoe-NovAi/xoe-novai-foundation.git
cd xoe-novai-foundation

# Navigate to research environment
cd research-environment
```

### 2. Configure Environment

Create a `.env` file with your configuration:

```bash
# Vikunja Configuration
VIKUNJA_URL=http://localhost:3456/api/v1
VIKUNJA_API_TOKEN=your_api_token_here

# Model Router Configuration
MODEL_ROUTER_CONFIG=configs/model-router.yaml

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

### 3. Start the Environment

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Access Services

- **JupyterLab**: http://localhost:8888
- **Vikunja**: http://localhost:3456
- **Documentation**: http://localhost:8000

## Features

### JupyterLab Integration

#### Classical Studies Support
- Ancient Greek text processing with CLTK
- Latin text analysis tools
- Classical language tokenization
- Historical text normalization

#### Research Task Integration
```python
from jupyter_vikunja_integration import init_research_environment, create_task_from_notebook

# Initialize environment
env = init_research_environment()

# Create research task from notebook
task = create_task_from_notebook(
    title="Ancient Greek Text Analysis",
    description="Analyze theological terms in John 1:1-3",
    project="Classical Studies",
    job_type="analysis",
    content=greek_text
)
```

#### Automatic Model Routing
- Content-based model selection
- Job type optimization
- Performance-aware routing
- Cost-effective model usage

### Vikunja Task Management

#### Task Creation and Tracking
- Create tasks from notebook cells
- Track progress during execution
- Complete tasks with detailed results
- Automatic task categorization

#### Research Queue Integration
- Asynchronous task processing
- Priority-based task handling
- Error handling and retry logic
- Task status monitoring

### Model Router

#### Intelligent Selection
```python
from model_router import ModelRouter

router = ModelRouter('config/model-router.yaml')
model_info = await router.select_model('translation', content)

# Returns:
# {
#     'model': 'gpt-4o',
#     'reasoning': 'Selected gpt-4o for translation job',
#     'confidence': 0.95
# }
```

#### Configuration-Based Routing
- YAML-based model configuration
- Performance metrics integration
- Cost optimization
- Provider fallback mechanisms

## Usage Examples

### 1. Ancient Greek Text Analysis

```python
# Import classical text processing
from cltk.corpus.greek.alphabet import normalize_grc
from cltk.tokenize.word import WordTokenizer

# Load and process text
greek_text = "Ἐν ἀρχῇ ἦν ὁ λόγος..."
normalized = normalize_grc(greek_text)
tokenizer = WordTokenizer('greek')
words = tokenizer.tokenize(normalized)

# Create research task
task = create_task_from_notebook(
    title="Greek Text Analysis",
    description="Analyze word frequency and theological terms",
    project="Classical Studies",
    job_type="analysis",
    content=normalized
)
```

### 2. Research Task Management

```python
# Track task progress
env.update_task_progress(task['id'], 50, "Halfway through analysis")

# Complete task with results
results = {
    'word_count': len(words),
    'frequency_analysis': word_freq,
    'theological_terms': theological_terms
}

env.complete_research_task(task['id'], str(results))
```

### 3. Model Selection

```python
# Automatic model selection
model_info = await router.select_model('translation', greek_text)
print(f"Selected model: {model_info['model']}")

# Manual model override
model_info = await router.select_model('analysis', content, preferred_model='gpt-4o')
```

## Configuration

### Model Router Configuration

Create `config/model-router.yaml`:

```yaml
models:
  gpt-4o:
    priority: 1
    cost_per_token: 0.00003
    max_tokens: 128000
    capabilities:
      - translation
      - analysis
      - research
    providers:
      - openai
      - anthropic

  gpt-4o-mini:
    priority: 2
    cost_per_token: 0.000006
    max_tokens: 128000
    capabilities:
      - analysis
      - summarization
    providers:
      - openai

routing_rules:
  content_length_threshold: 5000
  classical_keywords:
    - greek
    - latin
    - ancient
    - classical
    - theology
  job_type_preferences:
    translation: gpt-4o
    analysis: gpt-4o-mini
    research: gpt-4o
```

### Vikunja Integration

Configure Vikunja for research tasks:

```yaml
# Vikunja configuration
database:
  type: postgres
  host: postgres:5432
  database: xnai_research
  username: vikunja
  password: vikunja_password

service:
  jwt_secret: research_secret_key
  frontend_url: http://localhost:8888
  register: true
  mail_from_address: noreply@xnai.foundation
```

## Development

### Adding New Services

1. Create Dockerfile for new service
2. Add service to `docker-compose.yml`
3. Create corresponding Python module
4. Update integration scripts

### Extending Model Router

1. Add new models to configuration
2. Implement model-specific logic
3. Update routing algorithms
4. Add performance metrics

### Classical Studies Extensions

1. Add new language support to CLTK
2. Create specialized tokenizers
3. Implement domain-specific analysis
4. Add visualization tools

## Monitoring and Maintenance

### Service Health

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# Monitor resource usage
docker stats
```

### Task Monitoring

```python
# Get task status
task_status = env.get_task_status(task_id)
print(f"Task progress: {task_status['progress']}%")

# Get all tasks for notebook
tasks = env.get_tasks_from_notebook(notebook_path)
```

### Performance Optimization

- Monitor Redis memory usage
- Optimize model selection algorithms
- Tune PostgreSQL performance
- Scale workers based on queue length

## Troubleshooting

### Common Issues

1. **JupyterLab not accessible**: Check port 8888 is available
2. **Vikunja connection failed**: Verify database connectivity
3. **Model routing errors**: Check configuration file syntax
4. **Redis connection issues**: Verify Redis service is running

### Debug Mode

Enable debug logging:

```bash
# Set debug environment variable
export DEBUG=true

# Restart services
docker-compose restart
```

### Logs and Diagnostics

```bash
# View specific service logs
docker-compose logs jupyterlab
docker-compose logs vikunja
docker-compose logs research-queue
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Include unit tests

### Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Test specific module
python -m pytest tests/test_model_router.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Create GitHub issues for bugs and feature requests
- Join our Discord community
- Check the documentation in `/docs`
- Review existing research notebooks for examples

## Contributing Organizations

This research environment is part of the XNAi Foundation's mission to democratize enterprise-grade AI research tools. Special thanks to our partners in classical studies and AI research for their contributions to this project.