import asyncio
import re
import time
import pytest as pytest
import requests
from datetime import datetime
from termcolor import colored
import threading
import urllib3


# Configuración
CANT_REQUESTS = 20
URL_HOST = "https://pokeapi.co/api/v2/pokemon/raichu"
input_user_agent = "components/user-agents.txt"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Métodos
# Separador
def printer_separator():
    print('*' * 120)


# Nos da un user-agent random
def get_random_user_agent():
    try:
        with open(input_user_agent, 'r') as file:
            user_agents = file.read().splitlines()
            if not user_agents:
                return None
            import random
            return random.choice(user_agents)
    except FileNotFoundError:
        print(f"El archivo {input_user_agent} no existe.")
        return None


# Setea mejor el proxy para las pruebas.
def duplicate_proxy_urls(proxy_list):
    duplicated_list = []

    for proxy in proxy_list:
        ip_port = proxy.strip()
        ip, port = ip_port.split(':')
        http_proxy = f'http://{ip}:{port}'
        https_proxy = f'https://{ip}:{port}'

        duplicated_list.extend([http_proxy, https_proxy])

    return duplicated_list


# Realiza peticiones utilizando proxies
async def make_requests(proxy):
    session = requests.Session()
    session.proxies = {proxy}
    successful_requests = 0
    last_success = None
    last_fail = None
    last_status = None
    user_agent = get_random_user_agent()
    headers = {
        'User-Agent': user_agent,
        'Accept': 'application/json',
    }

    session.headers.update(headers)  # Set the headers for the session

    for _ in range(CANT_REQUESTS):
        try:
            response = await asyncio.to_thread(session.get, URL_HOST, timeout=5)
            if response.status_code == 200:
                last_status = response.status_code
                successful_requests += 1
                last_success = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_fail = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except (requests.exceptions.RequestException, asyncio.TimeoutError) as e:
            last_fail = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(colored(f"Error during request: {e}", 'red'))

    return successful_requests, last_success, last_fail, last_status


# Valida los proxies
async def validate_proxies(proxies):
    proxies_filtered = []
    tasks = []

    for proxy in proxies:
        tasks.append(make_requests(proxy))

    results = await asyncio.gather(*tasks)

    for proxy, (successful_requests, last_success, last_fail, last_status) in zip(proxies, results):
        if successful_requests >= CANT_REQUESTS // 2:
            await add_proxy_list_success(last_fail, last_success, proxies_filtered, proxy,
                                         successful_requests, last_status)

    return proxies_filtered


# Añade proxies validados a la lista de proxies exitosos
async def add_proxy_list_success(last_fail, last_success, proxies_filtered_success, proxy,
                                 successful_requests, last_status):
    proxies_filtered_success.append({
        "ip_port": proxy,
        "success_count": successful_requests,
        "fail_count": CANT_REQUESTS - successful_requests,
        "last_success": last_success,
        "last_fail": last_fail,
        "status": last_status
    })


# Filtra solo los valores de IP y puerto de una lista de proxies
def proxies_filtered_only(list_proxies_objects):
    ip_port_values = [proxy["ip_port"] for proxy in list_proxies_objects]
    return ip_port_values


# Extraemos el ip para sumar una validacion mas
def extract_ip(proxy):
    match = re.search(r'\d+\.\d+\.\d+\.\d+', proxy)
    if match:
        return match.group()
    return None


# Chequea si cambia el ip el proxy
def check_proxy_change(proxy, proxies_moving_ip, proxies_fixed_ip):
    try:
        r = requests.get('https://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=5)
        r.raise_for_status()
        current_ip = extract_ip(r.json()['origin'])

        if proxy not in proxies_fixed_ip and current_ip != extract_ip(proxy):
            proxies_moving_ip.append(proxy)
        elif proxy in proxies_moving_ip:
            proxies_moving_ip.remove(proxy)
        else:
            proxies_fixed_ip.append(proxy)

        print(f"Proxy {proxy} IP {'had changed to' if proxy in proxies_moving_ip else 'is fixed at'}: {current_ip}")

    except requests.exceptions.RequestException as e:
        if proxy in proxies_moving_ip:
            proxies_moving_ip.remove(proxy)


# Filtra proxies por cambio de IP
def filtered_by_change_ip(proxies_list_only_int):
    proxy_list = proxies_list_only_int
    proxies_moving_ip = []
    proxies_fixed_ip = []

    threads = []

    for proxy in proxy_list:
        thread = threading.Thread(target=check_proxy_change, args=(proxy, proxies_moving_ip, proxies_fixed_ip))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # Filtramos por duplicado
    proxies_moving_ip = list(set(proxies_moving_ip))
    proxies_fixed_ip = list(set(proxies_fixed_ip))

    print(colored(f"Proxies with IP on moving: {proxies_moving_ip}", 'cyan', 'on_black', ['bold', 'blink']))
    print(colored(f"Proxies with IP fixed: {proxies_fixed_ip}", 'yellow', 'on_black', ['bold', 'blink']))

    return proxies_moving_ip


# Validamos que no esten bloqueados los proxies finales
def validate_status(list_proxy):
    url = 'https://d3e6htiiul5ek9.cloudfront.net/prod/producto?limit=45&id_producto=7790040946200&array_sucursales=11-2-1052'
    valid_proxies = []
    user_agent = get_random_user_agent()
    headers = {
        'User-Agent': user_agent,
        'Accept': 'application/json',
    }
    for proxy in list_proxy:
        try:
            response = requests.get(url, headers=headers, proxies={'http': proxy})
            if response.status_code == 200:
                valid_proxies.append(proxy)
        except requests.exceptions.RequestException:
            pass
    print(colored(f"Final list: {valid_proxies}", 'green', 'on_black', ['bold', 'blink']))
    return valid_proxies


# Imprime el tiempo transcurrido desde el inicio
def time_to_get_some(start, some):
    seconds = str(int(time.time() - start))
    print(colored(f"{some} Execution time ............... {seconds} seconds", 'green', 'on_black', ['bold', 'blink']))


# Metodo principal
def ProxyInstantValidation(proxies_list: list):
    cant_proxies_initial = str(len(proxies_list))
    print(colored("Number of proxies before first filter: " + cant_proxies_initial, 'grey', 'on_green',
                  ['bold', 'blink']))
    list_http_https_proxies_before = duplicate_proxy_urls(proxies_list)
    list_proxies_before = list_http_https_proxies_before

    loop = asyncio.get_event_loop()
    valid_proxies = loop.run_until_complete(validate_proxies(list_proxies_before))
    proxies_list_only_int = proxies_filtered_only(valid_proxies)

    cant_proxies_after = str(len(valid_proxies))
    print(colored("Number of proxies after first filter: " + cant_proxies_after, 'grey', 'on_green',
                  ['bold', 'blink']))
    proxy_double_filtered = filtered_by_change_ip(proxies_list_only_int)
    final_list_proxy = validate_status(proxy_double_filtered)
    loop.close()

    print(final_list_proxy)
    return final_list_proxy


# if __name__ == '__main__':


@pytest.fixture
def proxies_list(proxies_list: list):
    list_proxies = proxies_list
    return list_proxies


# Prueba asincrónica para validar proxies
@pytest.mark.asyncio
async def test_validate_proxies(proxies_list):
    proxies = proxies_list
    result = await validate_proxies(proxies)

    assert isinstance(result, list)
    for proxy_data in result:
        assert isinstance(proxy_data, dict)
        assert "ip_port" in proxy_data
        assert "success_count" in proxy_data
        assert "fail_count" in proxy_data
        assert "last_success" in proxy_data
        assert "last_fail" in proxy_data
