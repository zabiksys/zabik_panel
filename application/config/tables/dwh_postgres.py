"""dwh_postgres."""
from application.config.config import Config
from application.utils import date2key, key2date
from datetime import date, datetime
from decimal import Decimal
from application.config.urls import postgres_url
from sqlalchemy import create_engine
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func
from typing import List, Optional


class Base(DeclarativeBase):
    pass


APPLICATION_NAME = 'Panel - tables'

DWH_POSTGRES_SECRETS = Config()['datawarehouse']
DWH_POSTGRES_URL = postgres_url(DWH_POSTGRES_SECRETS, APPLICATION_NAME)
ENGINE = create_engine(DWH_POSTGRES_URL, echo=False)


class _DimBase:
    key: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[Optional[str]] = mapped_column(String(50))
    caption: Mapped[Optional[str]] = mapped_column(String(71))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, code={self.code!r})')


class DimAccountManager(_DimBase, Base):
    __tablename__ = 'dim_account_manager'


class DimArea(Base):
    __tablename__ = 'dim_area'

    key: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10))
    text: Mapped[Optional[str]] = mapped_column(String(50))
    post_code_prefix: Mapped[Optional[str]] = mapped_column(String(20))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, code={self.code!r})')


class DimCampaign(_DimBase, Base):
    __tablename__ = 'dim_campaign'


class DimCampaignYear(_DimBase, Base):
    __tablename__ = 'dim_campaign_year'


class DimCatalog(Base):
    __tablename__ = 'dim_catalog'

    key: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10))


class DimCommercialArea(_DimBase, Base):
    __tablename__ = 'dim_commercial_area'


class DimCountryRegion(Base):
    __tablename__ = 'dim_country_region'

    key: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10))
    name: Mapped[Optional[str]] = mapped_column(String(50))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, code={self.code!r})')


class DimCustomer(Base):
    __tablename__ = 'dim_customer'

    key: Mapped[int] = mapped_column(primary_key=True)
    no_: Mapped[str] = mapped_column(String(20))
    caption: Mapped[Optional[str]] = mapped_column(String(71))
    name: Mapped[Optional[str]] = mapped_column(String(50))
    salesperson_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_salesperson_purchaser.key'))
    salesperson: Mapped[List['DimSalespersonPurchaser']] = relationship(
        backref='customers')
    purchasegroup_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_purchase_group.key'))
    purchasegroup: Mapped['DimPurchaseGroup'] = relationship(
        backref='customers')
    channel_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_customer_channel.key'))
    channel: Mapped['DimCustomerChannel'] = relationship(backref='customers')
    city: Mapped[Optional[str]] = mapped_column(String(30))
    county_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_area.key'))
    county: Mapped['DimArea'] = relationship(backref='customers')
    country_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_country_region.key'))
    country: Mapped['DimCountryRegion'] = relationship(backref='customers')
    commercial_area_key: Mapped[int] = mapped_column(
        ForeignKey('dim_commercial_area.key'))
    commercial_area: Mapped['DimCommercialArea'] = relationship(
        backref='customers')
    accountmanager_key: Mapped[int] = mapped_column(
        ForeignKey('dim_account_manager.key'))
    accountmanager: Mapped['DimAccountManager'] = relationship(
        backref='customers')
    customercategory_key: Mapped[int] = mapped_column(
        ForeignKey('dim_customer_category.key'))
    customercategory: Mapped['DimCustomerCategory'] = relationship(
        backref='customers')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'no_={self.no_!r}, name={self.name!r})')


class DimCustomerCategory(_DimBase, Base):
    __tablename__ = 'dim_customer_category'


class DimCustomerChannel(_DimBase, Base):
    __tablename__ = 'dim_customer_channel'


class DimDivision(_DimBase, Base):
    __tablename__ = 'dim_division'


