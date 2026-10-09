"""navision."""
from application.config.config import Config
from datetime import date, datetime, time
from decimal import Decimal
from application.config.urls import mssql_url
from sqlalchemy import create_engine
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import Union


NULLDATE = datetime(1753, 1, 1, 0, 0, 0)


class Base(DeclarativeBase):
    pass


NAV_SECRETS = Config()['navision']
NAV_COMPANY = NAV_SECRETS.get('company')
NAV_URL = mssql_url(NAV_SECRETS, 'Panel - tables')
ENGINE = create_engine(NAV_URL, echo=False)


class SalesReportEntry(Base):
    __tablename__ = f'{NAV_COMPANY}$Sales Report Entry'

    entry_no_: Mapped[int] = mapped_column(
        'Entry No_', primary_key=True, autoincrement=False)
    partner_no_: Mapped[str] = mapped_column(
        'Partner No_', String(20), default='')
    global_localtion_no_: Mapped[str] = mapped_column(
        'Global Location No_', String(20), default='')
    _posting_date: Mapped[datetime] = mapped_column(
        'Posting Date', DateTime, default=NULLDATE)
    item_no_: Mapped[str] = mapped_column('Item No_', String(20), default='')
    quantity: Mapped[Decimal] = mapped_column(
        'Quantity', Numeric(38, 20), default=Decimal(0))
    _initial_reporting_date: Mapped[datetime] = mapped_column(
        'Initial reporting Date', DateTime, default=NULLDATE)
    _ending_reporting_date: Mapped[datetime] = mapped_column(
        'Ending reporting Date', DateTime, default=NULLDATE)
    eanart: Mapped[str] = mapped_column('EANART', String(20), default='')
    codcom: Mapped[str] = mapped_column('CODCOM', String(20), default='')
    codpro: Mapped[str] = mapped_column('CODPRO', String(20), default='')
    eanven: Mapped[str] = mapped_column('EANVEN', String(20), default='')
    eanlug: Mapped[str] = mapped_column('EANLUG', String(20), default='')
    reference: Mapped[str] = mapped_column('REFERENCE', String(30), default='')
    posting_datetime: Mapped[datetime] = mapped_column(
        'Posting Datetime', DateTime, default=NULLDATE)

    @hybrid_property
    def posting_date(self) -> datetime:
        return self._posting_date

    @posting_date.setter
    def posting_date(self, value: Union[date, datetime]):
        if type(value) is date:
            self._posting_date = datetime.combine(
                value, time(0, 0), tzinfo=None)
        else:
            self._posting_date = value

    @hybrid_property
    def initial_reporting_date(self) -> datetime:
        return self._initial_reporting_date

    @initial_reporting_date.setter
    def initial_reporting_date(self, value: Union[date, datetime]):
        if type(value) is date:
            self._initial_reporting_date = datetime.combine(
                value, time(0, 0), tzinfo=None)
        else:
            self._initial_reporting_date = value

    @hybrid_property
    def ending_reporting_date(self) -> datetime:
        return self._ending_reporting_date

    @ending_reporting_date.setter
    def ending_reporting_date(self, value: Union[date, datetime]):
        if type(value) is date:
            self._ending_reporting_date = datetime.combine(
                value, time(0, 0), tzinfo=None)
        else:
            self._ending_reporting_date = value

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(entry_no_={self.entry_no_!r}, '
            f'partner_no_={self.partner_no_!r}, item_no_={self.item_no_!r})')


BINDS = {
    SalesReportEntry: ENGINE,
}
