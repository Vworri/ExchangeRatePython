import requests
import os
from bs4 import BeautifulSoup as bs
from money import  Money
import schedule
import time



class ExchangeRate:
    """Class to get rates and convert currency automatically"""
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"
    full_path = os.path.abspath("DailyRate.xml")
    
    @classmethod
    def worker(self):
        """If automation is needed. Collect the new file every dat when it is posted.
        Assuming CET timezone. I am not missing with timezones right now"""
        schedule.every().day.at("14:30").do(self.getDailyRates)
        while True:
            schedule.run_pending()
            time.sleep(1)


    @classmethod
    def getDailyRates(self):
        """manually get daily exchange rate xml"""
        rate_request = requests.get(self.url)
        with open(self.full_path, 'w') as daily_rate:
            data = rate_request.text
            daily_rate.write(data)
        return


    @classmethod
    def at(self, d, origin, destination):
        """get the exchange rate for a particular conversion"""
        origin = origin.upper()
        destination = destination.upper()
        res = {}
        res["origin"] = origin
        res["destination"] = destination
        if not os.path.isfile(self.full_path):
            self.getDailyRates()
        with open(self.full_path) as rates:
            data = bs(rates, 'lxml').cube.find_all('cube')
            try:
                origin_rate, destination_rate = zip(
                    *[(z.find(currency=origin), z.find(currency=destination)) for z in data if z.get("time") == d])
            except ValueError:
                d = self.max_minDate()["max"]
                origin_rate, destination_rate = zip(
                    *[(z.find(currency=origin), z.find(currency=destination)) for z in data if z.get("time") == d])
            res["rate"] = (float(destination_rate[0]["rate"]) / float(origin_rate[0]["rate"]))
            res["rateDate"] = d
            return res

    @classmethod
    def max_minDate(self):
        """get the exchange rate for a particular conversion"""
        res = {}
        if not os.path.isfile(self.full_path):
            self.getDailyRates()
        with open(self.full_path) as rates:
            data = bs(rates, 'lxml').cube.find_all('cube')
            dates = [z.get("time") for  z in data if z.get("time") is not None ]
            res["min"] = min(dates)
            res["max"] = max(dates)
            return res
        

    @staticmethod
    def exchangeCash(rate, amount, final_currency):
        """Administer an exchange"""
        val = rate * amount
        formmatted_value = Money(amount=val, currency=final_currency.upper()).format()
        return formmatted_value



if __name__ == '__main__':
    ExchangeRate.worker()