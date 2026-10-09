"""dwh_mssql."""
from application.config.config import Config
from datetime import date, datetime, time
from decimal import Decimal
import pyodbc
from application.config.urls import mssql_url
from sqlalchemy import create_engine
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func
from typing import Optional, Union


pyodbc.pooling = False


class Base(DeclarativeBase):
    pass


APPLICATION_NAME = 'Panel - tables'
DWH_MSSQL_SECRETS = Config()['datawarehouse_mssql']
DWH_MSSQL_URL = mssql_url(DWH_MSSQL_SECRETS, APPLICATION_NAME)
# https://techcommunity.microsoft.com/t5/azure-database-support-blog/lesson-learned-359-tcp-provider-error-code-0x68-104/ba-p/3834127
ENGINE = create_engine(
    DWH_MSSQL_URL,
    connect_args={'check_same_thread': False},
    pool_recycle=1500,
    echo=False)


class _DimNavDimension(Base):
    __tablename__ = 'DimNavDimension'

    key: Mapped[int] = mapped_column('DimKey', primary_key=True)
    dimcode: Mapped[str] = mapped_column('DimCode', String(20))
    code: Mapped[str] = mapped_column('Code', String(20))
    name: Mapped[Optional[str]] = mapped_column('Name', String(50))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'code={self.code!r})')


class DimAccountManager(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'RESP-COMERCIAL',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimArea(Base):
    __tablename__ = 'Dim_ Area'

    key: Mapped[int] = mapped_column('AreaKey', primary_key=True)
    code: Mapped[str] = mapped_column('Code', String(10))
    text: Mapped[Optional[str]] = mapped_column('Text', String(50))
    post_code_prefix: Mapped[Optional[str]] = mapped_column(
        'Post Code Prefix', String(20))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'code={self.code!r})')