class DimEDIPartner(Base):
    __tablename__ = 'dim_edi_partner'

    key: Mapped[int] = mapped_column(primary_key=True)
    no_: Mapped[str] = mapped_column(String(20))
    name: Mapped[Optional[str]] = mapped_column(String(50))
    purchasegroup_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_purchase_group.key'))
    purchasegroup: Mapped['DimPurchaseGroup'] = relationship(
        backref='edi_partners')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'no_={self.no_!r}, name={self.name!r})')


class DimEDIPartnerLine(Base):
    __tablename__ = 'dim_edi_partner_line'

    key: Mapped[int] = mapped_column(primary_key=True)
    edi_partner_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_edi_partner.key'))
    edi_partner: Mapped['DimEDIPartner'] = relationship(
        backref='edi_partner_lines')
    no_: Mapped[str] = mapped_column(String(20))
    name: Mapped[Optional[str]] = mapped_column(String(50))
    name_2: Mapped[Optional[str]] = mapped_column(String(50))
    global_location_no_: Mapped[Optional[str]] = mapped_column(String(20))
    salesperson_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_salesperson_purchaser.key'))
    salesperson: Mapped['DimSalespersonPurchaser'] = relationship()
    link_to_customer_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_customer.key'))
    link_to_customer: Mapped['DimCustomer'] = relationship()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'no_={self.no_!r}, name={self.name!r})')


class DimItem(Base):
    __tablename__ = 'dim_item'

    key: Mapped[int] = mapped_column(primary_key=True)
    no_: Mapped[str] = mapped_column(String(20))
    caption: Mapped[Optional[str]] = mapped_column(String(71))
    description: Mapped[Optional[str]] = mapped_column(String(50))
    division_key: Mapped[int] = mapped_column(ForeignKey('dim_division.key'))
    division: Mapped['DimDivision'] = relationship(backref='items')
    itemline_key: Mapped[int] = mapped_column(ForeignKey('dim_item_line.key'))
    itemline: Mapped['DimItemLine'] = relationship(backref='items')
    lifecycle_key: Mapped[int] = mapped_column(
        ForeignKey('dim_item_life_cycle.key'))
    lifecycle: Mapped['DimLifeCycle'] = relationship(backref='items')
    npd_key: Mapped[int] = mapped_column(ForeignKey('dim_npd.key'))
    npd: Mapped['DimNPD'] = relationship(backref='items')
    vendor_key: Mapped[int] = mapped_column(ForeignKey('dim_vendor.key'))
    vendor: Mapped['DimVendor'] = relationship(backref='items')
    report_order: Mapped[Optional[int]] = mapped_column()
    state: Mapped[str] = mapped_column(String(20))
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    unit_volume: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    gross_weight: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    direct_unit_cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    product_manager_key: Mapped[int] = mapped_column(
        ForeignKey('dim_product_manager.key'))
    product_manager: Mapped['DimProductManager'] = relationship(
        backref='items')
    report_order_2: Mapped[Optional[int]] = mapped_column()
    report_order_3: Mapped[Optional[int]] = mapped_column()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'no_={self.no_!r}, description={self.description!r})')


class DimItemLine(_DimBase, Base):
    __tablename__ = 'dim_item_line'


class DimLifeCycle(_DimBase, Base):
    __tablename__ = 'dim_item_life_cycle'


class DimNPD(_DimBase, Base):
    __tablename__ = 'dim_npd'


class DimProductManager(_DimBase, Base):
    __tablename__ = 'dim_product_manager'


class DimPurchaseGroup(_DimBase, Base):
    __tablename__ = 'dim_purchase_group'


class DimSalespersonPurchaser(Base):
    __tablename__ = 'dim_salesperson_purchaser'

    key: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10))
    caption: Mapped[str] = mapped_column(String(61))
    name: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[str] = mapped_column(String(20))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, code={self.code!r})')


class DimVendor(Base):
    __tablename__ = 'dim_vendor'

    key: Mapped[int] = mapped_column(primary_key=True)
    no_: Mapped[str] = mapped_column(String(20))
    caption: Mapped[Optional[str]] = mapped_column(String(71))
    name: Mapped[Optional[str]] = mapped_column(String(50))
    county_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_area.key'))
    county: Mapped['DimArea'] = relationship(backref='vendors')
    country_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_country_region.key'))
    country: Mapped['DimCountryRegion'] = relationship(backref='vendors')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'no_={self.no_!r}, name={self.name!r})')


