from typing import List
from dataclasses import dataclass, field, replace


@dataclass
class DemoObject:
    id: int
    name: str
    description: str
    sex: str
    password: str
    tags: List[str]
    options: List[str]
    choices: List[str]
    choice: str
    agree: bool

    def __str__(self):
        return self.name


def object_factory() -> List[DemoObject]:
    return [
        DemoObject(
            id=id,
            name=f"Record {id:02d}",
            description="Some description",
            sex="Male",
            password="",
            tags=["awesome", "starlette"],
            options=["One"],
            choices=["One"],
            choice="One",
            agree=True,
        ) for id in range(1, 16)
    ]


@dataclass
class DemoStore:
    objects: List[DemoObject] = field(default_factory=object_factory)

    def _next_id(self):
        return self.objects[-1].id + 1 if self.objects else 1

    def get(self, id: int) -> DemoObject:
        return next(o for o in self.objects if o.id == id)

    def create(self, data: dict) -> DemoObject:
        obj = DemoObject(id=self._next_id(), **data)
        self.objects.append(obj)
        return obj
    
    def update(self, obj: DemoObject, data: dict) -> DemoObject:
        index = self.objects.index(obj)
        replaced = replace(obj, **data)
        self.objects[index] = replaced
        return replaced

    def delete(self, obj: DemoObject) -> None:
        index = self.objects.index(obj)
        self.objects.pop(index)


store = DemoStore()