class DimCampaign(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'CAMPAÑA',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimCampaignYear(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'AÑO-CAMPAÑA',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimCatalog(Base):
    __tablename__ = 'Dim_ Catalog'

    key: Mapped[int] = mapped_column('CatalogKey', primary_key=True)
    code: Mapped[str] = mapped_column('Code', String(10))


class DimCommercialArea(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'AREA-COMERCIAL',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimCountryRegion(Base):
    __tablename__ = 'Dim_ Country_Region'

    countrykey: Mapped[int] = mapped_column('CountryKey', primary_key=True)
    code: Mapped[str] = mapped_column('Code', String(10))
    name: Mapped[Optional[str]] = mapped_column('Name', String(50))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(countrykey={self.countrykey!r}, '
            f'code={self.code!r})')


class DimCustomer(Base):
    __tablename__ = 'Dim_ Customer'

    customerkey: Mapped[int] = mapped_column('CustomerKey', primary_key=True)
    no_: Mapped[str] = mapped_column('No_', String(20))
    name: Mapped[Optional[str]] = mapped_column('Name', String(50))
    salesperson_key: Mapped[Optional[int]] = mapped_column(
        'SalespersonKey', ForeignKey('Dim_ Salesperson_Purchaser.Salesperson_PurchaserKey'))
    salesperson: Mapped[list['DimSalespersonPurchaser']] = relationship(
        backref='customers')
    purchasegroup_key: Mapped[Optional[int]] = mapped_column(
        'PurchaseGroupKey', ForeignKey('DimNavDimension.DimKey'))
    purchasegroup: Mapped['DimPurchaseGroup'] = relationship(
        foreign_keys=[purchasegroup_key], backref='customers')
    channel_key: Mapped[Optional[int]] = mapped_column(
        'ChannelKey', ForeignKey('DimNavDimension.DimKey'))
    channel: Mapped['DimCustomerChannel'] = relationship(
        foreign_keys=[channel_key], backref='customers')
    city: Mapped[Optional[str]] = mapped_column('City', String(30))
    county_key: Mapped[Optional[int]] = mapped_column(
        'CountyKey', ForeignKey('Dim_ Area.AreaKey'))
    county: Mapped['DimArea'] = relationship(backref='customers')
    country_key: Mapped[Optional[int]] = mapped_column(
        'CountryKey', ForeignKey('Dim_ Country_Region.CountryKey'))
    country: Mapped['DimCountryRegion'] = relationship(backref='customers')
    commercial_area_key: Mapped[int] = mapped_column(
        'CommercialAreaKey', ForeignKey('DimNavDimension.DimKey'))
    commercial_area: Mapped['DimCommercialArea'] = relationship(
        foreign_keys=[commercial_area_key], backref='customers')
    accountmanager_key: Mapped[int] = mapped_column(
        'AccountManagerKey', ForeignKey('DimNavDimension.DimKey'))
    accountmanager: Mapped['DimAccountManager'] = relationship(
        foreign_keys=[accountmanager_key], backref='customers')
    customercategory_key: Mapped[int] = mapped_column(
        'CustomerCategoryKey', ForeignKey('DimNavDimension.DimKey'))
    customercategory: Mapped['DimCustomerCategory'] = relationship(
        foreign_keys=[customercategory_key], backref='customers')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'no_={self.no_!r}, name={self.name!r})')


class DimCustomerCategory(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'CAT-CLIENTE',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimCustomerChannel(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'CANAL-CLIENTE',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimDivision(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'DIVISION',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimEDIPartner(Base):
    __tablename__ = 'Dim_ EDI Partner'

    edipartnerkey: Mapped[int] = mapped_column(
        'EDIPartnerKey', primary_key=True)
    no_: Mapped[str] = mapped_column('No_', String(20))
    name: Mapped[Optional[str]] = mapped_column('Name', String(50))
    purchasegroup_key: Mapped[int] = mapped_column(
        'PurchaseGroupKey', ForeignKey('DimNavDimension.DimKey'))
    purchasegroup: Mapped['DimPurchaseGroup'] = relationship(
        foreign_keys=[purchasegroup_key], backref='edi_partners')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(edipartnerkey={self.edipartnerkey!r}, '
            f'no_={self.no_!r}, name={self.name!r})')


class DimEDIPartnerLine(Base):
    __tablename__ = 'Dim_ EDI Partner Line'

    edipartnerlinekey: Mapped[int] = mapped_column(
        'EDIPartnerLineKey', primary_key=True)
    no_: Mapped[str] = mapped_column('No_', String(20))
    global_location_no_: Mapped[str] = mapped_column(
        'Global Location No_', String(20))
    edipartnerkey: Mapped[int] = mapped_column(
        'EDIPartnerKey', ForeignKey('Dim_ EDI Partner.EDIPartnerKey'))
    edipartner: Mapped['DimEDIPartner'] = relationship(
        backref='edi_partner_lines')
    name: Mapped[Optional[str]] = mapped_column('Name', String(50))
    name_2: Mapped[Optional[str]] = mapped_column('Name 2', String(50))
    salespersonkey: Mapped[int] = mapped_column(
        'SalespersonKey',
        ForeignKey('Dim_ Salesperson_Purchaser.Salesperson_PurchaserKey'))
    salesperson: Mapped['DimSalespersonPurchaser'] = relationship()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}'
            f'(edipartnerlinekey={self.edipartnerlinekey!r}, '
            f'no_={self.no_!r}, '
            f'global_localtion_no_={self.global_location_no_!r})')


class DimItem(Base):
    __tablename__ = 'Dim_ Item'

    key: Mapped[int] = mapped_column('ItemKey', primary_key=True)
    no_: Mapped[str] = mapped_column('No_', String(20))
    description: Mapped[Optional[str]] = mapped_column(
        'Description', String(50))
    divisionkey: Mapped[int] = mapped_column(
        'DivisionKey', ForeignKey('DimNavDimension.DimKey'))
    division: Mapped['DimDivision'] = relationship(
        foreign_keys=[divisionkey], backref='items')
    itemlinekey: Mapped[int] = mapped_column(
        'ItemLineKey', ForeignKey('DimNavDimension.DimKey'))
    itemline: Mapped['DimItemLine'] = relationship(
        foreign_keys=[itemlinekey], backref='items')
    npdkey: Mapped[int] = mapped_column(
        'NPDKey', ForeignKey('DimNavDimension.DimKey'))
    npd: Mapped['DimNPD'] = relationship(
        foreign_keys=[npdkey], backref='items')
    vendorkey: Mapped[int] = mapped_column(
        'VendorKey', ForeignKey('Dim_ Vendor.VendorKey'))
    vendor: Mapped['DimVendor'] = relationship(backref='items')
    report_order: Mapped[Optional[int]] = mapped_column('Report Order')
    state: Mapped[Optional[str]] = mapped_column('State', String(20))
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        'Unit Price', Numeric(38, 20))
    lifecyclekey: Mapped[int] = mapped_column(
        'LifeCycleKey', ForeignKey('DimNavDimension.DimKey'))
    lifecycle: Mapped['DimItemLifeCycle'] = relationship(
        foreign_keys=[lifecyclekey], backref='items')
    unit_volume: Mapped[Optional[Decimal]] = mapped_column(
        'Unit Volume', Numeric(38, 20))
    gross_weight: Mapped[Optional[Decimal]] = mapped_column(
        'Gross Weight', Numeric(38, 20))
    report_order_2: Mapped[Optional[int]] = mapped_column('Report Order 2')
    productmanagerkey: Mapped[int] = mapped_column(
        'ProductManagerKey', ForeignKey('DimNavDimension.DimKey'))
    productmanager: Mapped['DimProductManager'] = relationship(
        foreign_keys=[productmanagerkey], backref='items')
    report_order_3: Mapped[Optional[int]] = mapped_column('Report Order 3')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
            f'no_={self.no_!r}, description={self.description!r})')


class DimItemLifeCycle(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'CICLO-VIDA',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimItemLine(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'LINEA-PROD',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimNPD(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'NPD',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimProductManager(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'JEFE-PRODUCTO',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimSalespersonPurchaser(Base):
    __tablename__ = 'Dim_ Salesperson_Purchaser'

    salesperson_purchaserkey: Mapped[int] = mapped_column(
        'Salesperson_PurchaserKey', primary_key=True)
    code: Mapped[str] = mapped_column('Code', String(10))
    name: Mapped[Optional[str]] = mapped_column('Name', String(50))
    state: Mapped[str] = mapped_column('State', String(20))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}'
            f'(salesperson_purchaserkey={self.salesperson_purchaserkey!r}, '
            f'code={self.code!r})')


class DimPurchaseGroup(_DimNavDimension):
    __mapper_args__ = {
        'polymorphic_identity': 'GRUPO-COMPRA',
        'polymorphic_on': _DimNavDimension.dimcode
    }


class DimVendor(Base):
    __tablename__ = 'Dim_ Vendor'

    vendorkey: Mapped[int] = mapped_column('VendorKey', primary_key=True)
    no_: Mapped[str] = mapped_column('No_', String(20))
    name: Mapped[Optional[str]] = mapped_column('Name', String(50))
    countykey: Mapped[int] = mapped_column(
        'CountyKey', ForeignKey('Dim_ Area.AreaKey'))
    countrykey: Mapped[int] = mapped_column(
        'CountryKey', ForeignKey('Dim_ Country_Region.CountryKey'))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(vendorkey={self.vendorkey!r}, '
            f'no_={self.no_!r}, name={self.name!r})')


class FactAgreements(Base):
    __tablename__ = 'Fact Agreements'

    key: Mapped[int] = mapped_column('AgreementKey', primary_key=True, autoincrement=True)
    campaign_year_key: Mapped[int] = mapped_column(
        'CampaignYearDimKey', ForeignKey('DimNavDimension.DimKey'))
    campaign_year: Mapped['DimCampaignYear'] = relationship(
        foreign_keys=[campaign_year_key], backref='fact_agreements')
    campaign_key: Mapped[int] = mapped_column(
        'CampaignDimKey', ForeignKey('DimNavDimension.DimKey'))
    campaign: Mapped['DimCampaign'] = relationship(
        foreign_keys=[campaign_key], backref='fact_agreements')
    purchasegroup_key: Mapped[int] = mapped_column(
        'PurchaseGroupKey', ForeignKey('DimNavDimension.DimKey'))
    purchase_group: Mapped['DimPurchaseGroup'] = relationship(
        foreign_keys=[purchasegroup_key], backref='fact_agreements')
    customer_key: Mapped[int] = mapped_column(
        'CustomerKey', ForeignKey('Dim_ Customer.CustomerKey'))
    customer: Mapped['DimCustomer'] = relationship(
        foreign_keys=[customer_key], backref='fact_agreements')
    item_key: Mapped[int] = mapped_column('ItemKey', ForeignKey('Dim_ Item.ItemKey'))
    item: Mapped['DimItem'] = relationship(
        foreign_keys=[item_key], backref='fact_agreements')
    updated_at: Mapped[datetime] = mapped_column(
        'UpdatedAt',
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


class FactItemCustomerInventory(Base):
    __tablename__ = 'Fact Item Customer Inventory'

    inventorykey: Mapped[int] = mapped_column(
        'InventoryKey', primary_key=True, autoincrement=True)
    edipartnerkey: Mapped[int] = mapped_column(
        'EDIPartnerKey', ForeignKey('Dim_ EDI Partner.EDIPartnerKey'))
    edipartner: Mapped['DimEDIPartner'] = relationship()
    edipartnerlinekey: Mapped[int] = mapped_column(
        'EDIPartnerLineKey',
        ForeignKey('Dim_ EDI Partner Line.EDIPartnerLineKey'))
    edipartnerline: Mapped['DimEDIPartnerLine'] = relationship()
    itemkey: Mapped[int] = mapped_column(
        'ItemKey', ForeignKey('Dim_ Item.ItemKey'))
    item: Mapped['DimItem'] = relationship()
    quantity: Mapped[Decimal] = mapped_column('Quantity', Numeric(38, 20))
    _posting_date: Mapped[datetime] = mapped_column('Posting Date', DateTime)
    _inventory_date: Mapped[datetime] = mapped_column(
        'Inventory Date', DateTime)
    document_no_: Mapped[Optional[str]] = mapped_column(
        'Document No_', String(50))
    amount: Mapped[Optional[Decimal]] = mapped_column(
        'Amount', Numeric(38, 20))
    purchasegroup_key: Mapped[Optional[int]] = mapped_column('PurchaseGroupKey')

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
    def inventory_date(self) -> datetime:
        return self._inventory_date

    @inventory_date.setter
    def inventory_date(self, value: Union[date, datetime]):
        if type(value) is date:
            self._inventory_date = datetime.combine(
                value, time(0, 0), tzinfo=None)
        else:
            self._inventory_date = value

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(inventorykey={self.inventorykey!r}, '
            f'edipartner_no_={self.edipartner.no_!r}, '
            f'item_no_={self.item.no_!r})')


class FactItemCustomerSales(Base):
    __tablename__ = 'Fact Item Customer Sales'

    saleskey: Mapped[int] = mapped_column(
        'SalesKey', primary_key=True, autoincrement=True)
    entry_no_: Mapped[int] = mapped_column('Entry No_')
    edipartnerkey: Mapped[int] = mapped_column(
        'EDIPartnerKey', ForeignKey('Dim_ EDI Partner.EDIPartnerKey'))
    edipartner: Mapped['DimEDIPartner'] = relationship()
    edipartnerlinekey: Mapped[int] = mapped_column(
        'EDIPartnerLineKey', ForeignKey('Dim_ EDI Partner Line.EDIPartnerLineKey'))
    edipartnerline: Mapped['DimEDIPartnerLine'] = relationship()
    itemkey: Mapped[int] = mapped_column(
        'ItemKey', ForeignKey('Dim_ Item.ItemKey'))
    item: Mapped['DimItem'] = relationship()
    lifecyclekey: Mapped[int] = mapped_column(
        'LifeCycleDimKey', ForeignKey('DimNavDimension.DimKey'))
    quantity: Mapped[Decimal] = mapped_column('Quantity', Numeric(38, 20))
    _posting_date: Mapped[datetime] = mapped_column('Posting Date', DateTime)
    _initial_reporting_date: Mapped[datetime] = mapped_column(
        'Initial reporting Date', DateTime)
    _ending_reporting_date: Mapped[datetime] = mapped_column(
        'Ending reporting Date', DateTime)
    campaignkey: Mapped[int] = mapped_column('CampaignDimKey', ForeignKey('DimNavDimension.DimKey'))
    campaign: Mapped['DimCampaign'] = relationship('DimCampaign', foreign_keys=[campaignkey])
    campaignyearkey: Mapped[int] = mapped_column('CampaignYearDimKey', ForeignKey('DimNavDimension.DimKey'))
    campaignyear: Mapped['DimCampaignYear'] = relationship('DimCampaign', foreign_keys=[campaignyearkey])
    amount: Mapped[Optional[Decimal]] = mapped_column('Amount', Numeric(38, 20))
    purchasegroup_key: Mapped[Optional[int]] = mapped_column('PurchaseGroupKey')
    document_no_: Mapped[Optional[str]] = mapped_column(
        'Document No_', String(50))

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
            f'{self.__class__.__name__}(saleskey={self.saleskey!r}, '
            f'edipartner_no_={self.edipartner.no_!r}, '
            f'item_no_={self.item.no_!r})')


class FactItemSales(Base):
    __tablename__ = 'Fact Item Sales'

    key: Mapped[int] = mapped_column('SalesKey', primary_key=True)
    entry_no_: Mapped[int] = mapped_column('Entry No_')
    _posting_date: Mapped[datetime] = mapped_column('Posting Date', DateTime)
    document_no_: Mapped[str | None] = mapped_column('Document No_', String(20))
    document_line_no_: Mapped[int] = mapped_column('Document Line No_')
    department: Mapped[str | None] = mapped_column('Department', String(20))
    quantity: Mapped[Decimal] = mapped_column(
        'Quantity', Numeric(18, 6), default=Decimal(0))
    invoiced_quantity: Mapped[Decimal] = mapped_column(
        'Invoiced Quantity', Numeric(18, 6), default=Decimal(0))
    inv_qty_at_0: Mapped[Decimal] = mapped_column(
        'Inv_ Qty_ at 0', Numeric(18, 6), default=Decimal(0))
    inv_qty_at_gross_amt_0: Mapped[Decimal] = mapped_column(
        'Inv_ Qty_ at Gross Amt 0', Numeric(18, 6), default=Decimal(0))
    sales_amount_actual: Mapped[Decimal] = mapped_column(
        'Sales Amount (Actual)', Numeric(18, 6), default=Decimal(0))
    discount_amount: Mapped[Decimal] = mapped_column(
        'Discount Amount', Numeric(18, 6), default=Decimal(0))
    pmt_disc_given_amount: Mapped[Decimal] = mapped_column(
        'Pmt_ Disc_ Given Amount', Numeric(18, 6), default=Decimal(0))
    allocated_disc_amount: Mapped[Decimal] = mapped_column(
        'Allocated Disc_ Amount', Numeric(18, 6), default=Decimal(0))
    sales_amount_expected: Mapped[Decimal] = mapped_column(
        'Sales Amount (Expected)', Numeric(18, 6), default=Decimal(0))
    sales_amount_gross: Mapped[Decimal] = mapped_column(
        'Sales Amount (Gross)', Numeric(18, 6), default=Decimal(0))
    cost_amount_actual: Mapped[Decimal] = mapped_column(
        'Cost Amount (Actual)', Numeric(18, 6), default=Decimal(0))
    sell_to_customer_key: Mapped[int] = mapped_column('SellToCustomerKey')
    bill_to_customer_key: Mapped[int] = mapped_column('BillToCustomerKey')
    item_key: Mapped[int] = mapped_column('ItemKey')
    salesperson_key: Mapped[int] = mapped_column('SalespersonKey')
    reason_key: Mapped[int] = mapped_column('ReasonKey')
    ship_to_county_key: Mapped[int] = mapped_column('ShipToCountyKey')
    ship_to_country_key: Mapped[int] = mapped_column('ShipToCountryKey')
    document_type_key: Mapped[int] = mapped_column('DocumentTypeKey')
    product_posting_group_key: Mapped[int] = mapped_column('ProductPostingGroupKey')
    business_posting_group_key: Mapped[int] = mapped_column('BusinessPostingGroupKey')
    return_reason_key: Mapped[int] = mapped_column('ReturnReasonKey')
    campaign_key: Mapped[int] = mapped_column('CampaignDimKey')
    purchasegroup_key: Mapped[int] = mapped_column('PurchaseGroupKey')
    lifecycle_key: Mapped[int] = mapped_column('LifeCycleDimKey')
    item_ledger_entry_no_: Mapped[int] = mapped_column('Item Ledger Entry No_')
    order_type_key: Mapped[int] = mapped_column('OrderTypeKey')
    campaign_year_key: Mapped[int] = mapped_column('CampaignYearDimKey')
    catalog_key: Mapped[int] = mapped_column('CatalogKey')

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

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(key={self.key!r}, '
        )


class FactItemSalesOrders(Base):
    __tablename__ = 'Fact Item Sales Order'

    key: Mapped[int] = mapped_column('SalesOrderKey', primary_key=True)
    _order_date: Mapped[datetime] = mapped_column('Order Date', DateTime)
    first_order: Mapped[bool] = mapped_column('First Order')
    _to_date: Mapped[datetime] = mapped_column('To Date', DateTime)
    _date_archived: Mapped[datetime] = mapped_column('Date Archived', DateTime)
    _requested_delivery_date: Mapped[datetime] = mapped_column(
        'Requested Delivery Date', DateTime)
    order_class_key: Mapped[int] = mapped_column('OrderClassKey')
    document_no_: Mapped[Optional[str]] = mapped_column('Document No_', String(20))
    document_line_no_: Mapped[int] = mapped_column('Document Line No_')
    version_no_: Mapped[int] = mapped_column('Version No_')
    doc_no_occurrence: Mapped[int] = mapped_column('Doc_ No_ Occurrence')
    quantity: Mapped[Decimal] = mapped_column(
        'Quantity', Numeric(18, 6), default=Decimal(0))
    qty_at_0: Mapped[Decimal] = mapped_column(
        'Qty_ at 0', Numeric(18, 6), default=Decimal(0))
    qty_at_gross_amt_0: Mapped[Decimal] = mapped_column(
        'Qty_ at Gross Amt 0', Numeric(18, 6), default=Decimal(0))
    sales_amount_actual: Mapped[Decimal] = mapped_column(
        'Sales Amount (Actual)', Numeric(18, 6), default=Decimal(0))
    discount_amount: Mapped[Decimal] = mapped_column(
        'Discount Amount', Numeric(18, 6), default=Decimal(0))
    pmt_disc_given_amount: Mapped[Decimal] = mapped_column(
        'Pmt_ Disc_ Given Amount', Numeric(18, 6), default=Decimal(0))
    sales_amount_gross: Mapped[Decimal] = mapped_column(
        'Sales Amount (Gross)', Numeric(18, 6), default=Decimal(0))
    sell_to_customer_key: Mapped[int] = mapped_column('SellToCustomerKey')
    bill_to_customer_key: Mapped[int] = mapped_column('BillToCustomerKey')
    item_key: Mapped[int] = mapped_column('ItemKey')
    salesperson_key: Mapped[int] = mapped_column('SalespersonKey')
    reason_key: Mapped[int] = mapped_column('ReasonKey')
    ship_to_county_key: Mapped[int] = mapped_column('ShipToCountyKey')
    ship_to_country_key: Mapped[int] = mapped_column('ShipToCountryKey')
    product_posting_group_key: Mapped[int] = mapped_column('ProductPostingGroupKey')
    business_posting_group_key: Mapped[int] = mapped_column('BusinessPostingGroupKey')
    return_reason_key: Mapped[int] = mapped_column('ReturnReasonKey')
    campaign_key: Mapped[int] = mapped_column('CampaignDimKey')
    purchasegroup_key: Mapped[int] = mapped_column('PurchaseGroupKey')
    lifecycle_key: Mapped[int] = mapped_column('LifeCycleDimKey')
    department: Mapped[Optional[str]] = mapped_column('Department', String(20))
    allocated_disc_amount: Mapped[Decimal] = mapped_column(
        'Allocated Disc_ Amount', Numeric(18, 6), default=Decimal(0))
    order_type_key: Mapped[int] = mapped_column('OrderTypeKey')
    campaign_year_key: Mapped[int] = mapped_column('CampaignYearDimKey')
    catalog_key: Mapped[int] = mapped_column('CatalogKey')

    @hybrid_property
    def order_date(self) -> datetime:
        return self._order_date

    @order_date.setter
    def order_date(self, value: Union[date, datetime]):
        if type(value) is date:
            self._order_date = datetime.combine(
                value, time(0, 0), tzinfo=None)
        else:
            self._order_date = value

    @hybrid_property
    def to_date(self) -> datetime:
        return self._to_date

    @to_date.setter
    def to_date(self, value: Union[date, datetime]):
        if type(value) is date:
            self._to_date = datetime.combine(
                value, time(0, 0), tzinfo=None)
        else:
            self._to_date = value

    @hybrid_property
    def date_archived(self) -> datetime:
        return self._date_archived

    @date_archived.setter
    def date_archived(self, value: Union[date, datetime]):
        if type(value) is date:
            self._date_archived = datetime.combine(
                value, time(0, 0), tzinfo=None)
        else:
            self._date_archived = value

    @hybrid_property
    def requested_delivery_date(self) -> datetime:
        return self._requested_delivery_date

    @requested_delivery_date.setter
    def requested_delivery_date(self, value: Union[date, datetime]):
        if type(value) is date:
            self._requested_delivery_date = datetime.combine(
                value, time(0, 0), tzinfo=None)
        else:
            self._requested_delivery_date = value


BINDS = {
    DimArea: ENGINE,
    DimCampaign: ENGINE,
    DimCampaignYear: ENGINE,
    DimCatalog: ENGINE,
    DimCountryRegion: ENGINE,
    DimDivision: ENGINE,
    DimEDIPartner: ENGINE,
    DimEDIPartnerLine: ENGINE,
    DimItem: ENGINE,
    DimItemLifeCycle: ENGINE,
    DimItemLine: ENGINE,
    DimNPD: ENGINE,
    DimProductManager: ENGINE,
    DimSalespersonPurchaser: ENGINE,
    DimPurchaseGroup: ENGINE,
    DimVendor: ENGINE,
    FactAgreements: ENGINE,
    FactItemCustomerInventory: ENGINE,
    FactItemCustomerSales: ENGINE,
    FactItemSales: ENGINE,
    FactItemSalesOrders: ENGINE,
}
