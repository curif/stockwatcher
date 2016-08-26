#!/usr/bin/env python
# encoding: utf-8

#from yahoo_finance import Share
import googlefinance
from config import config
#import pandas
import urwid
import urwid.raw_display
import urwid.web_display
from dateutil import parser

# use appropriate Screen class
if urwid.web_display.is_web_request():
    screen = urwid.web_display.Screen
else:
    screen = urwid.raw_display.Screen


def show_or_exit(key):
  if key in ('q', 'Q'):
    raise urwid.ExitMainLoop()


#frente, fondo:
palette = [
    ('default', 'white', 'black'),
    ('baja', 'light red', 'black'),
    ('alta', 'light green', 'black'),
    ('alert', 'white', 'dark blue'),
    ]


__author__ = 'curif50@gmail.com'

googlefinance.googleFinanceKeyToFullName = {
    u'id'     : u'ID',
    u't'      : u'StockSymbol',
    u'e'      : u'Index',
    u'l'      : u'LastTradePrice',
    u'l_cur'  : u'LastTradeWithCurrency',
    u'ltt'    : u'LastTradeTime',
    u'lt_dts' : u'LastTradeDateTime',
    u'lt'     : u'LastTradeDateTimeLong',
    u'div'    : u'Dividend',
    u'yld'    : u'Yield',
    u'c'      : u'Change',
    u'cp'      : u'ChangePercent',
}

quotesStorage = {}

title = urwid.Text("BCBA Watcher")
#title = urwid.BigText("BCBA Watcher", None)
#title.attrib.append(("rows", 3))

grid = urwid.Pile([])

# class myShare(Share):
#
#   def _fetch(self):
#       data = super(Share, self)._fetch()
#       #if data['LastTradeDate'] and data['LastTradeTime']:
#       #    data[u'LastTradeDateTimeUTC'] = edt_to_utc('{0} {1}'.format(data['LastTradeDate'], data['LastTradeTime']))
#       data[u'LastTradeDateTimeUTC'] = '{0} {1}'.format(data['LastTradeDate'], data['LastTradeTime'])
#       return data
#
#   def change_price(self, new_price):
#     self.data_set[u'LastTradePriceOnly'] = float(new_price)
#
#   def set_time(self, last_trade_time):
#     self.data_set[u'LastTradeTime'] = last_trade_time


def getTableQuotes():

  tableQuotes = []
  title = [urwid.Text("SYM"),
           urwid.Text("DIF"),
           urwid.Text("PRICE"),
           urwid.Text("TIME"),
           urwid.Text("ACTION"),
           urwid.Text("ALERT")]

  tableQuotes.append((urwid.GridFlow(title, 10, 1, 0, "left"), ("pack", None)))

  for s, q in sorted(quotesStorage.iteritems(), key=lambda q: q[1]["dif"], reverse=True):

    #http://www.jarloo.com/real-time-google-stock-api/
    dif = float(q["data"]["ChangePercent"])/ 100
    price = float(q["data"]["LastTradePrice"].replace(",", ""))
    fec = parser.parse(q["data"]["LastTradeTime"]).time().strftime("%H:%M")

    attr = "default"
    if dif>0:
      attr = "alta"
    elif dif<0:
      attr= "baja"

    action=""
    attrAction = "default"
    if "buyAt" in config["what2watch"][s]:
      if price <= config["what2watch"][s]["buyAt"]:
        action="BUY"
        attrAction="alta"

    if "sellAt" in config["what2watch"][s]:
      if price >= config["what2watch"][s]["sellAt"]:
        action="SELL"
        attrAction="baja"

    #http://urwid.org/reference/widget.html#urwid.GridFlow
    cells = [urwid.Text(s),
             urwid.Text((attr, "{:>+3.2%}".format(q["dif"]))),
             urwid.Text("{:>8.2f}".format(price)),
             urwid.Text("{}".format(fec)),
             urwid.Text((attrAction,action)),
             urwid.Text(("alert", "ALERT!" if q["dif"] > config["alert"] else ""))
             ]

    tableQuotes.append((urwid.GridFlow(cells, 10, 1, 0, "left"), ("pack", None)))

  return tableQuotes