class FactAgreements(Base):
    __tablename__ = 'fact_agreements'

    key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    campaign_year_key: Mapped[int] = mapped_column(
        ForeignKey('dim_campaign_year.key'))
    campaign_year: Mapped['DimCampaignYear'] = relationship(
        backref='fact_agreements')
    campaign_key: Mapped[int] = mapped_column(
        ForeignKey('dim_campaign.key'))
    campaign: Mapped['DimCampaign'] = relationship(
        backref='fact_agreements')
    purchasegroup_key: Mapped[int] = mapped_column(
        ForeignKey('dim_purchase_group.key'))
    purchase_group: Mapped['DimPurchaseGroup'] = relationship(
        backref='fact_agreements')
    customer_key: Mapped[int] = mapped_column(
        ForeignKey('dim_customer.key'))
    customer: Mapped['DimCustomer'] = relationship(
        backref='fact_agreements')
    item_key: Mapped[int] = mapped_column(ForeignKey('dim_item.key'))
    item: Mapped['DimItem'] = relationship(
        backref='fact_agreements')
    # updated_at: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow)


    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'campaign_year={self.campaign_year.code!r}, '
            f'campaign={self.campaign.code!r}, '
            f'purchase_group={self.purchase_group.code!r}, '
            f'customer={self.customer.no_!r}, '
            f'item={self.item.no_!r})')


class FactItemCustomerSales(Base):
    __tablename__ = 'fact_item_customer_sales'

    key: Mapped[int] = mapped_column(primary_key=True)
    entry_no_: Mapped[Optional[int]] = mapped_column()
    edi_partner_key: Mapped[int] = mapped_column(
        ForeignKey('dim_edi_partner.key'))
    edi_partner: Mapped['DimEDIPartner'] = relationship(
        backref='fact_item_customer_sales')
    edi_partner_line_key: Mapped[int] = mapped_column(
        ForeignKey('dim_edi_partner_line.key'))
    edi_partner_line: Mapped['DimEDIPartnerLine'] = relationship(
        backref='fact_item_customer_sales')
    item_key: Mapped[int] = mapped_column(ForeignKey('dim_item.key'))
    item: Mapped['DimItem'] = relationship(backref='fact_item_customer_sales')
    lifecycle_key: Mapped[int] = mapped_column(ForeignKey('dim_item_life_cycle.key'))
    lifecycle: Mapped['DimLifeCycle'] = relationship(backref='fact_item_customer_sales')
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    posting_date_key: Mapped[int] = mapped_column()
    initial_reporting_date_key: Mapped[int] = mapped_column()
    ending_reporting_date_key: Mapped[int] = mapped_column()
    campaign_key: Mapped[int] = mapped_column(ForeignKey('dim_campaign.key'))
    campaign: Mapped['DimCampaign'] = relationship(backref='fact_item_customer_sales')
    campaign_year_key: Mapped[int] = mapped_column(ForeignKey('dim_campaign_year.key'))
    campaign_year: Mapped['DimCampaignYear'] = relationship(backref='fact_item_customer_sales')
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal(0))
    purchasegroup_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_purchase_group.key'))
    purchasegroup: Mapped['DimPurchaseGroup'] = relationship(
        backref='fact_item_customer_sales')
    eanart: Mapped[Optional[str]] = mapped_column(String(20))
    codcom: Mapped[Optional[str]] = mapped_column(String(20))
    codpro: Mapped[Optional[str]] = mapped_column(String(20))
    eanven: Mapped[Optional[str]] = mapped_column(String(20))
    eanlug: Mapped[Optional[str]] = mapped_column(String(20))
    reference: Mapped[Optional[str]] = mapped_column(String(50))

    def __init__(
            self,
            posting_date: date,
            initial_reporting_date: date,
            ending_reporting_date: date,
            **kw):
        super().__init__(
            posting_date_key=date2key(posting_date),
            initial_reporting_date_key=date2key(initial_reporting_date),
            ending_reporting_date_key=date2key(ending_reporting_date),
            **kw)

    @hybrid_property
    def posting_date(self) -> date:
        return key2date(self.posting_date_key)

    @posting_date.setter
    def posting_date(self, value: date):
        self.posting_date_key = date2key(value)

    @hybrid_property
    def initial_reporting_date(self) -> date:
        return key2date(self.initial_reporting_date_key)

    @initial_reporting_date.setter
    def initial_reporting_date(self, value: date):
        self.initial_reporting_date_key = date2key(value)

    @hybrid_property
    def ending_reporting_date(self) -> date:
        return key2date(self.ending_reporting_date_key)

    @ending_reporting_date.setter
    def ending_reporting_date(self, value: date):
        self.ending_reporting_date_key = date2key(value)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'edi_partner_no_={self.edi_partner.no_!r}, '
            f'item_no_={self.item.no_!r})')


