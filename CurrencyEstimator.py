"""
 An offline approximate currency lookup table.
 Used to approximate the sale and budget information for movies.

 Most exchange rates extracted using openexchangerates package on July 13, 2016
 using the following code:

    # first time usage
    from openexchangerates.exchange import Exchange
    app_id = "59354a7e650e4edab76ec7cc20f9ca74"
    local_dir = "~/.openexchangerates"
    exchange = Exchange(local_dir, app_id)

    # After first time usage:
    from openexchangerates.exchange import Exchange
    exchange = Exchange()
    xg = exchange.rates()

 Exchange rates for obsolete currencies are manually added from
    http://coinmill.com/USD_TRL.html?USD=1
"""

__author__ = "Hamid Younesy"
__copyright__ = "Copyright 2016"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Hamid Younesy"


# an offline approximate currency convertor
class CurrencyEstimator:
    currencies = {  'USD': 1, 'DZD': 110.35122, 'NAD': 14.40709, 'GHS': 3.946445, 'EGP': 8.878225, 'BGN': 1.7621, 'PAB': 1,
                    'PHP': 47.23008, 'BOB': 6.866232, 'DKK': 6.698861, 'BWP': 10.770925, 'LBP': 1510.043333,
                    'TZS': 2188.36, 'VND': 22310.933333, 'AOA': 165.565833, 'KHR': 4078.0225, 'QAR': 3.641597,
                    'KYD': 0.82438, 'LYD': 1.385223, 'UAH': 24.78282, 'JOD': 0.708132, 'AWG': 1.793333,
                    'SAR': 3.750409, 'XPT': 0.0009, 'HKD': 7.756498, 'EUR': 0.90005, 'CHF': 0.983025, 'GIP': 0.759963,
                    'BYR': 20026.25, 'XPF': 107.562375, 'XPD': 0.0017, 'BYN': 1.9998, 'MRO': 354.548167,
                    'HRK': 6.738676, 'DJF': 177.0925, 'THB': 35.18589, 'XAF': 592.61702, 'BND': 1.346713, 'ETB': 22.00023,
                    'UY': 30.36919, 'NIO': 28.54047, 'LAK': 8075.4175, 'SYP': 216.086667, 'MAD': 9.789585, 'MZN': 65.65,
                    'YER': 250.009, 'ZAR': 14.45476, 'NPR': 107.2698, 'ZWL': 322.387236, 'NGN': 282.7883,
                    'CRC': 546.748, 'AED': 3.672965, 'EEK': 14.10235, 'MWK': 714.1961, 'TTD': 6.660011, 'LKR': 145.9234,
                    'PKR': 104.8037, 'HUF': 282.7538, 'BMD': 1, 'LSL': 14.43109, 'MNT': 2011.5, 'AMD': 476.48,
                    'UGX': 3373.17, 'XDR': 0.718414, 'JMD': 126.4777, 'GEL': 2.34754, 'SHP': 0.759963,
                    'AFN': 68.59, 'MMK': 1177.475, 'KPW': 899.91, 'TRY': 2.899136, 'BDT': 78.39992, 'CNY': 6.687002,
                    'HTG': 63.22425, 'SLL': 5512.5, 'MGA': 3083.595, 'ANG': 1.783775, 'LRD': 90.25,
                    'RWF': 754.015875, 'NOK': 8.418847, 'MOP': 7.98973, 'INR': 67.03183, 'MXN': 18.37789, 'CZK': 24.34203,
                    'TJS': 7.8677, 'BTC': 0.001506557843, 'BTN': 67.0891, 'COP': 2927.315, 'MYR': 3.967416, 'TMT': 3.4682,
                    'MUR': 35.397988, 'IDR': 13096.1, 'HNL': 22.77943, 'FJD': 2.045717,
                    'ISK': 122.0874, 'PEN': 3.279996, 'BZD': 2.00257, 'ILS': 3.862092, 'DOP': 45.89093, 'GGP': 0.759963,
                    'MDL': 19.77584, 'BSD': 1, 'SEK': 8.487254, 'ZMK': 5221.025, 'JEP': 0.759963,
                    'AUD': 1.313688, 'SRD': 7.0525, 'CUP': 24.728383, 'CLF': 0.024898, 'BBD': 2, 'KMF': 431.375,
                    'KRW': 1146.24, 'GMD': 42.71614, 'VEF': 9.9785, 'IMP': 0.759963, 'CUC': 1, 'CLP': 656.8257,
                    'ZMW': 10.25155, 'LTL': 3.080136, 'ALL': 123.162, 'XCD': 2.70302, 'KZT': 338.155, 'RUB': 63.89577,
                    'XAG': 0.04904, 'CDF': 946.2525, 'RON': 4.043564, 'OMR': 0.384977, 'BRL': 3.284223,
                    'SBD': 7.90339, 'PLN': 3.969962, 'PYG': 5582.961667, 'KES': 101.28279, 'MKD': 55.42093,
                    'GBP': 0.759963, 'AZN': 1.556825, 'TOP': 2.2437, 'MVR': 15.156667, 'VUV': 107.1, 'GNF': 9025.69,
                    'WST': 2.513833, 'IQD': 1169.58303, 'ERN': 15.25, 'BAM': 1.762514, 'SCR': 13.05092,
                    'CAD': 1.298368, 'CVE': 99.621633, 'KWD': 0.302026, 'BIF': 1661.8575, 'PGK': 3.16225, 'SOS': 573.0905,
                    'TWD': 32.1565, 'SGD': 1.347199, 'UZS': 2957.5, 'STD': 22149.05, 'IRR': 30092.5, 'SVC': 8.743546,
                    'XOF': 595.55702, 'TND': 2.200574, 'GYD': 204.987667, 'MTL': 0.683738, 'NZD': 1.374213,
                    'FKP': 0.759963, 'LVL': 0.629127, 'KGS': 67.26545, 'ARS': 14.58535, 'SZL': 14.41707,
                    'GTQ': 7.618543, 'RSD': 111.12494, 'BHD': 0.377338, 'JPY': 104.2072, 'SDG': 6.083895, 'XA': 0.00074,
                     # obsolete currencies. manually added from: http://coinmill.com/USD_TRL.html?USD=1
                    'RUR': 64100, 'TRL': 2895000, 'PTE': 181.05, 'DEM': 1.77, 'ITL': 1749,
                    'AZM': 7890, 'SIT': 216.4, 'BEF': 36.5, 'YUM': 2.0, 'LUF': 36.5,
                    'GHC': 39582.8, 'TMM': 17514, 'SKK': 27.0, 'CYP': 0.53, 'ROL': 40819.72,
                    'NLG': 2.0, 'ZWD': 92233720368547760.00, 'FRF': 5.92, 'VEB': 9975,
                    'ESP': 150, 'IEP': 0.71, 'XAU': 0.001, 'BGL': 1770, 'AFA': 68683,
                    'GRD': 308.0, 'FIM': 5, 'UYU': 30.0, 'MGF': 15850, 'ATS': 12, 'SDD': 644.91
                }
    @classmethod
    def exchange(cls, value, from_currency, to_currency = 'USD'):
        from_rate = cls.currencies.get(from_currency, 0)
        to_rate = cls.currencies.get(to_currency, 0)
        if from_rate == 0 or to_rate == 0:
            return None
        return value * to_rate / from_rate

if __name__ == '__main__':
    print("100 CAD = " + str(round(CurrencyEstimator.exchange(100, 'CAD', 'EUR'),2)) + " EUR")
