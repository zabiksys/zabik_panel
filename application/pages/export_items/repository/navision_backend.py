from collections import OrderedDict
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from typing import Any, Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from application.pages.export_items.models import (
    Item,
    Feature,
    FeatureAnswer,
    FeatureDataType,
    FeatureQuestion,
    CrossRefType,
    uom_state_mapper,
)
from .interfaces import IItemRepository


DIMENSION_CTE_TPL = """{name}(No_, Code, Name) AS
  (SELECT def_dim.[No_], def_dim.[Dimension Value Code] Code, dim.Name
   FROM [{nav_company}$Default Dimension] def_dim INNER JOIN
        [{nav_company}$Dimension Value] dim ON
           dim.[Dimension Code] = def_dim.[Dimension Code]
           AND dim.Code = def_dim.[Dimension Value Code]
    WHERE
      def_dim.[Table ID] = 27
      AND def_dim.[Dimension Code] = '{dim_code}')"""


CROSS_REF_CTE_TPL = """{name}([Item No_], No_, Description) AS
  (SELECT icr.[Item No_], MIN(icr.[Cross-Reference No_]), MAX(icr.Description)
   FROM [{nav_company}$Item Cross Reference] icr
   WHERE icr.[Unit of Measure] = :{name}_unit_of_measure
     AND icr.[Cross-Reference Type] = :{name}_type
     AND icr.[Cross-Reference Type No_] = :{name}_type_no_
     AND icr.[Variant Code] = :{name}_variant_code
     AND icr.[Main Bar Code] = :{name}_main_bar_code
   GROUP BY icr.[Item No_])"""


@dataclass
class DimensionSQL:
    cte: str
    column_list: str
    join: str
    params: dict | None = None