class FactItemCustomerSalesErrors(Base):
    __tablename__ = 'fact_item_customer_sales_errors'

    key: Mapped[int] = mapped_column(primary_key=True)
    partner_no_: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey('dim_edi_partner.no_'))
    partner: Mapped['DimEDIPartner'] = relationship()
    global_location_no_: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey('dim_edi_partner_line.global_location_no_'))
    partner_line: Mapped['DimEDIPartnerLine'] = relationship(
        primaryjoin=(
            'and_(FactItemCustomerSalesErrors.partner_no_'
            '==DimEDIPartnerLine.no_, '
            'FactItemCustomerSalesErrors.global_location_no_'
            '==DimEDIPartnerLine.global_location_no_)'))
    posting_date_key: Mapped[Optional[int]] = mapped_column()
    item_no_: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey('dim_item.no_'))
    item: Mapped['DimItem'] = relationship()
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    initial_reporting_date_key: Mapped[Optional[int]] = mapped_column()
    ending_reporting_date_key: Mapped[Optional[int]] = mapped_column()
    posting_datetime: Mapped[datetime] = mapped_column(DateTime)
    eanart: Mapped[Optional[str]] = mapped_column(String(20))
    codcom: Mapped[Optional[str]] = mapped_column(String(20))
    codpro: Mapped[Optional[str]] = mapped_column(String(20))
    eanven: Mapped[Optional[str]] = mapped_column(String(20))
    eanlug: Mapped[Optional[str]] = mapped_column(String(20))
    reference: Mapped[Optional[str]] = mapped_column(String(30))

    def __init__(
            self,
            posting_date: date,
            initial_reporting_date: date,
            ending_reporting_date: date,
            **kw):
        super().__init__(
            posting_date_key=date2key(posting_date),
            initial_reporting_date_key=date2key(initial_reporting_date),
            ending_reporting_date_key=date2key(ending_reporting_date),
            **kw)

    @hybrid_property
    def posting_date(self) -> date:
        return key2date(self.posting_date_key)

    @posting_date.setter
    def posting_date(self, value: date):
        self.posting_date_key = date2key(value)

    @hybrid_property
    def initial_reporting_date(self) -> date:
        return key2date(self.initial_reporting_date_key)

    @initial_reporting_date.setter
    def initial_reporting_date(self, value: date):
        self.initial_reporting_date_key = date2key(value)

    @hybrid_property
    def ending_reporting_date(self) -> date:
        return key2date(self.ending_reporting_date_key)

    @ending_reporting_date.setter
    def ending_reporting_date(self, value: date):
        self.ending_reporting_date_key = date2key(value)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'partner_no_={self.partner.no_!r}, item_no_={self.item_no_!r})')


