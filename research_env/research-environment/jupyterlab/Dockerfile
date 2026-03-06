# JupyterLab Research Environment for XNAi Foundation
# Multi-stage build for optimal size and functionality

FROM jupyter/scipy-notebook:latest AS base

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Switch back to jovyan user
USER $NB_UID

# Install Python dependencies for XNAi integration
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy integration scripts
COPY ../scripts/ /home/jovyan/work/scripts/
COPY config/ /home/jovyan/work/config/

# Set up JupyterLab extensions for research
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager \
    && jupyter lab build

# Create directories for research notebooks
RUN mkdir -p /home/jovyan/work/notebooks/{classical_studies,ai_research,documentation}

# Copy example notebooks
COPY notebooks/ /home/jovyan/work/notebooks/

# Configure JupyterLab
COPY config/jupyter_notebook_config.py /home/jovyan/.jupyter/jupyter_notebook_config.py

# Set working directory
WORKDIR /home/jovyan/work

# Expose JupyterLab port
EXPOSE 8888

# Start JupyterLab with custom configuration
CMD ["start-notebook.sh", \
     "--NotebookApp.token=''", \
     "--NotebookApp.password=''", \
     "--NotebookApp.allow_origin='*'", \
     "--NotebookApp.disable_check_xsrf=True", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser"]