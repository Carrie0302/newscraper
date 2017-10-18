import json
import mongo_driver
from pprint import pprint
from custom_classes import addDict


def transform_open_format(x):
    ''' Original format:
        (u'NutritionalAnarchy.com',
        {u'2nd type': u'',
        u'3rd type': u'',
        u'Source Notes (things to know?)': u'',
        u'type': u'unreliable'})
    '''

    urls = mongo_driver.get_url('opensources')
    if x[0] in urls:
        return

    template = {
        'Category': 'conspiracy',
        'Reference': 'http://mediabiasfactcheck.com/zero-hedge/',
        'Truthiness': 'MIXED',
        'url': 'http://www.zerohedge.com/'
    }

    out_dict = dict().fromkeys(template)
    out_dict['url'] = x[0]
    out_dict['Category'] = ', '.join(
        list(set([x[1][_] for _ in x[1].keys() if 'type' in _ and x[1][_]])))
    out_dict['Reference'] = 'http://www.opensources.co'

    mongo_driver.insert('opensources', out_dict)


def load_opensources():
    mongo_driver.kill('opensources')
    opensources = json.load(
        open('/home/z/Documents/myRepos/newscraper/opensources/sources/sources.json'))
    list(map(transform_open_format, opensources.items()))
    assert mongo_driver.check_for_dups('opensources')


def get_clean_urls(table_name):
    raw_data = list(mongo_driver.get_all(table_name))
    urls = list(filter(lambda item: 'url' in item, raw_data))

    def clean_link(data):

        link = data['url'].lower().replace('http://', '').replace('https://', '').replace(
            'www.', '').replace((' '), '')

        if link.endswith('/'):
            return link[:-1], data
        else:
            return link, data

    return dict(list(map(lambda item: clean_link(item), urls)))


if __name__ == '__main__':

    mongo_driver.kill('all_sources')
    os_data = get_clean_urls('opensources')
    mb_data = get_clean_urls('media_bias')

    os_urls = set(os_data.keys())
    mb_urls = set(mb_data.keys())

    shared_urls = os_urls & mb_urls

    stats = {
        'individual': [len(os_urls), len(mb_urls)],
        'total': [len(os_urls) + len(mb_urls)],
        'not shared': len(os_urls ^ mb_urls),
        'shared': len(shared_urls),
        'total': len(os_urls | mb_urls),
        'opensource only': len(os_urls - mb_urls),
        'mediabias only': len(mb_urls - os_urls)
    }
    print(stats)

    def merge(url):
        os_ = addDict(os_data[url])
        mb_ = addDict(mb_data[url])
        [os_.pop(_) for _ in ('_id', 'Truthiness', 'url')]
        [mb_.pop(_) for _ in ('_id', 'url')]

        mb_['Category'] = mb_['Category'].replace('fake-news', 'fake').split(', ')
        os_['Category'] = os_['Category'].split(', ')

        merged_ = mb_ + os_
        merged_['url'] = url
        mongo_driver.insert('all_sources', merged_)

    def correct(url, source):
        if source == 'os':
            os_ = os_data[url]
            os_['Category'] = os_['Category'].split(', ')
            os_['url'] = url
            mongo_driver.insert('all_sources', os_)
        elif source == 'mb':
            mb_ = mb_data[url]
            mb_['Category'] = mb_['Category'].replace('fake-news', 'fake').split(', ')
            mb_['url'] = url
            mongo_driver.insert('all_sources', mb_)

    [correct(url, 'os') for url in os_urls - mb_urls]
    [correct(url, 'mb') for url in mb_urls - os_urls]
    list(map(merge, shared_urls))
