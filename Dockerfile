# --- STAGE 1: Build the React Frontend ---
FROM node:20-slim AS build-stage
WORKDIR /app/frontend

# Copy package files from the GoldAI directory
COPY GoldAI/frontend/package*.json ./
RUN npm install

# Copy the source code and build
COPY GoldAI/frontend/ ./
RUN npm run build

# --- STAGE 2: Build the Python Backend ---
FROM python:3.10-slim
WORKDIR /app

# Create a non-root user for Hugging Face security
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

# Install Python requirements
COPY --chown=user:user GoldAI/backend/requirements.txt ./
# Ensure huggingface_hub is installed for cloud sync
RUN pip install --no-cache-dir --user -r requirements.txt huggingface_hub

# Copy backend files to the container's /app/backend/ folder
COPY --chown=user:user GoldAI/backend/ ./backend/

# Copy the React build to /app/frontend/dist/
COPY --chown=user:user --from=build-stage /app/frontend/dist ./frontend/dist

# Hugging Face uses port 7860 by default
EXPOSE 7860

# --- THE FIX IS BELOW ---
# Added '-u' to python to UNBUFFER the logs (shows output instantly)
CMD ["sh", "-c", "python -u backend/live.py & uvicorn backend.api:app --host 0.0.0.0 --port 7860"]