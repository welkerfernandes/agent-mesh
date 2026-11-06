FROM node:22-bookworm-slim AS node
FROM python:3.12-slim
WORKDIR /service
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home service && chown service /service
COPY --chown=service:service app ./app
COPY --chown=service:service agents ./agents
USER service
EXPOSE 8301
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8301"]
