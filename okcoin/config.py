"""
:short_ratio: each time short ratio
:long_total_ratio:: percent of money that every time long
:long_price_down_ratio:: price down ratio since last dead cross of EMA, only when reach this ratio then long
"""
url_cn = "www.okcoin.cn"
url_com = "www.okcoin.com"
log_path = "c:\logs"
signal_test_log_path = "c:\logs\stlogs"

config_3min = {
    "stop_profit_ratio": 0.025,
    "stop_loss_ratio": 0.045,
    "short_ratio": [0.2, 0.3, 0.5],
    "coin_most_hold_ratio": 0.35,
    "long_total_ratio": 0.3,
    "long_price_down_ratio": 0.025,
    "stop_loss_count_down": 1,
    "give_up_long_count_down": 2
}

config_5min = {
    "stop_profit_ratio": 0.04,
    "stop_loss_ratio": 0.045,
    "short_ratio": [0.2, 0.3, 0.5],
    "coin_most_hold_ratio": 0.3,
    "long_total_ratio": 0.3,
    "long_price_down_ratio": 0.03,
    "stop_loss_count_down": 1,
    "give_up_long_count_down": 2
}

eamcrosswithmacd_config_3min = {
    "stop_profit_ratio": 0.005,#basically, any time dead cross then short
    "stop_loss_ratio": 0.045,
    "short_ratio": [0.8, 1],
    "coin_most_hold_ratio": 0.3,
    "long_total_ratio": 0.2,
    "long_price_down_ratio": 0.025,
    "stop_loss_count_down": 1,
    "give_up_long_count_down": 2,
    "ema_quick_periods": 9,
    "ema_slow_periods": 21
}

eamcrosswithmacd_config_5min = {
    "stop_profit_ratio": 0.01,
    "stop_loss_ratio": 0.045,
    "short_ratio": [0.8, 1],
    "coin_most_hold_ratio": 0.3,
    "long_total_ratio": 0.2,
    "long_price_down_ratio": 0.025,
    "stop_loss_count_down": 1,
    "give_up_long_count_down": 2,
    "ema_quick_periods": 9,
    "ema_slow_periods": 21
}