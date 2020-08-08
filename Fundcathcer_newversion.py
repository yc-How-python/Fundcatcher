from bs4 import BeautifulSoup
from urllib.request import urlopen
from re import search
from PyQt5.QtGui import  QColor,QBrush,QDesktopServices
from PyQt5 import QtWidgets,QtCore
from PyQt5 import uic
from time import sleep
from numpy import array

from sys import argv,exit

class ThreadTable(QtCore.QThread):
    signalrefresh = QtCore.pyqtSignal(tuple)
    def __init__(self,window,codelist,moneylist,parent=None,*args,**kwargs):
        super(ThreadTable, self).__init__(parent,*args,**kwargs)
        self.window=window
        self.codelist=codelist
        self.moneylist=moneylist

    def loadling(self, code):
        #print(code)
        page = urlopen('http://fund.eastmoney.com/' + str(code) + '.html?spm=search').read().decode(
            'utf-8')
        soup = BeautifulSoup(page, features='lxml')
        return soup

    def name_extract(self, bs):
        bs_name = bs.find_all('div', {'style': "float: left"})  # div 中寻找 style="float: left"
        name = search(r'>.*?<', str(bs_name))
        return name[0].split('>')[1].split('<')[0]

    def estimated_value_extract(self, bs):
        bs_value = self.bs.find_all('span', {'id': "gz_gsz"})
        # <span class="ui-font-large ui-color-red ui-num" id="gz_gsz">1.0626</span>
        # span 中寻找 id = gz_gsz
        value = search(r'>.*?</span>', str(bs_value))
        return value[0].split('>')[1].split('<')[0]

    def delta_rate_extract(self, bs):
        bs_rate = bs.find_all('span', {'id': "gz_gszzl"})
        # [<span class="ui-font-middle ui-color-red ui-num" id="gz_gszzl">+1.70%</span>]
        rate = float(search(r'>.*?</span>', str(bs_rate))[0].split('>')[1].split('<')[0][:-1])
        return rate
    def run(self):

        while True:
            self.table_data_update()

            sleep(30)#每隔三秒钟发射一次
    def table_data_update(self):


        row = 0

        profitlist = []
        for each in self.codelist:
            codeItem = QtWidgets.QTableWidgetItem(str(each))

            soup = self.loadling(each.strip(' '))



            nameItem = QtWidgets.QTableWidgetItem(str(self.name_extract(soup)))


            money = self.moneylist[row]
            print(money)
            moneyItem = QtWidgets.QTableWidgetItem(str(money))






            rate = self.delta_rate_extract(soup)
            rateItem = QtWidgets.QTableWidgetItem(str(rate))


            profit = round(rate * 0.01 * float(money), 2)
            profitItem = QtWidgets.QTableWidgetItem(str(profit))

            self.signalrefresh.emit((row, 0, codeItem))
            self.signalrefresh.emit((row, 1, nameItem))
            self.signalrefresh.emit((row, 2, moneyItem))
            self.signalrefresh.emit((row, 3, rateItem))
            self.signalrefresh.emit((row, 4, profitItem))

            row += 1
            profitlist.append(profit)




        totalmoney = 0
        for each in self.moneylist:
            totalmoney += float(each)
        newItem = QtWidgets.QTableWidgetItem(str(totalmoney))

        self.signalrefresh.emit((row, 2, newItem))


        profitarray = array(profitlist)
        profit_total = profitarray.sum()
        print("盈利更新：",profit_total)

        newItem = QtWidgets.QTableWidgetItem(str(profit_total))
        self.signalrefresh.emit((row, 4, newItem))


class Fund_UI():





    def __init__(self):
        #加载ui文件
        #定义动态加载
        self.screenRect = QtWidgets.QApplication.desktop()
        self.window = uic.loadUi("fund_ui.UI")
        data = open('setup.in', 'r')
        funddata = data.readlines()
        codelist = []
        moneylist = []
        row=0

        for eachline in funddata[1:]:
            if eachline=='':
                continue
            code,money=eachline.strip().split('\t')
            codelist.append(code)


            moneylist.append(money)


            row+=1



        self.window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CustomizeWindowHint)

        self.loc()
        self.codelist=codelist
        self.moneylist=moneylist
        self.window.Table.setRowCount(len(codelist)+1)
        self.window.Table.setColumnCount(5)
        self.window.Table.setHorizontalHeaderLabels(['编号','基金',"总金",'增减率','盈亏'])
        self.totalrow = self.window.Table.rowCount()
        self.window.Table2.setRowCount(self.totalrow-1)
        self.window.Table2.setColumnCount(2)
        self.window.Table2.setHorizontalHeaderLabels(['编号', "总金"])
        for order in range(len(codelist)):

            newItem = QtWidgets.QTableWidgetItem(str(codelist[order]))
            self.window.Table2.setItem(order, 0, newItem)
            newItem = QtWidgets.QTableWidgetItem(str(moneylist[order]))
            self.window.Table2.setItem(order, 1, newItem)


        self.table_thread = ThreadTable(self.window,self.codelist,self.moneylist)
        self.table_thread.start()

        self.window.sumbit.clicked.connect(self.update_setup)
        self.window.setting.clicked.connect(self.table_resize)
        self.table_thread.signalrefresh.connect(self.ui_refresh)
        self.window.pushButton.clicked.connect(self.intro)
    def intro(self):
        QDesktopServices.openUrl(QtCore.QUrl('https://github.com/yc-How-python/Fundcatcher/blob/master/README.md'))
    def ui_refresh(self,tuplevar):
        i,j,var=tuplevar
        self.window.Table.setItem(i,j,var)
        if j==0:
            self.window.Table.item(i, 0).setForeground(QBrush(QColor(255, 0, 0)))
        elif j==4:
            if float(var.text()) >= 0:
                self.window.Table.item(i, 4).setForeground(QBrush(QColor(255, 0, 0)))
            else:
                self.window.Table.item(i, 4).setForeground(QBrush(QColor(100, 255, 140)))

    def table_resize(self):
        newrow=self.window.numberoffunds.value()
        self.window.Table2.setRowCount(newrow)
        self.window.Table.setRowCount(newrow+1)
    def update_setup(self):
        dataf=open('setup.in','w')
        dataf.write('#基金\t金额\n')
        self.codelist.clear()
        self.moneylist.clear()
        for row in range(self.window.Table2.rowCount()):
            code=self.window.Table2.item(row,0)
            code=str(code.text())
            money = self.window.Table2.item(row, 1)
            money = str(money.text())

            if len(self.codelist)<=row:
                self.codelist.append(code)
            else:
                self.codelist[row]=code

            if len(self.moneylist) <= row:
                self.moneylist.append(money)
            else:
                self.moneylist[row] = money
            dataf.write(code+'\t'+money+'\n')
        print(self.codelist)
        print(self.moneylist)

        dataf.close()
        self.table_thread.codelist=self.codelist
        self.table_thread.moneylist=self.moneylist








    def loc(self):
       self.window.move((self.screenRect.width()-self.window.width()), (self.screenRect.height()-self.window.height()-50))  # 利用move函数窗口
#[<div style="float: left">招商国证生物医药指数分级<span>(</span><span class="ui-num">161726</span></div>]
if __name__ == "__main__":

    app = QtWidgets.QApplication(argv)
    QtWidgets.QApplication.setStyle("Fusion")

    myapp = Fund_UI()
    myapp.window.show()
    exit(app.exec_())