class FactItemCustomerInventoryErrors(Base):
    __tablename__ = 'fact_item_customer_inventory_errors'

    key: Mapped[int] = mapped_column(primary_key=True)
    partner_no_: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey('dim_edi_partner.no_'))
    partner: Mapped['DimEDIPartner'] = relationship()
    global_location_no_: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey('dim_edi_partner_line.global_location_no_'))
    partner_line: Mapped['DimEDIPartnerLine'] = relationship(
        primaryjoin=(
            'and_(FactItemCustomerInventoryErrors.partner_no_'
            '==DimEDIPartnerLine.no_, '
            'FactItemCustomerInventoryErrors.global_location_no_'
            '==DimEDIPartnerLine.global_location_no_)'))
    posting_date_key: Mapped[Optional[int]] = mapped_column()
    item_no_: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey('dim_item.no_'))
    item: Mapped['DimItem'] = relationship()
    quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    inventory_date_key: Mapped[Optional[int]] = mapped_column()
    posting_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True))
    eanart: Mapped[Optional[str]] = mapped_column(String(20))
    codcom: Mapped[Optional[str]] = mapped_column(String(20))
    codpro: Mapped[Optional[str]] = mapped_column(String(20))
    eanven: Mapped[Optional[str]] = mapped_column(String(20))
    eanlug: Mapped[Optional[str]] = mapped_column(String(20))
    reference: Mapped[Optional[str]] = mapped_column(String(50))

    @hybrid_property
    def posting_date(self) -> date:
        return key2date(self.posting_date_key)

    @posting_date.setter
    def posting_date(self, value: date):
        self.posting_date_key = date2key(value)

    @hybrid_property
    def inventory_date(self) -> date:
        return key2date(self.inventory_date_key)

    @inventory_date.setter
    def inventory_date(self, value: date):
        self.inventory_date_key = date2key(value)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'partner_no_={self.partner_no_!r}, '
            f'item_no_={self.item_no_!r})')


class FactItemCustomerInventory(Base):
    __tablename__ = 'fact_item_customer_inventory'

    key: Mapped[int] = mapped_column(primary_key=True)
    edi_partner_key: Mapped[int] = mapped_column(
        ForeignKey('dim_edi_partner.key'))
    edi_partner: Mapped['DimEDIPartner'] = relationship(
        backref='fact_item_customer_inventory')
    edi_partner_line_key: Mapped[int] = mapped_column(
        ForeignKey('dim_edi_partner_line.key'))
    edi_partner_line: Mapped['DimEDIPartnerLine'] = relationship(
        backref='fact_item_customer_inventory')
    item_key: Mapped[int] = mapped_column(ForeignKey('dim_item.key'))
    item: Mapped['DimItem'] = relationship(
        backref='fact_item_customer_inventory')
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    posting_date_key: Mapped[int] = mapped_column()
    inventory_date_key: Mapped[int] = mapped_column()
    document_no_: Mapped[Optional[str]] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal(0))
    purchasegroup_key: Mapped[Optional[int]] = mapped_column(
        ForeignKey('dim_purchase_group.key'))
    purchasegroup: Mapped['DimPurchaseGroup'] = relationship(
        backref='fact_item_customer_inventory')

    def __init__(
            self, posting_date: date, inventory_date: date, **kw):
        super().__init__(
            posting_date_key=date2key(posting_date),
            inventory_date_key=date2key(inventory_date),
            **kw)

    @hybrid_property
    def posting_date(self) -> date:
        return key2date(self.posting_date_key)

    @posting_date.expression
    def posting_date(cls) -> date:
        return key2date(cls.posting_date_key)

    @posting_date.setter
    def posting_date(self, value: date):
        self.posting_date_key = date2key(value)

    @hybrid_property
    def inventory_date(self) -> date:
        return key2date(self.inventory_date_key)

    @inventory_date.expression
    def inventory_date(cls) -> date:
        return key2date(cls.inventory_date_key)

    @inventory_date.setter
    def inventory_date(self, value: date):
        self.inventory_date_key = date2key(value)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'edi_partner_no_={self.edi_partner.no_!r}, '
            f'item_no_={self.item.no_!r})')


