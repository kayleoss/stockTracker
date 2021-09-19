import tkinter as tk
from tkinter import Frame, font
from bs4 import BeautifulSoup
import requests
import threading


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.stockList = []

        txtfile = open("stocksfile.txt", "w")
        txtfile.close()

        with open("stocksfile.txt", "r") as stocksfile:
            for stock in stocksfile:
                stock.rstrip()
                self.stockList.append(stock)

        headingFont = font.Font(
            family="Helvetica", name="appHighlightFont", size=20, weight="bold"
        )
        self.label = tk.Label(
            text="Add stock symbol:",
            font=headingFont,
            pady=30,
        )
        self.label.pack()

        self.stockEntry = tk.Entry(width=100)
        self.stockEntry.pack()

        self.contents = tk.StringVar()
        self.contents.set("")

        self.stockEntry["textvariable"] = self.contents
        self.stockEntry.bind("<Key-Return>", self.addStock)

        self.searchBtn = tk.Button(text="Add Stock")
        self.searchBtn.bind("<Button-1>", self.addStock)
        self.searchBtn.pack()

        self.bottomFrame = Frame()
        self.bottomFrame.pack(side=tk.BOTTOM)

        self.refreshStocksData()

    def addStock(self, event):
        inputEntry = str(self.contents.get()).replace(" ", "")
        self.stockList.append(inputEntry)

        with open("stocksfile.txt", "a") as stocksfile:
            stocksfile.write(str(self.contents.get()) + "\n")

        self.getStockData(inputEntry)
        self.contents.set("")

    def getStockData(self, stock):
        stock_price = 0
        stock_change = 0
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }

        if len(stock.replace(" ", "")) > 1:
            stock_history = requests.get(
                "https://ca.finance.yahoo.com/quote/" + stock + "/history?p=" + stock,
                headers=headers,
                timeout=10,
            )
            stock_history_html = BeautifulSoup(stock_history.content, "html.parser")

            try:
                stock_price = float(
                    stock_history_html.select("#quote-header-info span.Trsdu\(0\.3s\)")[
                        0
                    ].get_text()
                )

                labelToAdd = stock + ": " + str(stock_price)
                tk.Label(
                    self.bottomFrame, text=labelToAdd.replace("\n", ""), pady=10
                ).pack()
            except:
                self.deleteStock(stock.replace("\n", ""))
                dangerFont = font.Font(family="Helvetica", size=16, weight="bold")
                errorMessage = tk.Label(
                    text="Could not find the stock: " + stock,
                    pady=5,
                    fg="red",
                    font=dangerFont,
                )
                errorMessage.pack(side=tk.TOP)
                errorMessage.after(5000, errorMessage.destroy)

    def refreshStocksData(self):
        # refresh stock data every 30 seconds
        threading.Timer(30.0, self.refreshStocksData).start()

        if len(self.stockList):
            print("Refreshing stock data")
            for widget in self.bottomFrame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.destroy()

            for stock in self.stockList:
                self.getStockData(stock)

    def deleteStock(self, stock):
        self.stockList.remove(stock.rstrip())
        lines = []
        with open("stocksfile.txt", "r") as stocksfile:
            lines = stocksfile.readlines()

        with open("stocksfile.txt", "w") as stocksfile:
            for line in lines:
                if stock.replace("\n", "") not in line:
                    stocksfile.write(line)
            stocksfile.close()


root = tk.Tk()
root.geometry("980x981")
myapp = App(root)
myapp.master.title("stockTracker")
myapp.mainloop()
