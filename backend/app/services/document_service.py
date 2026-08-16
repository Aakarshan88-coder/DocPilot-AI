from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    filename: str,
    file_path: str,
    user_id: int
):
    new_document = Document(
        filename=filename,
        file_path=file_path,
        user_id=user_id
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


def get_user_documents(
    db: Session,
    user_id: int
):
    return db.query(Document).filter(
        Document.user_id == user_id
    ).all()


def get_user_document(
    db: Session,
    document_id: int,
    user_id: int
):
    return db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()


def delete_document(
    db: Session,
    document_id: int,
    user_id: int
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()

    if not document:
        return None

    db.delete(document)
    db.commit()

    return document