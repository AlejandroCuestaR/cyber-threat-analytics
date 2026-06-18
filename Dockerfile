FROM python:3.11-slim

WORKDIR /app

# Solo las dependencias necesarias para servir la API
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" scikit-learn joblib numpy pandas pydantic

COPY api/ ./api/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
