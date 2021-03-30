tsla = yf.Ticker('')
history = tsla.history(period='1d')

print(tsla.info)