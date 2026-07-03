from config import load_app_config
load_app_config()

from database import SessionLocal
from models import PensumRight


def main() -> None:
    db = SessionLocal()
    try:
        rights = (
            db.query(PensumRight)
            .order_by(PensumRight.LOGIN.asc(), PensumRight.ID.asc())
            .all()
        )

        if not rights:
            print("Brak rekordów w ANS_PENSUM_PRAWO.")
            return

        print(f"Znaleziono {len(rights)} rekordów:")
        print("ID\tLOGIN\tPRAWO")
        for row in rights:
            print(f"{row.ID}\t{row.LOGIN}\t{row.PRAWO}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
