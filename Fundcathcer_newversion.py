from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

from PyQt5.QtGui import  QColor, QBrush
from PyQt5 import QtWidgets,QtCore

from PyQt5 import uic
import threading
from time import sleep
import numpy as np
import sys

class ThreadTable(QtCore.QThread):
    update_date = QtCore.pyqtSignal()

    def __init__(self,parent=None,*args,**kwargs):
        super(ThreadTable, self).__init__(parent,*args,**kwargs)

    def run(self):

        while True:
            self.update_date.emit()  # 发射信号
            sleep(30)#每隔三秒钟发射一次

class Fund_UI():



    def ui_data_update(self):
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

            self.window.Table.item(row, 0).setForeground(QBrush(QColor(255, 0, 0)))

            rate = self.delta_rate_extract(soup)
            newItem = QtWidgets.QTableWidgetItem(str(rate))
            self.window.Table.setItem(row, 3, newItem)
            profit =    round(rate * 0.01 * float(money),2)
            newItem = QtWidgets.QTableWidgetItem(str(profit))
            self.window.Table.setItem(row, 4, newItem)
            if profit >=0:
                self.window.Table.item(row, 4).setForeground(QBrush(QColor(255, 0, 0)))
            else:
                self.window.Table.item(row, 4).setForeground(QBrush(QColor(100, 255, 140)))
            row += 1
            profitlist.append(profit)

        profitarray = np.array(profitlist)
        profit_total = profitarray.sum()
        print(profit_total, self.totalrow)
        newItem = QtWidgets.QTableWidgetItem(str(round(profit_total,2)))
        self.window.Table.setItem(self.totalrow - 1, 4, newItem)
        if profit_total >= 0:
            self.window.Table.item(self.totalrow - 1, 4).setForeground(QBrush(QColor(255, 0, 0)))
        else:
            self.window.Table.item(self.totalrow - 1, 4).setForeground(QBrush(QColor(100, 255, 140)))


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
 1-
    def delta_rate_extract(self, bs):
        bs_rate = bs.find_all('span', {'id': "gz_gszzl"})
        # [<span class="ui-font-middle ui-color-red ui-num" id="gz_gszzl">+1.70%</span>]
        rate = float(re.search(r'>.*?</span>', str(bs_rate))[0].split('>')[1].split('<')[0][:-1])
        return rate
    def run(self):

        totalrow=self.window.Table.rowCount()
        while 1:
            self.ui_data_update(totalrow)

            QtWidgets.QApplication.processEvents()

            sleep(60)

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
        self.window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CustomizeWindowHint)

        self.loc()
        self.codelist=codelist
        self.moneylist=moneylist
        self.window.Table.setRowCount(len(codelist)+1)
        self.window.Table.setColumnCount(5)
        self.window.Table.setHorizontalHeaderLabels(['编号','基金',"总金",'增减率','盈亏'])
        self.totalrow = self.window.Table.rowCount()


        self.table_thread = ThreadTable()
        self.table_thread.start()
        self.table_thread.update_date.connect(self.table_data_update)

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
    def table_data_update(self):


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

            self.window.Table.item(row, 0).setForeground(QBrush(QColor(255, 0, 0)))

            rate = self.delta_rate_extract(soup)
            newItem = QtWidgets.QTableWidgetItem(str(rate))
            self.window.Table.setItem(row, 3, newItem)
            profit = round(rate * 0.01 * float(money), 2)
            newItem = QtWidgets.QTableWidgetItem(str(profit))
            self.window.Table.setItem(row, 4, newItem)
            if profit >= 0:
                self.window.Table.item(row, 4).setForeground(QBrush(QColor(255, 0, 0)))
            else:
                self.window.Table.item(row, 4).setForeground(QBrush(QColor(100, 255, 140)))
            row += 1
            profitlist.append(profit)

        profitarray = np.array(profitlist)
        profit_total = profitarray.sum()
        print(profit_total, self.totalrow)
        newItem = QtWidgets.QTableWidgetItem(str(profit_total))

        self.window.Table.setItem(self.totalrow - 1, 4, newItem)


    def loc(self):
       self.window.move((1920-self.window.width()), (1080-self.window.height()-50))  # 利用move函数窗口
#[<div style="float: left">招商国证生物医药指数分级<span>(</span><span class="ui-num">161726</span></div>]
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle("Fusion")

    myapp = Fund_UI()
    myapp.window.show()
    sys.exit(app.exec_())