class FactInitialCustomerInventory(Base):
    __tablename__ = 'fact_initial_customer_inventory'

    key: Mapped[int] = mapped_column(primary_key=True)
    entry_no_: Mapped[Optional[int]] = mapped_column()
    edi_partner_key: Mapped[int] = mapped_column(
        ForeignKey('dim_edi_partner.key'))
    edi_partner: Mapped['DimEDIPartner'] = relationship(
        backref='fact_initial_customer_inventory')
    posting_date_key: Mapped[int] = mapped_column()
    item_key: Mapped[int] = mapped_column(ForeignKey('dim_item.key'))
    item: Mapped['DimItem'] = relationship(
        backref='fact_initial_customer_inventory')
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    document_no_: Mapped[Optional[str]] = mapped_column(String(50))
    inventory_date_key: Mapped[int] = mapped_column()

    def __init__(
            self, posting_date: date, inventory_date: date, **kw):
        super().__init__(
            posting_date_key=date2key(posting_date),
            inventory_date_key=date2key(inventory_date),
            **kw)

    @hybrid_property
    def posting_date(self) -> date:
        return key2date(self.posting_date_key)

    @posting_date.setter
    def posting_date(self, value: date):
        self.posting_date_key = date2key(value)

    @hybrid_property
    def inventory_date(self) -> date:
        return key2date(self.inventory_date_key)

    @inventory_date.setter
    def inventory_date(self, value: date):
        self.inventory_date_key = date2key(value)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'edi_partner_no_={self.edi_partner.no_!r}, '
            f'item_no_={self.item.no_!r})')


class FactItemSales(Base):
    __tablename__ = 'fact_item_sales'

    key: Mapped[int] = mapped_column(primary_key=True)
    entry_no_: Mapped[int] = mapped_column()
    posting_date_key: Mapped[int] = mapped_column()
    document_no_: Mapped[str | None] = mapped_column(String(20))
    document_line_no_: Mapped[int] = mapped_column()
    department: Mapped[str | None] = mapped_column(String(20))
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    invoiced_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    inv_qty_at_0: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    inv_qty_at_gross_amt_0: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    sales_amount_actual: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    pmt_disc_given_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    allocated_disc_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    sales_amount_expected: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    sales_amount_gross: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    cost_amount_actual: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    sell_to_customer_key: Mapped[int] = mapped_column()
    bill_to_customer_key: Mapped[int] = mapped_column()
    item_key: Mapped[int] = mapped_column()
    salesperson_key: Mapped[int] = mapped_column()
    reason_key: Mapped[int] = mapped_column()
    ship_to_county_key: Mapped[int] = mapped_column()
    ship_to_country_key: Mapped[int] = mapped_column()
    document_type_key: Mapped[int] = mapped_column()
    product_posting_group_key: Mapped[int] = mapped_column()
    business_posting_group_key: Mapped[int] = mapped_column()
    return_reason_key: Mapped[int] = mapped_column()
    campaign_key: Mapped[int] = mapped_column()
    purchasegroup_key: Mapped[int] = mapped_column()
    lifecycle_key: Mapped[int] = mapped_column()
    item_ledger_entry_no_: Mapped[int] = mapped_column()
    order_type_key: Mapped[int] = mapped_column()
    campaign_year_key: Mapped[int] = mapped_column()
    catalog_key: Mapped[int] = mapped_column()

    def __init__(
            self, posting_date: date, **kw):
        super().__init__(
            posting_date_key=date2key(posting_date),
            **kw)

    @hybrid_property
    def posting_date(self) -> date:
        return key2date(self.posting_date_key)

    @posting_date.setter
    def posting_date(self, value: date):
        self.posting_date_key = date2key(value)


