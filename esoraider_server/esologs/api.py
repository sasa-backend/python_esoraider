import asyncio
from typing import Dict, List, Optional, Union

import backoff  # type: ignore
from gql import Client  # type: ignore
from gql.dsl import DSLField, DSLQuery, DSLSchema, dsl_gql  # type: ignore
from gql.transport.aiohttp import AIOHTTPTransport  # type: ignore
from gql.transport.exceptions import (  # type: ignore
    TransportClosed,
    TransportQueryError,
)
from loguru import logger
from oauthlib.oauth2 import BackendApplicationClient  # type: ignore
from requests_oauthlib import OAuth2Session  # type: ignore

from esoraider_server.esologs.consts import DataType, HostilityType
from esoraider_server.esologs.responses.base import BaseResponseData
from esoraider_server.esologs.responses.report_data.casts import CastsTableData
from esoraider_server.esologs.responses.report_data.effects import (
    EffectsTableData,
)
from esoraider_server.esologs.responses.report_data.graph import (
    Event,
    GraphData,
)
from esoraider_server.esologs.responses.report_data.report import Report
from esoraider_server.esologs.responses.report_data.summary import (
    SummaryTableData,
)
from esoraider_server.esologs.responses.world_data.encounter import Encounter
from esoraider_server.settings import CLIENT_ID, CLIENT_SECRET

WAIT_FOR = 300
TIMEOUT = 10.0


