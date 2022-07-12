from typing import Optional

from pydantic import BaseModel


def partial_model_factory(model: BaseModel, prefix: str = "Partial", name: str = None) -> BaseModel:
    from . import model_annotations_with_parents

    if not name:
        name = f"{prefix}{model.__name__}"

    return type(
        name, (model,),
        dict(
            __module__=model.__module__,
            __annotations__={
                k: Optional[v]
                for k, v in model_annotations_with_parents(model).items()
            }
        )
    )


def partial_model(cls: BaseModel) -> BaseModel:
    return partial_model_factory(cls, name=cls.__name__)