class NavisionRepository(IItemRepository):

    def __init__(self, conn_url: str, nav_company: str):
        self.conn_url = conn_url
        self.nav_company = nav_company
        self.engine = create_engine(self.conn_url, echo=False)

    def get_items(
        self,
        filters: dict,
        fields: list[str],
        feature_profile: str,
    ) -> Iterator[Item]:
        conditions, params = self._build_conditions(filters)
        fields_def = self._get_fields_def(feature_profile)
        column_list, use_ctes, cte_params = self._build_columns_and_ctes(fields, fields_def, params, filters)
        where = ' AND '.join(conditions) if conditions else '1=1'
        sql = self._build_sql(use_ctes, column_list, where)
        params.update(cte_params)
        with Session(self.engine) as session:
            result = session.execute(sql, params)
            for row in result:
                item_data = self._row_to_item(row, fields, fields_def, session, feature_profile)
                if item_data:
                    yield Item(**item_data)

    def _build_conditions(self, filters: dict) -> tuple[list[str], dict[str, Any]]:
        conditions = []
        params = {}
        if filters.get('state') and filters['state'] != 'Todos':
            conditions.append("item.State = :state")
            params['state'] = filters['state']
        if filters.get('item_line'):
            conditions.append("item_line.Code = :line")
            params['line'] = filters['item_line']
        if filters.get('search'):
            search = f"%{filters['search'].strip()}%"
            conditions.append("(item.No_ LIKE :search OR item.Description LIKE :search)")
            params['search'] = search
        return conditions, params

    def _get_fields_def(self, feature_profile: str) -> dict:
        return {
            'no_': (['item.No_ no_'], lambda row: {'no_': row.no_}),
            'description': (['item.Description description'], lambda row: {'description': row.description}),
            'description_2': (['item.[Description 2] description_2'], lambda row: {'description_2': row.description_2}),
            'state': (['item.State state'], lambda row: {'state': row.state}),
            'blocked': (['item.Blocked blocked'], lambda row: {'blocked': bool(row.blocked)}),
            'report_order': (['item.[Report Order] report_order'], lambda row: {'report_order': row.report_order}),
            'blocked___quot__ord__sales_': (
                ['item.[Blocked - Quot__Ord_ (Sales)] blocked___quot__ord__sales_'],
                lambda row: {'blocked___quot__ord__sales_': bool(row.blocked___quot__ord__sales_)}
            ),
            'sales_order_multiple': (
                ['item.[Sales Order Multiple] sales_order_multiple'],
                lambda row: {'sales_order_multiple': float(row.sales_order_multiple) if row.sales_order_multiple else None}
            ),
            'unit_volume': (
                ['item.[Unit Volume] unit_volume'],
                lambda row: {'unit_volume': float(row.unit_volume) if row.unit_volume else None}
            ),
            'royalty__': (
                ['item.[Royalty %] royalty__'],
                lambda row: {'royalty__': float(row.royalty__) if row.royalty__ else None}
            ),
            'vendor_no_': (['item.[Vendor No_] vendor_no_'], lambda row: {'vendor_no_': row.vendor_no_}),
            'tariff_no_': (['item.[Tariff No_] tariff_no_'], lambda row: {'tariff_no_': row.tariff_no_}),
            'ean_no_': (['ean.No_ ean_code'], lambda row: {'ean_no_': getattr(row, 'ean_code', None)}),
            'dun14_no_': (['dun14.No_ dun14_code'], lambda row: {'dun14_no_': getattr(row, 'dun14_code', None)}),
            'vendor_item_no_': (['vendor_item.No_ vendor_item_no_'], lambda row: {'vendor_item_no_': getattr(row, 'vendor_item_no_', None)}),
            'vendor_item_description': (['vendor_item.Description vendor_item_description'], lambda row: {'vendor_item_description': getattr(row, 'vendor_item_description', None)}),
            'price_a': (['item.No_ no_'], lambda row: self._get_price(row, 'A')),
            'price_b': (['item.No_ no_'], lambda row: self._get_price(row, 'B')),
            'price_i': (['item.No_ no_'], lambda row: self._get_price(row, 'I')),
            'price_p': (['item.No_ no_'], lambda row: self._get_price(row, 'P')),
            'price_ddp': (['item.No_ no_'], lambda row: self._get_price(row, 'DDP')),
            'price_r': (['item.No_ no_'], lambda row: self._get_price(row, 'R')),
            'std_quantity': (['item.No_ no_'], lambda row: self._get_uom(row, 'STD', 'quantity')),
            'std_height': (['item.No_ no_'], lambda row: self._get_uom(row, 'STD', 'height')),
            'std_width': (['item.No_ no_'], lambda row: self._get_uom(row, 'STD', 'width')),
            'std_length': (['item.No_ no_'], lambda row: self._get_uom(row, 'STD', 'length')),
            'std_cubage': (['item.No_ no_'], lambda row: self._get_uom(row, 'STD', 'cubage')),
            'std_weight': (['item.No_ no_'], lambda row: self._get_uom(row, 'STD', 'weight')),
            'std_state': (['item.No_ no_'], lambda row: self._get_uom(row, 'STD', 'state')),
            'uds_height': (['item.No_ no_'], lambda row: self._get_uom(row, 'UDS', 'height')),
            'uds_width': (['item.No_ no_'], lambda row: self._get_uom(row, 'UDS', 'width')),
            'uds_length': (['item.No_ no_'], lambda row: self._get_uom(row, 'UDS', 'length')),
            'uds_cubage': (['item.No_ no_'], lambda row: self._get_uom(row, 'UDS', 'cubage')),
            'uds_weight': (['item.No_ no_'], lambda row: self._get_uom(row, 'UDS', 'weight')),
            'uds_state': (['item.No_ no_'], lambda row: self._get_uom(row, 'UDS', 'state')),
            'product_height': (['item.No_ no_'], lambda row: self._get_uom(row, 'PRODUCTO', 'height')),
            'product_width': (['item.No_ no_'], lambda row: self._get_uom(row, 'PRODUCTO', 'width')),
            'product_length': (['item.No_ no_'], lambda row: self._get_uom(row, 'PRODUCTO', 'length')),
            'product_weight': (['item.No_ no_'], lambda row: self._get_uom(row, 'PRODUCTO', 'weight')),
            'product_state': (['item.No_ no_'], lambda row: self._get_uom(row, 'PRODUCTO', 'state')),
            'pallet_quantity': (['item.No_ no_'], lambda row: self._get_uom(row, 'PALET', 'quantity')),
            'pallet_height': (['item.No_ no_'], lambda row: self._get_uom(row, 'PALET', 'height')),
            'pallet_cubage': (['item.No_ no_'], lambda row: self._get_uom(row, 'PALET', 'cubage')),
            'pallet_weight': (['item.No_ no_'], lambda row: self._get_uom(row, 'PALET', 'weight')),
            'pallet_layers': (['item.No_ no_'], lambda row: self._get_uom(row, 'PALET', 'layers')),
            'pallet_qty__per_layer': (['item.No_ no_'], lambda row: self._get_uom(row, 'PALET', 'qty__per_layer')),
            'pallet_state': (['item.No_ no_'], lambda row: self._get_uom(row, 'PALET', 'state')),
            'cont20_quantity': (['item.No_ no_'], lambda row: self._get_uom(row, 'CONT20', 'quantity')),
            'cont40_quantity': (['item.No_ no_'], lambda row: self._get_uom(row, 'CONT40', 'quantity')),
            'cont40h_quantity': (['item.No_ no_'], lambda row: self._get_uom(row, 'CONT40H', 'quantity')),
            'item_line_code': (['item_line.Code item_line_code'], lambda row: {'item_line_code': getattr(row, 'item_line_code', None)}),
            'item_line_name': (['item_line.Name item_line_name'], lambda row: {'item_line_name': getattr(row, 'item_line_name', None)}),
            'npd_code': (['npd.Code npd_code'], lambda row: {'npd_code': getattr(row, 'npd_code', None)}),
            'npd_name': (['npd.Name npd_name'], lambda row: {'npd_name': getattr(row, 'npd_name', None)}),
            'division_code': (['division.Code division_code'], lambda row: {'division_code': getattr(row, 'division_code', None)}),
            'division_name': (['division.Name division_name'], lambda row: {'division_name': getattr(row, 'division_name', None)}),
            'life_cycle_code': (['life_cycle.Code life_cycle_code'], lambda row: {'life_cycle_code': getattr(row, 'life_cycle_code', None)}),
            'life_cycle_name': (['life_cycle.Name life_cycle_name'], lambda row: {'life_cycle_name': getattr(row, 'life_cycle_name', None)}),
            'campaign_code': (['campaign.Code campaign_code'], lambda row: {'campaign_code': getattr(row, 'campaign_code', None)}),
            'campaign_name': (['campaign.Name campaign_name'], lambda row: {'campaign_name': getattr(row, 'campaign_name', None)}),
            'extended_text_1': (['item.[ExtTextExportField[1]] extended_text_1'], lambda row: {'extended_text_1': row.extended_text_1 if hasattr(row, 'extended_text_1') else None}),
            'extended_text_2': (['item.[ExtTextExportField[2]] extended_text_2'], lambda row: {'extended_text_2': row.extended_text_2 if hasattr(row, 'extended_text_2') else None}),
            'extended_text_3': (['item.[ExtTextExportField[3]] extended_text_3'], lambda row: {'extended_text_3': row.extended_text_3 if hasattr(row, 'extended_text_3') else None}),
            'extended_text_4': (['item.[ExtTextExportField[4]] extended_text_4'], lambda row: {'extended_text_4': row.extended_text_4 if hasattr(row, 'extended_text_4') else None}),
            'extended_text_5': (['item.[ExtTextExportField[5]] extended_text_5'], lambda row: {'extended_text_5': row.extended_text_5 if hasattr(row, 'extended_text_5') else None}),
            'extended_text_6': (['item.[ExtTextExportField[6]] extended_text_6'], lambda row: {'extended_text_6': row.extended_text_6 if hasattr(row, 'extended_text_6') else None}),
            'extended_text_7': (['item.[ExtTextExportField[7]] extended_text_7'], lambda row: {'extended_text_7': row.extended_text_7 if hasattr(row, 'extended_text_7') else None}),
            'extended_text_8': (['item.[ExtTextExportField[8]] extended_text_8'], lambda row: {'extended_text_8': row.extended_text_8 if hasattr(row, 'extended_text_8') else None}),
            'extended_text_9': (['item.[ExtTextExportField[9]] extended_text_9'], lambda row: {'extended_text_9': row.extended_text_9 if hasattr(row, 'extended_text_9') else None}),
            'extended_text_10': (['item.[ExtTextExportField[10]] extended_text_10'], lambda row: {'extended_text_10': row.extended_text_10 if hasattr(row, 'extended_text_10') else None}),
        }

    def _build_columns_and_ctes(self, fields: list[str], fields_def: dict, params: dict, filters: dict | None = None) -> tuple[set, list, dict]:
        column_list = set()
        use_ctes = {}
        cte_params = {}
        uom_fields = {'std_quantity', 'std_height', 'std_width', 'std_length', 'std_cubage', 'std_weight', 'std_state',
                      'uds_height', 'uds_width', 'uds_length', 'uds_cubage', 'uds_weight', 'uds_state',
                      'product_height', 'product_width', 'product_length', 'product_weight', 'product_state',
                      'pallet_quantity', 'pallet_height', 'pallet_cubage', 'pallet_weight', 'pallet_layers', 'pallet_qty__per_layer', 'pallet_state',
                      'cont20_quantity', 'cont40_quantity', 'cont40h_quantity'}
        dim_fields = {'item_line_code', 'item_line_name', 'npd_code', 'npd_name', 'division_code', 'division_name',
                      'life_cycle_code', 'life_cycle_name', 'campaign_code', 'campaign_name'}
        barcode_fields = {'ean_no_', 'dun14_no_'}
        vendor_fields = {'vendor_item_no_', 'vendor_item_description'}
        price_fields = {'price_a', 'price_b', 'price_i', 'price_p', 'price_ddp', 'price_r'}
        extended_fields = {f'extended_text_{i}' for i in range(1, 11)}
        requested_uom = uom_fields & set(fields)
        requested_dims = dim_fields & set(fields)
        requested_barcodes = barcode_fields & set(fields)
        requested_vendors = vendor_fields & set(fields)
        requested_prices = price_fields & set(fields)
        requested_extended = extended_fields & set(fields)
        if filters:
            if filters.get('item_line'):
                requested_dims = requested_dims | {'item_line_code', 'item_line_name'}
        for field in fields:
            if field in fields_def:
                col_list, _ = fields_def[field]
                column_list.update(col_list)
        if requested_dims:
            dim_map = {
                'item_line_code': ('item_line', 'LINEA-PROD'),
                'item_line_name': ('item_line', 'LINEA-PROD'),
                'npd_code': ('npd', 'NPD'),
                'npd_name': ('npd', 'NPD'),
                'division_code': ('division', 'DIVISION'),
                'division_name': ('division', 'DIVISION'),
                'life_cycle_code': ('life_cycle', 'CICLO-VIDA'),
                'life_cycle_name': ('life_cycle', 'CICLO-VIDA'),
                'campaign_code': ('campaign', 'CAMPAÑA'),
                'campaign_name': ('campaign', 'CAMPAÑA'),
            }
            for df in requested_dims:
                name, dim_code = dim_map[df]
                if name not in use_ctes:
                    use_ctes[name] = DimensionSQL(
                        cte=DIMENSION_CTE_TPL.format(nav_company=self.nav_company, name=name, dim_code=dim_code),
                        column_list=f'{name}.Code {name}_code, {name}.Name {name}_name',
                        join=f'LEFT OUTER JOIN {name} ON {name}.No_ = item.No_'
                    )
        if requested_barcodes:
            if 'ean_no_' in requested_barcodes:
                use_ctes['ean'] = DimensionSQL(
                    cte=CROSS_REF_CTE_TPL.format(nav_company=self.nav_company, name='ean'),
                    column_list='ean.No_ ean_code',
                    join='LEFT OUTER JOIN ean ON ean.[Item No_] = item.No_',
                    params={'ean_type': CrossRefType.BARCODE.value, 'ean_type_no_': '', 'ean_unit_of_measure': 'UDS', 'ean_variant_code': '', 'ean_main_bar_code': 1}
                )
            if 'dun14_no_' in requested_barcodes:
                use_ctes['dun14'] = DimensionSQL(
                    cte=CROSS_REF_CTE_TPL.format(nav_company=self.nav_company, name='dun14'),
                    column_list='dun14.No_ dun14_code',
                    join='LEFT OUTER JOIN dun14 ON dun14.[Item No_] = item.No_',
                    params={'dun14_type': CrossRefType.BARCODE.value, 'dun14_type_no_': '', 'dun14_unit_of_measure': 'STD', 'dun14_variant_code': '', 'dun14_main_bar_code': 1}
                )
        if requested_vendors:
            use_ctes['vendor_item'] = DimensionSQL(
                cte=CROSS_REF_CTE_TPL.format(nav_company=self.nav_company, name='vendor_item'),
                column_list="ISNULL(NULLIF(item.[Vendor Item No_], ''), vendor_item.No_) vendor_item_no_, ISNULL(NULLIF(item.[Vendor Item No_], ''), vendor_item.Description) vendor_item_description",
                join='LEFT OUTER JOIN vendor_item ON vendor_item.[Item No_] = item.No_',
                params={'vendor_item_type': CrossRefType.VENDOR.value, 'vendor_item_type_no_': 'item.[Vendor No_]', 'vendor_item_unit_of_measure': 'item.[Base Unit of Measure]', 'vendor_item_variant_code': '', 'vendor_item_main_bar_code': 1}
            )
        for cte_name, cte_obj in use_ctes.items():
            if cte_obj.params:
                cte_params.update(cte_obj.params)
        return column_list, use_ctes, cte_params

    def _build_sql(self, use_ctes: dict, column_list: set, where: str) -> str:
        cte_parts = []
        joins = []
        for name, cte_obj in use_ctes.items():
            cte_parts.append(cte_obj.cte)
            if cte_obj.join:
                joins.append(cte_obj.join)
        select_cols = ', '.join(sorted(column_list))
        join_clause = ' '.join(joins)
        if use_ctes:
            cte_str = 'WITH ' + ', '.join(cte_parts) + ' '
        else:
            cte_str = ""
        sql = text(f"""{cte_str}SELECT {select_cols} FROM [{self.nav_company}$Item] item {join_clause} WHERE {where} ORDER BY item.[Report Order]""")
        return sql

    def _row_to_item(self, row, fields: list[str], fields_def: dict, session: Session, feature_profile: str) -> dict | None:
        item_data = {}
        for field in fields:
            if field in fields_def:
                _, processor = fields_def[field]
                try:
                    result = processor(row)
                    if result:
                        item_data.update(result)
                except Exception:
                    pass
        if 'features' in fields:
            feature_data = self._get_features(row.no_, session, feature_profile)
            item_data.update(feature_data)
            item_data.pop('features', None)
        item_fields = set(Item.model_fields.keys())
        feature_fields = {k for k in item_data.keys() if k.startswith('Feature_')}
        item_fields = item_fields | feature_fields
        item_data = {k: v for k, v in item_data.items() if k in item_fields}
        return item_data if item_data else None

    def _get_price(self, row, sales_code: str) -> dict[str, Any]:
        item_no = row.no_
        sql = text(f"""SELECT sp.[Unit Price] unit_price
            FROM [{self.nav_company}$Sales Price] sp
            WHERE sp.[Item No_] = :item_no_
              AND sp.[Sales Type] = 1
              AND sp.[Sales Code] = :sales_code
              AND (sp.[Unit of Measure Code] = :unit_of_measure OR :unit_of_measure = NULL)
              AND sp.[Currency Code] = :currency_code
              AND sp.[Starting Date] <= :starting_date
              AND (sp.[Ending Date] = '1753-01-01' OR sp.[Ending Date] >= :ending_date)
              AND sp.[Minimum Quantity] = :minimum_quantity
              AND sp.[Variant Code] = :variant_code""")
        params = {'item_no_': item_no, 'sales_code': sales_code, 'unit_of_measure': '', 'currency_code': '',
                  'starting_date': date.today(), 'ending_date': date.today(), 'minimum_quantity': 0, 'variant_code': ''}
        with Session(self.engine) as sess:
            result = sess.execute(sql, params).first()
            if result:
                return {f'price_{sales_code.lower()}': float(result.unit_price)}
        return {f'price_{sales_code.lower()}': None}

    def _get_uom(self, row, code: str, attr: str) -> dict[str, Any]:
        item_no = row.no_
        sql = text(f"""SELECT [Qty_ per Unit of Measure], [Height], [Width], [Length], [Cubage], [Weight], [State], [Layers], [Qty_ per Layer]
            FROM [{self.nav_company}$Item Unit of Measure]
            WHERE [Item No_] = :item_no_ AND Code = :code""")
        with Session(self.engine) as sess:
            result = sess.execute(sql, {'item_no_': item_no, 'code': code}).first()
            if result:
                idx_map = {
                    'quantity': 0, 'height': 1, 'width': 2,
                    'length': 3, 'cubage': 4, 'weight': 5, 'state': 6,
                    'layers': 7, 'qty__per_layer': 8
                }
                idx = idx_map.get(attr, 0)
                val = result[idx]
                if attr == 'state' and val is not None:
                    from application.pages.export_items.models import UOMState
                    val = uom_state_mapper(UOMState(val), 'es')
                elif val is not None and attr in ('quantity', 'height', 'width', 'length', 'cubage', 'layers', 'qty__per_layer'):
                    val = float(val)
                prefix = code.lower()
                return {f'{prefix}_{attr}': val}
        return {f'{code.lower()}_{attr}': None}

    def _get_features(self, item_no: str, session: Session, feature_profile: str) -> dict[str, Any]:
        questions = self.get_feature_questions(feature_profile)
        if not questions:
            return {}
        sql = text(f"""SELECT [Line No_], [Data Type], [Feature Integer], [Feature Decimal],
              [Feature Text], [Feature Date], [Feature Boolean]
            FROM [{self.nav_company}$Feature Questionnaire]
            WHERE [Profile Code] = :profile_code AND [No_] = :item_no_ ORDER BY [Line No_]""")
        result = session.execute(sql, {'profile_code': feature_profile, 'item_no_': item_no})
        rows = list(result)
        if not rows:
            return {}
        questionnaire = []
        for row in rows:
            print(f"DEBUG row: line_no={row[0]}, all_values={tuple(row)}")
            dt_val = row[1]
            try:
                data_type = FeatureDataType(dt_val)
            except ValueError:
                data_type = None
            if data_type is None or data_type == FeatureDataType.OPTION:
                continue
            value = None
            if data_type == FeatureDataType.INTEGER:
                value = row[2]
            elif data_type == FeatureDataType.DECIMAL:
                value = float(row[3]) if row[3] else None
            elif data_type == FeatureDataType.TEXT:
                value = row[4]
            elif data_type == FeatureDataType.DATE:
                value = row[5]
            elif data_type == FeatureDataType.BOOLEAN:
                value = row[6]
            line_no = row[0]
            print(f"DEBUG: line_no={line_no}, in_questions={line_no in questions}, value={value}, type={type(value)}")
            if line_no in questions:
                desc = questions[line_no].description.replace(' ', '_').replace('/', '_').replace('-', '_')
                col_name = f"Feature_{line_no}_{desc}"
                questionnaire.append((col_name, value))
        result_dict = {}
        for col_name, value in questionnaire:
            result_dict[col_name] = value
        return result_dict

    def get_lines(self) -> dict[str, str]:
        sql = text(f"""SELECT DISTINCT Code, [Name]
            FROM [{self.nav_company}$Dimension Value]
            WHERE [Dimension Code] = 'LINEA-PROD'
            ORDER BY Code""")
        with Session(self.engine) as session:
            try:
                lines = {r[1]: r[0] for r in session.execute(sql)}
            except Exception:
                lines = {}
        return lines

    @lru_cache
    def get_feature_questions(self, feature_profile: str) -> OrderedDict[int, FeatureQuestion]:
        sql = text(f"""SELECT feat.Type type, feat.Description description,
              feat.[Line No_] line_no_, feat.[Multiple Answers] multiple_answers, feat.[Data Type] data_type
            FROM [{self.nav_company}$Feature] feat
            WHERE feat.[Profile Code] = :profile_code ORDER BY feat.[Line No_]""")
        feature_questions = []
        with Session(self.engine) as session:
            for row in session.execute(sql, {'profile_code': feature_profile}):
                if row.type == 0:
                    feature_questions.append((row.line_no_, FeatureQuestion(
                        line_no_=row.line_no_, description=row.description,
                        multiple_answers=row.multiple_answers, answers=[],
                        data_type=FeatureDataType(row.data_type))))
                elif row.type == 1 and feature_questions:
                    feature_questions[-1][1].answers.append(
                        FeatureAnswer(description=row.description, line_no_=row.line_no_))
        return OrderedDict(feature_questions)
