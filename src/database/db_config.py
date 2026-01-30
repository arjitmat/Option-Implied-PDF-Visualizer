"""
Database configuration and session management.
"""

import os
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base


class DatabaseManager:
    """
    Manages database connections and sessions.

    Singleton pattern ensures only one database connection pool exists.
    """

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = None, echo: bool = False):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file. If None, uses default from config.
            echo: If True, SQL statements are logged (useful for debugging)
        """
        if self._engine is None:
            if db_path is None:
                # Use default path from project root
                project_root = Path(__file__).parent.parent.parent
                db_dir = project_root / 'data'
                db_dir.mkdir(exist_ok=True)
                db_path = str(db_dir / 'pdf_visualizer.db')

            # Create engine
            self._engine = self._create_engine(db_path, echo)

            # Enable foreign keys for SQLite
            @event.listens_for(self._engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            # Create session factory
            self._session_factory = sessionmaker(bind=self._engine)

            # Create all tables
            self.create_tables()

    @staticmethod
    def _create_engine(db_path: str, echo: bool = False):
        """
        Create SQLAlchemy engine.

        Args:
            db_path: Path to database file
            echo: If True, log SQL statements

        Returns:
            SQLAlchemy engine
        """
        # SQLite connection string
        database_url = f"sqlite:///{db_path}"

        # Create engine
        # Use StaticPool for SQLite to avoid threading issues
        engine = create_engine(
            database_url,
            echo=echo,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )

        return engine

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self._engine)

    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(self._engine)

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy session

        Note:
            Caller is responsible for closing the session.
        """
        return self._session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around database operations.

        Usage:
            with db_manager.session_scope() as session:
                session.add(obj)
                # Changes are automatically committed on exit
                # Or rolled back on exception

        Yields:
            SQLAlchemy session
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_engine(self):
        """Get the SQLAlchemy engine."""
        return self._engine

    def __repr__(self):
        return f"<DatabaseManager(engine={self._engine})>"


# Convenience function for getting a session
def get_db_session() -> Session:
    """
    Get a new database session.

    Returns:
        SQLAlchemy session

    Example:
        session = get_db_session()
        try:
            snapshots = session.query(PDFSnapshot).all()
        finally:
            session.close()
    """
    db_manager = DatabaseManager()
    return db_manager.get_session()


# Convenience context manager
@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with db_session() as session:
            snapshots = session.query(PDFSnapshot).all()

    Yields:
        SQLAlchemy session
    """
    db_manager = DatabaseManager()
    with db_manager.session_scope() as session:
        yield session


if __name__ == "__main__":
    # Test database setup
    print("Testing database configuration...")

    # Initialize database manager
    db_manager = DatabaseManager(echo=True)
    print(f"✅ Database manager created: {db_manager}")

    # Check if tables were created
    from sqlalchemy import inspect
    inspector = inspect(db_manager.get_engine())
    tables = inspector.get_table_names()
    print(f"\n✅ Tables created: {tables}")

    # Test session creation
    with db_manager.session_scope() as session:
        print(f"\n✅ Session created: {session}")

    print("\n✅ All database configuration tests passed!")