class ApiWrapper:
    # https://github.com/graphql-python/gql/issues/179#issuecomment-749044193
    def __init__(self) -> None:
        self._token = self._auth()
        self._transport = AIOHTTPTransport(
            url='https://www.esologs.com/api/v2/client',
            headers={'Authorization': 'Bearer {0}'.format(self._token)},
        )
        self._client = Client(
            transport=self._transport,
            fetch_schema_from_transport=True,
        )
        self._session = None
        self._connect_task = None

        self._close_request_event: Optional[asyncio.Event] = None
        self._reconnect_request_event: Optional[asyncio.Event] = None

        self._connected_event: Optional[asyncio.Event] = None
        self._closed_event: Optional[asyncio.Event] = None

        self.ds: DSLSchema = None

    def _auth(self):
        access_token_url = 'https://www.esologs.com/oauth/token'

        client = BackendApplicationClient(client_id=CLIENT_ID)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(
            token_url=access_token_url,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        return token['access_token']

    @backoff.on_exception(backoff.expo, Exception, max_time=WAIT_FOR)
    async def _connection_loop(self):
        while True:
            logger.info('Connecting to API')
            try:
                async with self._client as session:
                    self._session = session
                    self.ds = DSLSchema(self._client.schema)
                    logger.info('Connected to API')
                    self._connected_event.set()

                    # Wait for the close or reconnect event
                    self._close_request_event.clear()
                    self._reconnect_request_event.clear()

                    close_event_task = asyncio.create_task(
                        self._close_request_event.wait(),
                    )
                    reconnect_event_task = asyncio.create_task(
                        self._reconnect_request_event.wait(),
                    )

                    events = [close_event_task, reconnect_event_task]

                    done, pending = await asyncio.wait(
                        events, return_when=asyncio.FIRST_COMPLETED,
                    )

                    for task in pending:
                        task.cancel()

                    if close_event_task in done:
                        # If we received a closed event,
                        # then we go out of the loop
                        break

                    # If we received a reconnect event,
                    # then we disconnect and connect again
            finally:
                self._session = None
                logger.info('Disconnected from API')
        logger.info('Connection closed')
        self._closed_event.set()

    async def connect(self):
        self._close_request_event = asyncio.Event()
        self._reconnect_request_event = asyncio.Event()

        self._connected_event = asyncio.Event()
        self._closed_event = asyncio.Event()

        logger.info('Opening connection')
        if self._connect_task:
            logger.info('Already connected')
        else:
            self._connected_event.clear()
            self._connect_task = asyncio.create_task(self._connection_loop())
            await asyncio.wait_for(
                self._connected_event.wait(), timeout=TIMEOUT,
            )

    async def close(self):
        logger.info('Disconnecting')
        self._connect_task = None
        self._closed_event.clear()
        self._close_request_event.set()
        await asyncio.wait_for(self._closed_event.wait(), timeout=TIMEOUT)

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def execute(self, *args, **kwargs):
        try:
            answer = await self._session.execute(*args, **kwargs)
        except TransportClosed:
            self._reconnect_request_event.set()
            raise
        except TransportQueryError as ex:
            logger.error(ex)
            return ex

        return answer

    async def query_name(self, encounter_id: int) -> Encounter:
        logger.info('Requesting info on encounter = {0}'.format(encounter_id))
        query = self.ds.Query.worldData

        encounter = self.ds.WorldData.encounter(id=encounter_id)
        difficulties_fields = self.ds.Zone.difficulties.select(
            self.ds.Difficulty.id,
            self.ds.Difficulty.name,
        )
        zone_fields = self.ds.Encounter.zone.select(
            difficulties_fields,
        )
        encounter_fields = encounter.select(
            self.ds.Encounter.id,
            self.ds.Encounter.name,
            zone_fields,
        )

        query.select(encounter_fields)

        return BaseResponseData.from_dict(
            await self.execute(dsl_gql(DSLQuery(query))),
        ).world_data.encounter

    async def query_log(self, log: str):
        logger.info('Requesting log {0}'.format(log))
        query = self.ds.Query.reportData

        report = self.ds.ReportData.report(code=log)
        fight_fields = self.ds.Report.fights.select(
            self.ds.ReportFight.id,
            self.ds.ReportFight.name,
            self.ds.ReportFight.difficulty,
            self.ds.ReportFight.fightPercentage,
            self.ds.ReportFight.encounterID,
            self.ds.ReportFight.kill,
            self.ds.ReportFight.startTime,
            self.ds.ReportFight.endTime,
            self.ds.ReportFight.gameZone.select(self.ds.GameZone.name),
            self.ds.ReportFight.friendlyPlayers,
        )
        report_fields = report.select(
            self.ds.Report.code,
            self.ds.Report.title,
            self.ds.Report.endTime,
            # self.ds.Report.rankings, # for so-called partition aka patch
            self.ds.Report.owner.select(self.ds.User.name),
            fight_fields,
        )

        query.select(report_fields)
        return await self.execute(dsl_gql(DSLQuery(query)))

    async def query_fight_times(self, log: str, fight_id: int):
        logger.info('Requesting fight times of log = {0}, fight = {1}'.format(
            log, fight_id,
        ))
        query = self.ds.Query.reportData
        report = self.ds.ReportData.report(code=log)
        fight = self.ds.Report.fights(fightIDs=fight_id)
        fight_fields = fight.select(
            self.ds.ReportFight.startTime,
            self.ds.ReportFight.endTime,
        )
        report_fields = report.select(fight_fields)

        query.select(report_fields)
        return await self.execute(dsl_gql(DSLQuery(query)))

    async def query_table(
        self,
        log: str,
        fight_id: int,
        data_type: str = 'Summary',
        hostility_type: str = 'Friendlies',
        start_time: int = None,
        end_time: int = None,
        source_id: int = None,
        target_id: int = None,
        filter_exp: str = None,
    ) -> Union[SummaryTableData, CastsTableData, EffectsTableData]:
        logger.info('Requesting reportData')
        logger.info('Log = {0}'.format(log))
        logger.info('Fight ID = {0}'.format(fight_id))
        logger.info('Data Type = {0}'.format(data_type))
        logger.info('Hostility Type = {0}'.format(hostility_type))
        logger.info('Start Time = {0}'.format(start_time))
        logger.info('End Time = {0}'.format(end_time))
        logger.info('Source ID = {0}'.format(source_id))
        logger.info('Target ID = {0}'.format(target_id))
        logger.info('Filter = {0}'.format(filter_exp))

        if (start_time is None) and (end_time is None):
            start_time, end_time = await self._get_fight_times(log, fight_id)

        query = self.ds.Query.reportData

        report = self.ds.ReportData.report(code=log)
        table = self.ds.Report.table(
            startTime=start_time,
            endTime=end_time,
            dataType=data_type,
            hostilityType=hostility_type,
            sourceID=source_id,
            targetID=target_id,
            filterExpression=filter_exp,
        )
        report_fields = report.select(table)

        query.select(report_fields)

        response = BaseResponseData.from_dict(
            await self.execute(dsl_gql(DSLQuery(query))),
        )

        types = {
            'Summary': SummaryTableData,
            'DamageDone': CastsTableData,
            'Casts': CastsTableData,
            'Buffs': EffectsTableData,
            'Debuffs': EffectsTableData,
        }
        table_data = types[data_type]

        return table_data.from_dict(response.report_data.report.table.data)

    async def query_char_table(
        self,
        log: str,
        fight_id: int,
        char_id: int,
        start_time: int = None,
        end_time: int = None,
    ) -> Report:
        logger.info('Requesting char summary table')
        logger.info('Log = {0}'.format(log))
        logger.info('Fight ID = {0}'.format(fight_id))
        logger.info('Char ID = {0}'.format(char_id))
        logger.info('Start Time = {0}'.format(start_time))
        logger.info('End Time = {0}'.format(end_time))

        if (start_time is None) and (end_time is None):
            start_time, end_time = await self._get_fight_times(log, fight_id)

        query = self.ds.Query.reportData

        report = self.ds.ReportData.report(code=log)
        fights = self.ds.Report.fights(fightIDs=fight_id).select(
            self.ds.ReportFight.encounterID,
            self.ds.ReportFight.difficulty,
        )
        table = self.ds.Report.table(
            startTime=start_time,
            endTime=end_time,
            dataType='Summary',
            sourceID=char_id,
        )
        report_fields = report.select(table).select(fights)

        query.select(report_fields)

        response = BaseResponseData.from_dict(
            await self.execute(dsl_gql(DSLQuery(query))),
        ).report_data.report
        response.table.data = SummaryTableData.from_dict(response.table.data)

        return response

    async def query_events(
        self,
        log: str,
        char_id: int,
        start_time: int,
        end_time: int,
        data_type: str = 'CombatantInfo',
    ) -> List[Event]:
        logger.info('Requesting events')
        logger.info('Log = {0}'.format(log))
        logger.info('Char ID = {0}'.format(char_id))
        logger.info('Start Time = {0}'.format(start_time))
        logger.info('End Time = {0}'.format(end_time))
        logger.info('Data Type = {0}'.format(data_type))

        query = self.ds.Query.reportData

        report = self.ds.ReportData.report(code=log)
        events = self.ds.Report.events(
            # ********************** GQL forbidden magic **********************
            # GQL will turn numbers into scientific notation, which means
            # number '6951757' will turn into '6.95176e+06'. As you can see,
            # last digit got rounded which will potentially skip needed events.
            # So we will substract one second (1000) from start_time
            # just to avoid this loss
            startTime=start_time - 1000,
            endTime=end_time,
            sourceID=char_id,
            dataType=data_type,
        ).select(self.ds.ReportEventPaginator.data)

        report_fields = report.select(events)

        query.select(report_fields)

        response = BaseResponseData.from_dict(
            await self.execute(dsl_gql(DSLQuery(query))),
        )

        return [
            Event.from_dict(event)
            for event in response.report_data.report.events.data
        ]

    async def query_graph(
        self,
        log: str,
        char_id: int,
        ability_id: int = None,
        fight_id: int = None,
        start_time: int = None,
        end_time: int = None,
        data_type: DataType = DataType.BUFFS,
        hostility_type: HostilityType = HostilityType.FRIENDLIES,
        graphs: Dict[str, DSLField] = None,
    ) -> Dict[int, GraphData]:
        logger.info('Requesting graph')
        logger.info('Log = {0}'.format(log))
        logger.info('Fight ID = {0}'.format(fight_id))
        logger.info('Char ID = {0}'.format(char_id))
        logger.info('Start Time = {0}'.format(start_time))
        logger.info('End Time = {0}'.format(end_time))
        logger.info('Data Type = {0}'.format(data_type))
        logger.info('Ability ID = {0}'.format(ability_id))
        logger.info('Hostility Type = {0}'.format(hostility_type))

        if (start_time is None) and (end_time is None):
            start_time, end_time = await self._get_fight_times(log, fight_id)

        query = self.ds.Query.reportData

        report = self.ds.ReportData.report(code=log)

        if ability_id and not graphs:
            graph = await self.partial_query_graph(
                data_type=data_type,
                ability_id=ability_id,
                start_time=start_time,
                end_time=end_time,
                hostility_type=hostility_type,
                char_id=char_id,
            )
            report_fields = report.select(**graph)
        elif graphs:
            report_fields = report.select(**graphs)

        query.select(report_fields)

        response = await self.execute(dsl_gql(DSLQuery(query)))
        response = response.get('reportData')
        response = response.get('report')

        return {
            int(id_.split('_')[1]): GraphData.from_dict(graph.get('data'))
            for id_, graph in response.items()
        }

    async def partial_query_graph(
        self,
        data_type: DataType,
        ability_id: int,
        start_time: int,
        end_time: int,
        hostility_type: HostilityType = HostilityType.FRIENDLIES,
        char_id: Optional[int] = None,
    ) -> Dict[str, DSLField]:
        logger.info('Building partial graph request')
        logger.info('Char ID = {0}'.format(char_id))
        logger.info('Start Time = {0}'.format(start_time))
        logger.info('End Time = {0}'.format(end_time))
        logger.info('Data Type = {0}'.format(data_type))
        logger.info('Ability ID = {0}'.format(ability_id))
        logger.info('Hostility Type = {0}'.format(hostility_type))

        source_id = char_id if hostility_type == HostilityType.FRIENDLIES else None
        target_id = char_id if hostility_type == HostilityType.ENEMIES else None

        return {
            'id_{0}'.format(ability_id): self.ds.Report.graph(
                startTime=start_time,
                endTime=end_time,
                abilityID=ability_id,
                hostilityType=hostility_type.value,
                dataType=data_type.value,
                sourceID=source_id,
                targetID=target_id,
            ),
        }

    async def _get_fight_times(self, log: str, fight_id: int):
        response = await self.query_fight_times(log, fight_id)
        response = response.get('reportData').get('report').get('fights')[0]
        return response.get('startTime'), response.get('endTime')
