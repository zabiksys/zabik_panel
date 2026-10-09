from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict

from .title import Title


class Item(BaseModel):
    model_config = ConfigDict(extra='allow')

    no_: Annotated[str, Title(en='No.', es='Nº')]
    description: Annotated[str | None, Field(default=None), Title(
        en='Description', es='Descripción')]
    description_2: Annotated[str | None, Field(default=None), Title(
        en='Description 2', es='Descripción 2')]
    item_line_code: Annotated[str | None, Field(default=None), Title(
        en='Item Line Code', es='Cód. línea prod.')]
    item_line_name: Annotated[str | None, Field(default=None), Title(
        en='Item Line Name', es='Nombre línea prod.')]
    npd_code: Annotated[str | None, Field(default=None), Title(
        en='NPD Code', es='Cód. NPD')]
    npd_name: Annotated[str | None, Field(default=None), Title(
        en='NPD Name', es='Nombre NPD')]
    division_code: Annotated[str | None, Field(default=None), Title(
        en='Division Code', es='Cód. división')]
    division_name: Annotated[str | None, Field(default=None), Title(
        en='Division Name', es='Nombre división')]
    life_cycle_code: Annotated[str | None, Field(default=None), Title(
        en='Life Cycle Code', es='Cód. ciclo vida')]
    life_cycle_name: Annotated[str | None, Field(default=None), Title(
        en='Life Cycle Name', es='Nombre ciclo vida')]
    campaign_code: Annotated[str | None, Field(default=None), Title(
        en='Campaign Code', es='Cód. campaña')]
    campaign_name: Annotated[str | None, Field(default=None), Title(
        en='Campaign Name', es='Nombre campaña')]
    state: Annotated[str | None, Field(default=None), Title(
        en='State', es='Estado')]
    blocked: Annotated[bool | None, Field(default=None), Title(
        en='Blocked', es='Bloqueado')]
    report_order: Annotated[int | None, Field(default=None), Title(
        en='Report Order', es='Orden de informe')]
    blocked___quot__ord__sales_: Annotated[bool | None, Field(default=None), Title(
        en='Blocked - Quot./Ord. (Sales)', es='Bloq. - of./ped. (venta)')]
    ean_no_: Annotated[str | None, Field(default=None), Title(
        en='EAN No.', es='Nº EAN')]
    dun14_no_: Annotated[str | None, Field(default=None), Title(
        en='DUN14 No.', es='Nº DUN14')]
    vendor_item_no_: Annotated[str | None, Field(default=None), Title(
        en='Vendor Item No.', es='Nº producto proveedor')]
    vendor_item_description: Annotated[str | None, Field(default=None), Title(
        en='Vendor Item Description', es='Producto descripción proveedor')]
    sales_order_multiple: Annotated[float | None, Field(default=None), Title(
        en='Sales Order Multiple', es='Múltiplo pedido venta')]
    unit_volume: Annotated[float | None, Field(default=None), Title(
        en='Unit Volume', es='Volumen')]
    royalty__: Annotated[float | None, Field(default=None), Title(
        en='Royalty %', es='% royalty')]
    vendor_no_: Annotated[str | None, Field(default=None), Title(
        en='Vendor No.', es='Nº proveedor')]
    price_a: Annotated[float | None, Field(default=None), Title(
        en='Price A', es='Precio A')]
    price_b: Annotated[float | None, Field(default=None), Title(
        en='Price B', es='Precio B')]
    price_i: Annotated[float | None, Field(default=None), Title(
        en='Price I', es='Precio I')]
    price_p: Annotated[float | None, Field(default=None), Title(
        en='Price P', es='Precio P')]
    price_ddp: Annotated[float | None, Field(default=None), Title(
        en='Price DDP', es='Precio DDP')]
    price_r: Annotated[float | None, Field(default=None), Title(
        en='Price R', es='Precio R')]
    tariff_no_: Annotated[str | None, Field(default=None), Title(
        en='Tariff No.', es='Cód. arancelario')]
    std_quantity: Annotated[float | None, Field(default=None), Title(
        en='STD Quantity', es='STD Cantidad')]
    std_height: Annotated[float | None, Field(default=None), Title(
        en='STD Height', es='STD Alto')]
    std_width: Annotated[float | None, Field(default=None), Title(
        en='STD Width', es='STD Ancho')]
    std_length: Annotated[float | None, Field(default=None), Title(
        en='STD Length', es='STD Largo')]
    std_cubage: Annotated[float | None, Field(default=None), Title(
        en='STD Cubage', es='STD Cubicaje')]
    std_weight: Annotated[float | None, Field(default=None), Title(
        en='STD Weight', es='STD Peso')]
    std_state: Annotated[str | None, Field(default=None), Title(
        en='STD State', es='STD Estado')]
    uds_height: Annotated[float | None, Field(default=None), Title(
        en='UDS Height', es='UDS Alto')]
    uds_width: Annotated[float | None, Field(default=None), Title(
        en='UDS Width', es='UDS Ancho')]
    uds_length: Annotated[float | None, Field(default=None), Title(
        en='UDS Length', es='UDS Largo')]
    uds_cubage: Annotated[float | None, Field(default=None), Title(
        en='UDS Cubage', es='UDS Cubicaje')]
    uds_weight: Annotated[float | None, Field(default=None), Title(
        en='UDS Weight', es='UDS Peso')]
    uds_state: Annotated[str | None, Field(default=None), Title(
        en='UDS State', es='UDS Estado')]
    product_height: Annotated[float | None, Field(default=None), Title(
        en='PRODUCTO Height', es='PRODUCTO Alto')]
    product_width: Annotated[float | None, Field(default=None), Title(
        en='PRODUCTO Width', es='PRODUCTO Ancho')]
    product_length: Annotated[float | None, Field(default=None), Title(
        en='PRODUCTO Length', es='PRODUCTO Largo')]
    product_weight: Annotated[float | None, Field(default=None), Title(
        en='PRODUCTO Weight', es='PRODUCTO Peso')]
    product_state: Annotated[str | None, Field(default=None), Title(
        en='PRODUCTO State', es='PRODUCTO Estado')]
    pallet_quantity: Annotated[float | None, Field(default=None), Title(
        en='PALET Quantity', es='PALET Cantidad')]
    pallet_height: Annotated[float | None, Field(default=None), Title(
        en='PALET Height', es='PALET Alto')]
    pallet_cubage: Annotated[float | None, Field(default=None), Title(
        en='PALET Cubage', es='PALET Cubicaje')]
    pallet_weight: Annotated[float | None, Field(default=None), Title(
        en='PALET Weight', es='PALET Peso')]
    pallet_layers: Annotated[float | None, Field(default=None), Title(
        en='PALET Layers', es='PALET Capas')]
    pallet_qty__per_layer: Annotated[float | None, Field(default=None), Title(
        en='PALET Qty. per Layer', es='PALET Cdad. por capa')]
    pallet_state: Annotated[str | None, Field(default=None), Title(
        en='PALET State', es='PALET Estado')]
    cont20_quantity: Annotated[float | None, Field(default=None), Title(
        en='CONT20 Quantity', es='CONT20 Cantidad')]
    cont40_quantity: Annotated[float | None, Field(default=None), Title(
        en='CONT40 Quantity', es='CONT40 Cantidad')]
    cont40h_quantity: Annotated[float | None, Field(default=None), Title(
        en='CONT40H Quantity', es='CONT40H Cantidad')]
    features: Annotated[dict | None, Field(default=None), Title(
        en='Features', es='Características')]
    extended_text_1: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 1', es='Texto ext. 1')]
    extended_text_2: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 2', es='Texto ext. 2')]
    extended_text_3: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 3', es='Texto ext. 3')]
    extended_text_4: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 4', es='Texto ext. 4')]
    extended_text_5: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 5', es='Texto ext. 5')]
    extended_text_6: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 6', es='Texto ext. 6')]
    extended_text_7: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 7', es='Texto ext. 7')]
    extended_text_8: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 8', es='Texto ext. 8')]
    extended_text_9: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 9', es='Texto ext. 9')]
    extended_text_10: Annotated[str | None, Field(default=None), Title(
        en='Ext. Text 10', es='Texto ext. 10')]