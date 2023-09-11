import time
from services.db_manager import AddProxyList, FilterExistingProxys
from data import WEBS_FOR_SCRAP
from components.ProxyHarvest import ProxyHarvest
from components.ProxyInstantValidation import ProxyInstantValidation, time_to_get_some


def main():
    start = time.time()
    some = 'Final'
    proxy_list_harvested = ProxyHarvest(WEBS_FOR_SCRAP)
    proxy_list = FilterExistingProxys(proxy_list_harvested)
    valid_proxys = ProxyInstantValidation(proxy_list)
    AddProxyList(valid_proxys)
    time_to_get_some(start, some)


if __name__ == '__main__':
    main()