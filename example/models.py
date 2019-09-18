import sqlalchemy as sa
from starlette_core.database import Base


class DemoModel(Base):
    name = sa.Column(sa.String(), nullable=False, unique=True)
    description = sa.Column(sa.Text(), nullable=True)

    def __str__(self):
        return self.name


class SystemSettingsModel(Base):
    setting_1 = sa.Column(sa.String(), nullable=True)
    setting_2 = sa.Column(sa.String(), nullable=True)
    setting_3 = sa.Column(sa.String(), nullable=True)
    setting_4 = sa.Column(sa.String(), nullable=True)

    def __str__(self):
        return "Update System Settings"
