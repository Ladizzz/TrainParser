
import lxml.etree
import lxml.html
from aiogram.client.session import aiohttp
from fake_useragent import UserAgent


async def get_trains(station_from, station_to, date, detailed_response=False):
    # page - full code
    result = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pass.rw.by/ru/route/?from={station_from}&to={station_to}&date={date}',
                                   headers={'user-agent': UserAgent().random}) as response:
                # make a lxml tree
                tree = lxml.html.fromstring(await response.text())
                # print(lxml.html.tostring(tree))
                # search for trains by ccs
                trains = tree.cssselect('div.sch-table__row-wrap')
                # for each train
                for index, data in enumerate(trains, start=1):
                    # strip - without spaces
                    train_number = data.cssselect('span.train-number')[0].text_content().strip()
                    train_name = data.cssselect('span.train-route')[0].text_content().strip()
                    train_departure = data.cssselect('div.train-from-time')[0].text_content().strip()
                    train_arrival = data.cssselect('div.train-to-time')[0].text_content().strip()
                    train_duration = data.cssselect('div.train-duration-time')[0].text_content().strip()
                    tickets_bad = data.cssselect('div.sch-table__no-info')
                    tickets = []
                    if not tickets_bad and detailed_response:
                        tickets_raw = data.cssselect('div.sch-table__t-item')
                        for ticket_raw in tickets_raw:
                            # ticket = str(lxml.html.tostring(ticket_raw))
                            ticket = {}
                            # тип
                            ticket_type_raw = ticket_raw.cssselect('div.sch-table__t-name')
                            if ticket_type_raw[0].text is not None and ticket_type_raw[0].text != ' ':
                                ticket['type'] = ticket_type_raw[0].text
                            # кол-во
                            ticket_free_raw = ticket_raw.cssselect('a.sch-table__t-quant')
                            if ticket_free_raw[0].text_content() is not None:
                                ticket['available_seats'] = ticket_free_raw[0].text_content().strip()
                            # стоимость
                            ticket_prices_raw = ticket_raw.cssselect('span.ticket-cost')
                            ticket['prices'] = ticket_prices_raw[0].text_content().strip()
                            tickets.append(ticket)

                    train_info = {'index': index, 'train_number': train_number, 'train_name': train_name, 'train_departure': train_departure,
                                  'train_arrival': train_arrival, 'train_duration': train_duration, 'tickets': tickets}
                    result.append(train_info)
            # print(result)
    except Exception as error:
        print(error)
        result = None
    return result
