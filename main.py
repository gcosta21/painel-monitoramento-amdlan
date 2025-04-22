from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./monitoramento.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

class Monitoramento(Base):
    __tablename__ = "monitoramento"
    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String)
    usoCPU = Column(Float)
    usoRAM = Column(Float)
    usoDisco = Column(Float)
    temperaturaCPU = Column(Float)
    uptimeHoras = Column(Float)
    firebirdRodando = Column(Boolean)
    tamanhoBancoMB = Column(Float)
    dataHoraUltimoBackup = Column(DateTime)
    dataHoraUltimaValidacao = Column(DateTime)
    validacaoComErro = Column(Boolean)
    dataHoraEnvio = Column(DateTime, default=datetime.utcnow)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Liberar acesso de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint para forçar a criação da tabela (usar 1x)
@app.get("/api/teste-criacao")
def criar_tabela_manual():
    try:
        Base.metadata.create_all(bind=engine)
        return {"status": "ok", "mensagem": "Tabela criada com sucesso (ou já existia)."}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

# Envio de dados para o banco
@app.post("/api/dados")
async def receber_dados(request: Request):
    data = await request.json()
    db = SessionLocal()
    try:
        registro = Monitoramento(
            cliente=data.get("cliente"),
            usoCPU=data.get("usoCPU"),
            usoRAM=data.get("usoRAM"),
            usoDisco=data.get("usoDisco"),
            temperaturaCPU=data.get("temperaturaCPU"),
            uptimeHoras=data.get("uptimeHoras"),
            firebirdRodando=data.get("firebirdRodando"),
            tamanhoBancoMB=data.get("tamanhoBancoMB"),
            dataHoraUltimoBackup=datetime.fromisoformat(data.get("dataHoraUltimoBackup")) if data.get("dataHoraUltimoBackup") else None,
            dataHoraUltimaValidacao=datetime.fromisoformat(data.get("dataHoraUltimaValidacao")) if data.get("dataHoraUltimaValidacao") else None,
            validacaoComErro=data.get("validacaoComErro")
        )
        db.add(registro)
        db.commit()
        return {"status": "ok", "mensagem": "Dados armazenados com sucesso"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
    finally:
        db.close()

# Consulta de dados recentes
@app.get("/api/ultimos")
def listar_ultimos():
    db = SessionLocal()
    try:
        registros = db.query(Monitoramento).order_by(desc(Monitoramento.dataHoraEnvio)).limit(50).all()
        return [r.__dict__ for r in registros if "_sa_instance_state" not in r.__dict__]
    finally:
        db.close()
