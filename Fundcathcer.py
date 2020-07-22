from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import requests
import matplotlib.pyplot as plt
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5 import QtWidgets,QtCore
import sys
from PyQt5 import uic
import threading
import time
import numpy as np


class Fund_UI():


    class fund_Thread(threading.Thread):

        def __init__(self,codelist,moneylist,window):
            threading.Thread.__init__(self)
            self.codelist=codelist
            self.moneylist=moneylist
            self.window=window
        def ui_data_update(self,totalrow):
            row = 0
            col = 0
            profitlist = []
            for each in self.codelist:
                newItem = QtWidgets.QTableWidgetItem(str(each))
                self.window.Table.setItem(row, 0, newItem)
                soup = self.loadling(each.strip(' '))

                newItem = QtWidgets.QTableWidgetItem(str(self.name_extract(soup)))
                self.window.Table.setItem(row, 1, newItem)

                money = self.moneylist[row]
                newItem = QtWidgets.QTableWidgetItem(str(money))
                self.window.Table.setItem(row, 2, newItem)

                self.window.setAttribute(QtCore.Qt.WA_TranslucentBackground)

                self.window.Table.item(0, 0).setForeground(QBrush(QColor(255, 0, 0)))

                rate = self.delta_rate_extract(soup)
                newItem = QtWidgets.QTableWidgetItem(str(rate))
                self.window.Table.setItem(row, 3, newItem)
                profit = rate * 0.01 * float(money)
                newItem = QtWidgets.QTableWidgetItem(str(profit))
                self.window.Table.setItem(row, 4, newItem)
                row += 1
                profitlist.append(profit)
            profitarray = np.array(profitlist)
            profit_total = profitarray.sum()
            print(profit_total, totalrow)
            newItem = QtWidgets.QTableWidgetItem(str(profit_total))
            self.window.Table.setItem(totalrow - 1, 4, newItem)

        def loadling(self, code):
            print(code)
            page = urlopen('http://fund.eastmoney.com/' + str(code) + '.html').read().decode(
                'utf-8')
            soup = BeautifulSoup(page, features='lxml')
            return soup

        def name_extract(self, bs):
            bs_name = bs.find_all('div', {'style': "float: left"})  # div 中寻找 style="float: left"
            name = re.search(r'>.*?<', str(bs_name))
            return name[0].split('>')[1].split('<')[0]

        def estimated_value_extract(self, bs):
            bs_value = self.bs.find_all('span', {'id': "gz_gsz"})
            # <span class="ui-font-large ui-color-red ui-num" id="gz_gsz">1.0626</span>
            # span 中寻找 id = gz_gsz
            value = re.search(r'>.*?</span>', str(bs_value))
            return value[0].split('>')[1].split('<')[0]

        def delta_rate_extract(self, bs):
            bs_rate = bs.find_all('span', {'id': "gz_gszzl"})
            # [<span class="ui-font-middle ui-color-red ui-num" id="gz_gszzl">+1.70%</span>]
            rate = float(re.search(r'>.*?</span>', str(bs_rate))[0].split('>')[1].split('<')[0][:-1])
            return rate
        def run(self):
            t1=time.time()
            totalrow=self.window.Table.rowCount()
            while 1:
                self.ui_data_update(totalrow)
                t2 = time.time()
                newItem = QtWidgets.QTableWidgetItem(str(t2))
                self.window.Table.setItem(totalrow - 1, 3, newItem)
                self.window.Table.viewport().update()
                time.sleep(60)

    def __init__(self):
        #加载ui文件
        #定义动态加载

        self.window = uic.loadUi("fund_ui.UI")
        data = open('setup.in', 'r')
        funddata = data.readlines()
        codelist = []
        moneylist = []
        for eachline in funddata[1:]:
            code,money=eachline.strip().split('\t')
            codelist.append(code)
            moneylist.append(money)
        self.codelist=codelist
        self.moneylist=moneylist
        self.window.Table.setRowCount(len(codelist)+1)
        self.window.Table.setColumnCount(5)
        self.window.Table.setHorizontalHeaderLabels(['编号','基金',"总金",'增减率','盈亏'])
        fT=self.fund_Thread(self.codelist,self.moneylist,self.window)
        fT.start()
#[<div style="float: left">招商国证生物医药指数分级<span>(</span><span class="ui-num">161726</span></div>]
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle("Fusion")

    myapp = Fund_UI()
    myapp.window.show()
    sys.exit(app.exec_())