# Stage 1: build
FROM python:3.12-slim AS build
WORKDIR /app

# Copia apenas requirements primeiro (cache melhor)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto da aplicação
COPY . .

# Stage 2: runtime
FROM python:3.12-slim
WORKDIR /app

# Copia libs e código da fase build
COPY --from=build /app /app

# Porta usada pelo uvicorn
EXPOSE 8000

# Comando para iniciar a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
