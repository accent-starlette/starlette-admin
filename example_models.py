import sqlalchemy as sa
from starlette_core.database import Base


class DemoModel(Base):
    name = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.Text(), nullable=False)

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
