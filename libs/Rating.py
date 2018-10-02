from libs.model import Stock, AnalystRatings


class Rating:

    def __init__(self, stock: Stock):
        self.stock = stock
        self.is_medium = check_for_medium_stock(stock)
        self.is_small = check_for_small_stock(stock)

        self.roi = 0
        self.ebit = 0
        self.equity_ratio = 0
        self.per_5_years = 0
        self.per = 0
        self.ratings = 0
        self.quarterly_figures = 0
        self.profit_revision = 0
        self.performance_6_month = 0
        self.performance_1_year = 0
        self.price_momentum = 0
        self.month_closings = 0
        self.eps = 0

    def rate(self):

        self.roi = rate_roi(self.stock.roi)
        self.ebit = rate_ebit(self.stock.ebit_margin)
        self.equity_ratio = rate_equity_ratio(self.stock.equity_ratio)
        self.per_5_years = rate_per(self.stock.per_5_years)
        self.per = rate_per(self.stock.per)

        if (self.is_small and self.stock.ratings.count() <= 5):
            self.ratings = rate_small_ratings(self.stock.ratings)
        else:
            self.ratings = rate_ratings(self.stock.ratings)

        self.quarterly_figures = 0
        self.profit_revision = 0

        self.performance_6_month = rate_performance(self.stock.history.performance_6_month(),
                                                    self.stock.indexGroup.history.performance_6_month())

        self.performance_1_year = rate_performance(self.stock.history.performance_1_year(),
                                                   self.stock.indexGroup.history.performance_1_year())
        self.price_momentum = rate_price_momentum(self.performance_6_month, self.performance_1_year)

        if (self.is_medium or self.is_small):
            self.month_closings = 0
        else:
            self.month_closings = rate_monthClosings(self.stock.monthClosings.calculate_performance(),
                                                     self.stock.indexGroup.monthClosings.calculate_performance())

        self.eps = rate_eps(self.stock.eps_current_year, self.stock.eps_next_year)

        all_ratings = [self.roi, self.ebit, self.equity_ratio, self.per_5_years, self.per, self.ratings,
                       self.quarterly_figures, self.profit_revision, self.performance_6_month,
                       self.performance_1_year, self.price_momentum, self.month_closings, self.eps]

        return sum(all_ratings)

    def print_overview(self):
        print("1. Eigenkapitalrendite 2017: \t%i" % self.roi)
        print("2. EBIT-Marge 2017\t\t\t\t%i" % self.ebit)
        print("3. Eigenkapitalquote 2017\t\t%i" % self.equity_ratio)
        print("4. KGV 5 Jahre\t\t\t\t\t%i" % self.per_5_years)
        print("5. KGV 2018e\t\t\t\t\t%i" % self.per)
        print("6. Analystenmeinungen:\t\t\t%i" % self.ratings)
        print("7. Reaktion auf Quartalszahlen\t%i" % self.quarterly_figures)
        print("8. Gewinnrevision\t\t\t\t%i" % self.profit_revision)
        print("9. Performance 6 Monaten\t\t%i" % self.performance_6_month)
        print("10. Performance 1 Jahr\t\t\t%i" % self.performance_1_year)

        print("11. Kursmomentum steigend\t\t%i" % self.price_momentum)

        print("12. Dreimonatsreversal\t\t\t%i" % self.month_closings)

        print("13. EPS \t\t\t\t\t\t%i" % self.eps)


def check_for_small_stock(stock: Stock):
    return stock.market_capitalization < 2, 000, 000, 000


def check_for_medium_stock(stock: Stock):
    return stock.market_capitalization < 5, 000, 000, 000 and stock.market_capitalization >= 2, 000, 000, 000


def rate_roi(roi):
    if roi > 20: return 1
    if roi < 10: return -1
    return 0


def rate_ebit(ebit_margin):
    if ebit_margin > 12: return 1
    if ebit_margin < 6: return -1
    return 0


def rate_equity_ratio(equity_ratio):
    if equity_ratio > 25: return 1
    if equity_ratio < 15: return -1
    return 0


def rate_per(per):
    if per < 12: return 1
    if per > 16: return -1
    return 0


def rate_eps(eps_current_year, eps_next_year):
    changing = eps_next_year / eps_current_year - 1

    if changing > 0.05: return 1
    if changing < -0.05: return -1
    return 0


def rate_performance(stock, index):
    performance = stock - index

    if performance > 0.05: return 1
    if performance < -0.05: return -1
    return 0


def rate_price_momentum(performance_6_month, performance_1_year):
    if performance_6_month == 1 and performance_1_year != 1: return 1
    if performance_6_month == -1 and performance_1_year != -1: return -1
    return 0


def rate_monthClosings(stockClosings, indexClosings):
    performance = 0

    for idx, stockClosing in enumerate(stockClosings):
        indexClosing = indexClosings[idx]

        if stockClosing > indexClosing:
            performance += 1
        if stockClosing < indexClosing:
            performance += -1

    if performance == len(stockClosings): return -1
    if performance * -1 == len(stockClosings): return 1
    return 0


def rate_ratings(ratings: AnalystRatings):
    count = ratings.count()
    sum = ratings.sum_weight()

    rating = round(sum / count, 1)

    if rating <= 1.5: return -1
    if rating >= 2.5: return 1
    return 0


def rate_small_ratings(ratings: AnalystRatings):
    count = ratings.count()
    sum = ratings.sum_weight()

    if count == 0:
        return 0

    rating = round(sum / count, 1)

    if rating <= 1.5: return 1
    if rating >= 2.5: return -1
    return 0