def getQuotesWatched(loop, userData=None):
  global grid

  try:
    syms = map(lambda s: config["what2watch"][s]['g'], config["what2watch"].keys())
    quotes = googlefinance.getQuotes(syms)
  except Exception as e:
    print str(e)
  else:
    for q in quotes:
      stock_symbol_ = q["StockSymbol"]
      if stock_symbol_ not in quotesStorage:
        quotesStorage[stock_symbol_] = {"data": {}, "dif":0.}
      qSt = quotesStorage[stock_symbol_]
      qSt["data"] = q
      qSt["dif"] = float(q["ChangePercent"])/ 100

    #http://urwid.org/manual/widgets.html#container-widgets
    grid.contents = getTableQuotes()

  loop.set_alarm_in(config["sleep"]*60, getQuotesWatched)

# def getTableQuotesYHOO():
#
#   tableQuotes = []
#   title = [urwid.Text("GEN"),
#            urwid.Text("DIF"),
#            urwid.Text("OPEN"),
#            urwid.Text("PRICE"),
#            urwid.Text("DATE"),
#            urwid.Text("ALERT")]
#   tableQuotes.append((urwid.GridFlow(title, 10, 1, 0, "left"), ("pack",None)))
#
#   for s, q in sorted(quotesStorage.iteritems(), key=lambda q: q[1]["dif"], reverse=True):
#     first = float(q["data"].get_open() or 0)
#     last = float(q["data"].get_price() or 0)
#     dif = q["dif"]
#
#     attr = "default"
#     if dif>0:
#       attr = "alta"
#     elif dif<0:
#       attr= "baja"
#
#     alert = ""
#     if dif > config["alert"]:
#       alert = "ALERT!"
#
#     t = str(q["data"].data_set.get("LastTradeTime", "")) or ""
#
#     #http://urwid.org/reference/widget.html#urwid.GridFlow
#     cells = [urwid.Text(s),
#              urwid.Text((attr, "{:>+3.2%}".format(dif))),
#              urwid.Text("{:>8.2f}".format(first)),
#              urwid.Text("{:>8.2f}".format(last)),
#              urwid.Text(t),
#              urwid.Text(("alert", alert)),
#             ]
#     tableQuotes.append((urwid.GridFlow(cells, 10, 1, 0, "left"), ("pack", None)))
#
#   return tableQuotes
#
#
# def _getSymbolFromConfig(c, provider):
#   """
#   :param c: collection symbol description, ex: {"MIRG": {"g":"MIRG:BCBA", "y": "MIRG.BA"}
#   :param provider: "g" for google finance "y" for yahoo.
#   :return: provider's symbol: "MIRG:BCBA"
#   """
#   return c[c.keys()[0]]["g"]
#
#
# def getQuotesWatchedYHOO(loop, userData=None):
#
#   for sym, symCfg in config["what2watch"].iteritems():
#     try:
#         if sym not in quotesStorage:
#           quotesStorage[sym] = {"data": myShare(symCfg["y"]), "dif": 0.}
#         else:
#           quotesStorage[sym]["data"].refresh()
#     except Exception as e:
#       print sym + ": " + str(e)
#
#   #replace price with google's finance data.
#   syms = map(lambda s: config["what2watch"][s]['g'], config["what2watch"].keys())
#   try:
#     quotes = googlefinance.getQuotes(syms)
#   except Exception as e:
#     print str(e)
#   else:
#     for q in quotes:
#       sym = q["StockSymbol"]
#       if sym in quotesStorage:
#         quotesStorage[sym]["data"].change_price(q["LastTradePrice"].replace(",", ""))
#         quotesStorage[sym]["data"].set_time(q["LastTradeTime"])
#
#   #calc difference
#   for sym, q in quotesStorage.iteritems():
#     first = float(q["data"].get_open() or 0)
#     last = float(q["data"].get_price() or 0)
#     ser = pandas.Series([first, last])
#     q["dif"]=ser.pct_change()[1]
#
#   grid.contents = getTableQuotesYHOO()
#
#   loop.set_alarm_in(config["sleep"]*60, getQuotesWatchedYHOO)
#
#   return

def main():

  div = urwid.Divider("-")

  scr = urwid.Pile([title, div, grid])
  loop = urwid.MainLoop(urwid.Filler(scr, "top"),
                        unhandled_input=show_or_exit,
                        palette=palette)
  getQuotesWatched(loop, None)
  loop.run()


if '__main__'==__name__ or urwid.web_display.is_web_request():
  main()