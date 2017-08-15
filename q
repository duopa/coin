[1mdiff --git a/strategy/macd.py b/strategy/macd.py[m
[1mindex d746e1d..7201937 100644[m
[1m--- a/strategy/macd.py[m
[1m+++ b/strategy/macd.py[m
[36m@@ -256,7 +256,7 @@[m [mclass MacdStrategy:[m
         else:[m
             return False[m
     #-----------------------------------------------------------------------------------------------[m
[31m-    def _is_long_price_under_highest_price_percent(self, kline, long_price, percent=0.01):[m
[32m+[m[32m    def _is_long_price_under_highest_price_percent(self, kline, long_price):[m
         '''[m
         : avoid long at first time price down from latest top price[m
         '''[m
[36m@@ -272,9 +272,9 @@[m [mclass MacdStrategy:[m
         :而非 17:05的23372.5[m
         '''[m
         distance = klen - highest_index - (klen_amend - highest_index_amend)[m
[31m-        if highest_price > highest_price_amend and abs(distance) >= 26:    [m
[32m+[m[32m        if highest_price > highest_price_amend and abs(distance) >= 26:[m
             '''[m
[31m-            :if difference between the two highest less than 0.005%, [m
[32m+[m[32m            :if difference between the two highest less than 0.005%,[m
             :and they far enough(26 periods?), then amend highest_index[m
             :--------------H-------------------------------a-----------------------klen[m
             :                                     ---------h-----------------------klen_amend[m
[36m@@ -283,14 +283,15 @@[m [mclass MacdStrategy:[m
             if highest_price_amend >= (highest_price * 0.995):[m
                 highest_index = klen - (klen_amend - highest_index_amend)[m
         #:if highest price far enough[m
[31m-        if klen - highest_index > 35:# 26 + 9?[m
[32m+[m[32m        if klen - highest_index > 21:# 12 + 9?[m
             #当long_price >= highest_price时,认为是在创新高,买入[m
             if long_price >= highest_price:[m
                 return True[m
                 #: return True run into problem: reason: ltc 3min long at 2017-08-08 13:48:24[m
                 #return False[m
             else:[m
[31m-                diff = highest_price * (1-percent)[m
[32m+[m[32m                percent = self._config["long_price_down_ratio"][m
[32m+[m[32m                diff = highest_price * (1 - percent)[m
                 if long_price <= diff:[m
                     return True[m
                 else:[m
