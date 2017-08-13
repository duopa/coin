"""
:short_ratio: each time short ratio
:long_total_ratio:: percent of money that every time long
:long_price_down_ratio:: price down ratio since last dead cross of EMA, only when reach this ratio then long
"""
url_cn = "www.okcoin.cn"
url_com = "www.okcoin.com"

config_3min = {
    "stop_profit_ratio": 0.025,
    "stop_loss_ratio": 0.04,
    "short_ratio": 0.4,
    "coin_most_hold_ratio": 0.3,
    "long_total_ratio": 0.25,
    "long_price_down_ratio": 0.02,
    "stop_loss_count_down": 1,
    "give_up_long_count_down": 2
}

config_5min = {
    "stop_profit_ratio": 0.035,
    "stop_loss_ratio": 0.04,
    "short_ratio": 0.4,
    "coin_most_hold_ratio": 0.3,
    "long_total_ratio": 0.25,
    "long_price_down_ratio": 0.02,
    "stop_loss_count_down": 1,
    "give_up_long_count_down": 2
}
