from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()


class HealthPolicy(Base):
    __tablename__ = "health_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(3), nullable=False, index=True)  # ISO 3166-1 alpha-3: USA, GBR, MEX
    country_name = Column(String(100), nullable=False)
    source = Column(String(50), nullable=False)  # e.g., "CMS", "WHO", "CCHP", "NHS", "COFEPRIS"
    source_url = Column(Text)
    category = Column(String(100), index=True)  # e.g., "telehealth", "drug_regulation", "licensing"
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    full_text = Column(Text)
    original_language = Column(String(10), default="en")  # ISO 639-1
    english_translation = Column(Text)  # populated if original_language != "en"
    effective_date = Column(String(50))
    last_updated = Column(String(50))
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    policy_id_external = Column(String(200))  # ID from the original source

    # Verification fields
    verification_status = Column(String(20), default="unverified")  # unverified, machine_verified, user_verified, failed
    verified_by = Column(String(50))  # "url_checker", "user:alley", agent name, etc.
    verified_at = Column(DateTime)
    verification_notes = Column(Text)  # Why it passed/failed, what was checked


class WHOIndicator(Base):
    __tablename__ = "who_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(3), nullable=False, index=True)
    country_name = Column(String(100))
    indicator_code = Column(String(50), nullable=False)
    indicator_name = Column(String(500))
    year = Column(Integer)
    value = Column(Float)
    value_type = Column(String(50))  # numeric, percentage, etc.
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PolicyUpdate(Base):
    __tablename__ = "policy_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(3), nullable=False, index=True)
    source = Column(String(50), nullable=False)
    change_type = Column(String(20))  # "new", "modified", "removed"
    title = Column(String(500))
    summary = Column(Text)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_engine(db_path="data/policies.db"):
    return create_engine(f"sqlite:///{db_path}", echo=False)


def get_session(db_path="data/policies.db"):
    engine = get_engine(db_path)
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(db_path="data/policies.db"):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return engine
