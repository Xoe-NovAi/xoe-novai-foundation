# JupyterLab Configuration for XNAi Foundation Research Environment
# This configuration optimizes JupyterLab for research workflows with
# Vikunja integration and classical studies support

c = get_config()

# Basic configuration
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
c.NotebookApp.token = ''
c.NotebookApp.password = ''

# Security settings for research environment
c.NotebookApp.allow_origin = '*'
c.NotebookApp.disable_check_xsrf = True
c.NotebookApp.allow_remote_access = True

# File handling and storage
c.FileContentsManager.delete_to_trash = False
c.FileContentsManager.checkpoints_dir = '.ipynb_checkpoints'

# Notebook settings
c.NotebookApp.tornado_settings = {
    'headers': {
        'Content-Security-Policy': "frame-ancestors 'self' http://localhost:*"
    }
}

# Extensions and widgets
c.NotebookApp.nbserver_extensions = {
    'jupyterlab': True,
    'jupyterlab_widgets': True,
    'nb_conda': False,  # Disable if not using conda
}

# Kernel settings
c.KernelManager.shutdown_wait_time = 10.0
c.MappingKernelManager.cull_idle_timeout = 3600  # 1 hour
c.MappingKernelManager.cull_interval = 300  # 5 minutes

# Research-specific settings
c.NotebookApp.contents_manager_class = 'notebook.services.contents.largefilemanager.LargeFileManager'

# Logging configuration
c.Application.log_level = 'INFO'
c.NotebookApp.log_format = '%(color)s[%(levelname)1.1s %(asctime)s.%(msecs)03d %(name)s %(module)s:%(lineno)d]%(end_color)s %(message)s'

# Custom templates for research notebooks
c.NotebookApp.template_file = 'lab'
c.NotebookApp.extra_template_paths = ['/home/jovyan/work/templates']

# Research environment specific settings
c.NotebookApp.default_url = '/lab'
c.NotebookApp.allow_credentials = True

# Performance optimizations for large research datasets
c.FileContentsManager.max_file_size = 100 * 1024 * 1024  # 100MB
c.NotebookApp.iopub_data_rate_limit = 1000000000  # 1GB/s
c.NotebookApp.rate_limit_window = 3.0

# Enable research extensions
c.NotebookApp.nbserver_extensions.update({
    'jupyterlab_git': True,
    'jupyterlab_lsp': True,
    'jupyterlab_code_formatter': True,
})

# Custom research environment settings
import os
RESEARCH_ENV = {
    'vikunja_url': os.getenv('VIKUNJA_URL', 'http://localhost:3456/api/v1'),
    'model_router_config': os.getenv('MODEL_ROUTER_CONFIG', 'configs/model-router.yaml'),
    'research_projects': [
        'Classical Studies',
        'AI Research', 
        'Documentation',
        'Development'
    ]
}

# Save research environment configuration
with open('/home/jovyan/work/research_config.json', 'w') as f:
    import json
    json.dump(RESEARCH_ENV, f, indent=2)