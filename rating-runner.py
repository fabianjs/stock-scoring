from queue import Queue
from threading import Thread

from libs.Rating import Rating
from libs.downloader import OnVistaDownloader as downloader
from libs.model import IndexGroup
from libs.scraper import OnVistaScraper as scraper
from libs.storage import IndexStorage, StockStorage

task_download_index = True
task_download = True
task_scrap = True
print_full = True
skip_underrated = True

# indexGroup = IndexGroup("DE0008469008", "DAX")
# indexGroup = IndexGroup("DE0008467416", "MDAX")
# indexGroup = IndexGroup("DE0007203275", "TecDAX")
# indexGroup = IndexGroup("DE0009653386", "SDAX")
# indexGroup = IndexGroup("EU0009658145", "EURO-STOXX-50")
# indexGroup = IndexGroup("AT0000999982", "ATX")
# indexGroup = IndexGroup("CH0009980894", "SMI")
indexGroup = IndexGroup("US2605661048", "Dow-Jones")
# indexGroup = IndexGroup("US6311011026", "NASDAQ")

index_storage = IndexStorage("dump", indexGroup, source="onvista")

downloader.dump_index(indexGroup, index_storage)

scraper.read_stocks(indexGroup, index_storage)
scraper.scrap_index(indexGroup, index_storage)

for stock in indexGroup.stocks:
    stock_storage = StockStorage(index_storage, stock)

    stock_storage.load()

    stock = stock_storage.stock

    rating = Rating(stock)
    result = rating.rate()

    if rating.is_small:
        stock_type = "S"
    elif rating.is_medium:
        stock_type = "M"
    else:
        stock_type = "L"

    if rating.is_finance:
        stock_type += ", F"

    buy_signal = ""
    if rating.is_small or rating.is_medium:
        if result == 7:
            buy_signal = "+"
        elif result > 7:
            buy_signal = "++"
        elif skip_underrated:
            continue
    else:
        if result == 4:
            buy_signal = "+"
        elif result > 4:
            buy_signal = "++"
        elif skip_underrated:
            continue

    if print_full:
        print("- Kennzahlen")
        stock.print_report()
        print("- Einzelbewertung")
        rating.print_overview()

    print("Bewertung: %s %s (%s)\t[%i]\t%s" % (stock.stock_id, stock.name, stock_type, result, buy_signal))
    if print_full:
        print("---")