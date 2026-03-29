FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements first
COPY --chown=user server/requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir openenv-core fastapi uvicorn

# Copy all files
COPY --chown=user . /app

# Set PYTHONPATH
ENV PYTHONPATH="/app:$PYTHONPATH"

# Expose port 7860 for HF Spaces
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the server on port 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]