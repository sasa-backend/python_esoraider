"""Summary table (dataType: Summary) response."""

from dataclasses import dataclass, field
from typing import Any, List, Optional

from dataclasses_json import config
from esologs.responses.common import Gear, Talent
from esologs.responses.core import EsoLogsDataClass


@dataclass
class CombatantInfo(EsoLogsDataClass):
    stats: List[Any]
    talents: List[Talent]
    gear: List[Gear]

    spec_ids: Optional[List[Any]] = field(
        default=None,
        metadata=config(field_name='specIDs'),
    )
    artifact: Optional[List[Any]] = None

    def skill_ids(self):
        return [t.guid for t in self.talents]


@dataclass
class PlayerDetails(EsoLogsDataClass):
    name: str
    id: int
    guid: int
    type: str
    server: str
    display_name: str
    anonymous: bool
    icon: str
    specs: List[str]
    combatant_info: CombatantInfo

    min_item_level: Optional[int] = None
    max_item_level: Optional[int] = None


@dataclass
class PlayerDetailsBySpec(EsoLogsDataClass):
    dps: Optional[List[PlayerDetails]] = None
    healers: Optional[List[PlayerDetails]] = None
    tanks: Optional[List[PlayerDetails]] = None


@dataclass
class DoneByAbility(EsoLogsDataClass):
    name: str
    guid: int
    type: int
    ability_icon: str
    total: int

    composite: Optional[bool] = None
    flags: Optional[int] = None


@dataclass
class DeathFromAbility(EsoLogsDataClass):
    name: str
    guid: int
    type: int
    ability_icon: str
    flags: int


@dataclass
class DeathEvent(EsoLogsDataClass):
    name: str
    id: int
    guid: int
    type: str
    icon: str
    death_time: int
    ability: DeathFromAbility


@dataclass
class DoneByChar(EsoLogsDataClass):
    name: str
    guid: int
    type: str
    total: int

    id: Optional[int] = None
    icon: Optional[str] = None
    ability_icon: Optional[str] = None
    composite: Optional[bool] = None
    flags: Optional[int] = None


@dataclass
class Spec(EsoLogsDataClass):
    spec: str
    role: str


@dataclass
class Composition(EsoLogsDataClass):
    name: str
    id: int
    guid: int
    type: str
    specs: List[Spec]


@dataclass
class SummaryTableData(EsoLogsDataClass):
    total_time: int
    item_level: float
    log_version: int
    game_version: int
    composition: List[Composition]
    damage_done: List[DoneByChar]
    healing_done: List[DoneByChar]
    damage_taken: List[DoneByAbility]
    death_events: List[DeathEvent]

    combatant_info: Optional[CombatantInfo] = None
    player_details: Optional[PlayerDetailsBySpec] = None
