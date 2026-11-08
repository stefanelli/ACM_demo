"""Seed the database with mock market data.

Usage:
    python -m app.seed
"""

from app.db import Base, get_engine, get_session_factory
from app.mds.service import refresh


def main() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)

    session = get_session_factory()()
    try:
        n_contracts, n_quotes = refresh(session)
    finally:
        session.close()

    print(f"Seeded {n_contracts} contracts and {n_quotes} quotes.")


if __name__ == "__main__":
    main()
