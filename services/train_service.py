
import lxml.etree
import lxml.html
import requests
from aiogram.client.session import aiohttp


async def get_trains(station_from, station_to, date):
    # page - full code
    result = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pass.rw.by/ru/route/?from={station_from}&to={station_to}&date={date}') as response:
                # return await response.json()
                # TODO add user-agent
                # debug_print(f'{page}')
                # make a lxml tree
                tree = lxml.html.fromstring(await response.text())
                # print(lxml.html.tostring(tree))
                # search for trains by ccs
                transport_res = tree.cssselect('div.sch-table__row-wrap')
                # for each train
                for index, data in enumerate(transport_res, start=1):
                    # strip - without spaces
                    train_number = data.cssselect('span.train-number')[0].text_content().strip()
                    train_name = data.cssselect('span.train-route')[0].text_content().strip()
                    train_departure = data.cssselect('div.train-from-time')[0].text_content().strip()
                    train_arrival = data.cssselect('div.train-to-time')[0].text_content().strip()
                    train_duration = data.cssselect('div.train-duration-time')[0].text_content().strip()

                    train_info = {'index': index, 'train_number': train_number, 'train_name': train_name, 'train_departure': train_departure,
                                  'train_arrival': train_arrival, 'train_duration': train_duration}
                    result.append(train_info)
            # print(result)
    except Exception as error:
        print(error)
        result = None
    return result
