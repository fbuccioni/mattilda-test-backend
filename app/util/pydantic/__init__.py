from typing import Mapping, Any, List, Type, Dict, Optional, Sequence, Callable

from pydantic import BaseModel

from .partial_model import partial_model, partial_model_factory


def model_annotations_with_parents(model: BaseModel) -> Mapping[str, Any]:
    parent_models: List[Type] = [
        parent_model for parent_model in model.__bases__
        if (
            issubclass(parent_model, BaseModel)
            and hasattr(parent_model, '__annotations__')
        )
    ]

    annotations: Dict[str, Any] = {}

    for parent_model in reversed(parent_models):
        annotations.update(model_annotations_with_parents(parent_model))

    annotations.update(model.__annotations__)
    return annotations


def model_inherit_fields(
    exclude: Optional[Sequence[str]] = None,
    include: Optional[Sequence[str]] = None
) -> Callable[[type], type]:
    def wrapper(klass):
        nonlocal exclude, include

        if exclude and include:
            raise ValueError('Is either exclude or include.')

        if exclude:
            fields_to_remove = exclude
        else:
            fields_to_remove = set(klass.__fields__.keys()) - set(include)

        for field in fields_to_remove:
            klass.__fields__.pop(field)

        return klass

    return wrapper
