import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends,FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from .infrastructure import PublicAPI,Snapshots,tenant
from .contracts import Mission
from .models import Models
from .orchestrator import Orchestrator

def create_app(path=None,api=None,models=None,critic=None):
    api=api or PublicAPI();models=models or Models()
    store=Snapshots(path or os.getenv('DATABASE_PATH','agents.db'))
    orchestrator=Orchestrator(api,models,**({'critic':critic} if critic else {}))
    @asynccontextmanager
    async def lifespan(app):
        yield
        api.close();models.close()
    app=FastAPI(title='Agent Mesh',version='1.0.0',lifespan=lifespan)
    @app.get('/',response_class=HTMLResponse)
    def dashboard():return Path(__file__).with_name('dashboard.html').read_text(encoding='utf-8')
    @app.get('/health')
    def health():return {'status':'ok'}
    @app.post('/api/runs')
    def run(mission:Mission,identity:str=Depends(tenant)):
        result=orchestrator.run(mission)
        return store.save(identity,'agent-run',result)
    @app.get('/api/history')
    def history(identity:str=Depends(tenant)):return store.history(identity)
    return app
app=create_app()