class FactItemSalesOrders(Base):
    __tablename__ = 'fact_item_sales_orders'

    key: Mapped[int] = mapped_column(primary_key=True)
    order_date_key: Mapped[int] = mapped_column()
    first_order: Mapped[bool] = mapped_column()
    to_date_key: Mapped[int] = mapped_column()
    date_archived_key: Mapped[int] = mapped_column()
    requested_delivery_date_key: Mapped[int] = mapped_column()
    order_class_key: Mapped[int] = mapped_column()
    document_no_: Mapped[Optional[str]] = mapped_column(String(20))
    document_line_no_: Mapped[int] = mapped_column()
    version_no_: Mapped[int] = mapped_column()
    doc_no_occurrence: Mapped[int] = mapped_column()
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    qty_at_0: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    qty_at_gross_amt_0: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    sales_amount_actual: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    pmt_disc_given_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    sales_amount_gross: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    sell_to_customer_key: Mapped[int] = mapped_column()
    bill_to_customer_key: Mapped[int] = mapped_column()
    item_key: Mapped[int] = mapped_column()
    salesperson_key: Mapped[int] = mapped_column()
    reason_key: Mapped[int] = mapped_column()
    ship_to_county_key: Mapped[int] = mapped_column()
    ship_to_country_key: Mapped[int] = mapped_column()
    product_posting_group_key: Mapped[int] = mapped_column()
    business_posting_group_key: Mapped[int] = mapped_column()
    return_reason_key: Mapped[int] = mapped_column()
    campaign_key: Mapped[int] = mapped_column()
    purchasegroup_key: Mapped[int] = mapped_column()
    lifecycle_key: Mapped[int] = mapped_column()
    department: Mapped[Optional[str]] = mapped_column(String(20))
    allocated_disc_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal(0))
    order_type_key: Mapped[int] = mapped_column()
    campaign_year_key: Mapped[int] = mapped_column()
    catalog_key: Mapped[int] = mapped_column()

    def __init__(
            self,
            order_date: date,
            to_date: date,
            date_archived: date,
            requested_delivery_date: date,
            **kw):
        super().__init__(
            order_date_key=date2key(order_date),
            to_date_key=date2key(to_date),
            date_archived_key=date2key(date_archived),
            requested_delivery_date_key=date2key(requested_delivery_date),
            **kw)

    @hybrid_property
    def order_date(self) -> date:
        return key2date(self.order_date_key)

    @order_date.setter
    def order_date(self, value: date):
        self.order_date_key = date2key(value)

    @hybrid_property
    def to_date(self) -> date:
        return key2date(self.to_date_key)

    @to_date.setter
    def to_date(self, value: date):
        self.to_date_key = date2key(value)

    @hybrid_property
    def date_archived(self) -> date:
        return key2date(self.date_archived_key)

    @date_archived.setter
    def date_archived(self, value: date):
        self.date_archived_key = date2key(value)

    @hybrid_property
    def requested_delivery_date(self) -> date:
        return key2date(self.requested_delivery_date_key)

    @requested_delivery_date.setter
    def requested_delivery_date(self, value: date):
        self.requested_delivery_date_key = date2key(value)


BINDS = {
    DimAccountManager: ENGINE,
    DimArea: ENGINE,
    DimCampaign: ENGINE,
    DimCampaignYear: ENGINE,
    DimCatalog: ENGINE,
    DimCommercialArea: ENGINE,
    DimCountryRegion: ENGINE,
    DimCustomer: ENGINE,
    DimCustomerCategory: ENGINE,
    DimCustomerChannel: ENGINE,
    DimDivision: ENGINE,
    DimEDIPartner: ENGINE,
    DimEDIPartnerLine: ENGINE,
    DimItem: ENGINE,
    DimItemLine: ENGINE,
    DimLifeCycle: ENGINE,
    DimNPD: ENGINE,
    DimProductManager: ENGINE,
    DimPurchaseGroup: ENGINE,
    DimSalespersonPurchaser: ENGINE,
    DimVendor: ENGINE,
    FactAgreements: ENGINE,
    FactInitialCustomerInventory: ENGINE,
    FactItemCustomerInventory: ENGINE,
    FactItemCustomerInventoryErrors: ENGINE,
    FactItemCustomerSales: ENGINE,
    FactItemCustomerSalesErrors: ENGINE,
    FactItemSales: ENGINE,
    FactItemSalesOrders: ENGINE,
}
