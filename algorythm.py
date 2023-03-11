from scipy.stats import spearmanr

def correlation(prices_lists: list):
    list_1 = prices_lists[0]
    list_2 = prices_lists[1]
    len_1 = len(list_1)
    len_2 = len(list_2)
    len_list = 0 - min(len_1, len_2)
    if len(list_1) > 0 and len(list_2) > 0:
        corr, p_value = spearmanr(list_1[len_list:], list_2[len_list:])
        return corr


def get_self_price(corr, current_price, previous_price):
    if corr:
        price_change = (current_price - previous_price)/previous_price
        self_price = current_price - (price_change * corr)
        return self_price