from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./backend/app.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Yield a database session for dependency injection."""
    with Session(engine) as session:
        yield session
