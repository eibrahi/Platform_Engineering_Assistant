from pydantic import BaseModel


def reject_null(model: BaseModel, fields: tuple[str, ...]) -> None:
    """Für Update-Schemas: ein mitgeschicktes Pflichtfeld darf nicht null sein."""
    for field in fields:
        if field in model.model_fields_set and getattr(model, field) is None:
            raise ValueError(f'{field} darf nicht null sein')
