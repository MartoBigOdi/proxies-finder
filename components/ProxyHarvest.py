import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from playwright._impl._api_types import Error as PlaywrightError


def copy_text(url: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Añade cabeceras para simular un navegador real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                # Aquí puedes agregar más cabeceras si es necesario
            }
            page.set_extra_http_headers(headers)

            page.goto(url)

            try:
                page.wait_for_load_state('networkidle')
            except PlaywrightError as e:
                page.wait_for_load_state('domcontentloaded')

            page.wait_for_selector('body')

            # Obtiene todo el contenido de texto seleccionable en la página
            selectable_text = page.evaluate('''() => {
                let selectableText = '';
                const textNodes = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                let currentNode;

                while (currentNode = textNodes.nextNode()) {
                    if (currentNode.textContent.trim() !== '') {
                        selectableText += currentNode.textContent + '\\n';
                    }
                }

                return selectableText;
            }''')

            browser.close()

            return selectable_text
    except TimeoutError:
        print(f"Timeout al procesar {url}")
        return ''
    except PlaywrightError as e:
        print(f"Error al procesar {url}: {e}")
        return ''


def harvest(url: str):
    proxies = []
    try:
        text = copy_text(url)
        proxies = re.findall(r'(\d+\.\d+\.\d+\.\d+\n\d+)', text)

        # format the proxies
        proxies = [proxy.replace('\n', ':') for proxy in proxies]
        print(f"Procesado {url} con {len(proxies)} proxies")
    except Exception as e:
        print(f"Error al procesar {url}: {e}")

    return proxies


def ProxyHarvest(webs_for_scrap: list):
    import time 
    start = time.time()
    proxies = []

    print(f"Procesando {len(webs_for_scrap)} webs...")

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(harvest, url) for url in webs_for_scrap]

        for future in as_completed(futures):
            proxy = future.result()
            proxies.extend(proxy)

    proxies = list(set(proxies))
    print(f"Tiempo de ejecución: {time.time() - start} segundos")
    return proxies


# if __name__ == '__main__':
