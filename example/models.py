import sqlalchemy as sa
from starlette_core.database import Base


class DemoModel(Base):
    name = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.Text(), nullable=True)

    def __str__(self):
        return self.name
