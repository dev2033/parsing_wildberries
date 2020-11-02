import bs4
import collections
import csv
import requests

from my_logging import logger


url = "https://www.wildberries.ru/catalog/muzhchinam/odezhda/vodolazki"

# Создает namedtuple с заголовком ParseResult
ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url_domain',
    ),
)

# Названия 'полей в таблице'
HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка',
)


class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"
        }
        self.result = []

    def load_page(self):
        """Загружает страницу"""
        url = "https://www.wildberries.ru/catalog/muzhchinam/odezhda/vodolazki"
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        """Парсит страницу"""
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.dtList.i-dtList.j-card-item')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        """Парсит блок по частям"""
        domain = 'https://www.wildberries.ru'

        url_block = block.select_one('a.ref_goods_n_p.j-open-full-product-card')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return

        name_block = block.select_one('div.dtlist-inner-brand-name')
        if not name_block:
            logger.error('no name_block')
            return

        brand_name = name_block.select_one('strong.brand-name.c-text-sm')
        if not brand_name:
            logger.error('no brand_name')
            return

        # Удаляем / между названием фирмы и названием товара
        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = name_block.select_one('span.goods-name.c-text-sm')
        if not goods_name:
            logger.error('no goods_name')
            return
        goods_name = goods_name.text.strip()

        # Переменная url_domain - нужна для того чтобы
        # совметстить href и название + домен сайта
        url_domain = domain + url

        # Заполняем массив
        self.result.append(ParseResult(
            url_domain=url_domain,
            brand_name=brand_name,
            goods_name=goods_name,
        ))

        # Данный код нужен для отладки и проверки работоспособности кода
        # out_logger = '%s, %s, %s', url_domain, brand_name, goods_name
        # logger.debug(out_logger)
        # logger.debug('-' * 100)

    def save_result(self):
        """Сохраняет данные в csv файл"""
        path_file = 'result_csv/main.csv'
        with open(path_file, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        """Стартует"""
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Получили {len(self.result)} элементов')
        self.save_result()


if __name__ == '__main__':
    parser = Client()
    parser.run()
