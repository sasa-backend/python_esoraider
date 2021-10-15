from dataclasses import dataclass
from typing import List, Optional, Union

from esologs.responses.core import EsoLogsDataClass
from esologs.responses.report_data.casts import CastsTableData
from esologs.responses.report_data.effects import EffectsTableData
from esologs.responses.report_data.fight import Fight
from esologs.responses.report_data.graph import GraphData


@dataclass
class BaseData(EsoLogsDataClass):
    data: Union[CastsTableData, EffectsTableData, GraphData, None] = None


@dataclass
class Report(EsoLogsDataClass):
    fights: Optional[List[Fight]] = None
    graph: Optional[BaseData] = None
    table: Optional[BaseData] = None