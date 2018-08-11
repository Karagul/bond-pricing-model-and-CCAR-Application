 # This whole model is rooted in a quarter base.

from scipy.optimize import fsolve
import pandas as pd


class Pricing_Model():
    def __init__(self, par=0, cpn_r=0, freq=0, T=0, M_p=0, c_f=[], f_r=0.0, B_d=[], B_c=[], S_d=[], S_c=[]):
        self.par = par
        self.cpn_r = cpn_r
        self.freq = freq
        self.T = T
        self.M_p = M_p  # market price
        self.c_f = c_f  # cash flow
        self.f_r = f_r  # funding rate
        self.B_d = B_d
        self.B_c = B_c
        self.S_d = S_d
        self.S_c = S_c

    def PV(self, C_F, Dis_Cur, Cre_Cur, F_R):
        T_d = []  # T_d means Total_discount rate curve
        for i in range(len(Dis_Cur)):
            T_d.append(Dis_Cur[i] + Cre_Cur[i] + F_R)
        PV = 0.0
        for i in range(len(C_F)):
            PV = PV + C_F[i] / pow((1 + T_d[i]), (float(i + 1) / 4))  # This requires that both the cash_flow list
        return PV  # and the T_d list are always expressed in quarter form.

    def CalculateFundingRate(self):
        def f(x):
            x = float(x)
            return [
                self.PV(self.c_f, self.B_d, self.B_c, x) - self.M_p
            ]

        self.f_r = fsolve(f, [0.2])
        # print("\nThe funding rate is %f" % (self.f_r))

    def CalculateModelPrice(self):
        result = 0.0
        result = self.PV(self.c_f, self.S_d, self.S_c, self.f_r)
        # print("\nBased on the shocked curves and funding rate, the new PV(model price) is: %f" % result)
        return result


class Loan():
    def __init__(self, Pri_M, par=0, cpn_r=0, freq=0, T=0, M_p=0, c_f=[], f_r=0.0, B_d=[], B_c=[], S_d=[], S_c=[]):
        self.Pri_M = Pri_M
        self.par = par
        self.cpn_r = cpn_r
        self.freq = freq
        self.T = T
        self.M_p = M_p  # market price
        self.c_f = c_f  # cash flow
        self.f_r = f_r  # funding rate
        self.B_d = B_d
        self.B_c = B_c
        self.S_d = S_d
        self.S_c = S_c

    def UpdateBasicBondInfo(self, Pri_M=0, par=0, cpn_r=0, freq=0, T=0, M_p=0):
        self.Pri_M = Pri_M
        self.par = par
        self.cpn_r = cpn_r
        self.freq = freq
        self.T = T
        self.M_p = M_p

    def UpdateShockedFromBasic(self, scenario_dis, scenario_cre):
        self.S_d = []  # set it to be NULL every time you reuse it.
        self.S_c = []
        for i in range(len(self.B_d)):
            self.S_d.append(self.B_d[i] * scenario_dis)
        for i in range(len(self.B_c)):
            self.S_c.append(self.B_c[i] * scenario_cre)

    def UpdateShockedForDV01(self):
        for i in range(len(self.S_d)):
            self.S_d[i] = self.S_d[i] - 0.0001

    def CreateFollowingCashFlow(self):
        coupon = (self.cpn_r / self.freq) * self.par
        redemption = coupon + self.par
        self.c_f = [0] * int(self.T * 4)
        for i in range(int(self.T * 4)):
            if (i % (4 / self.freq)) == 0:
                self.c_f[i] = coupon
        self.c_f[0] = redemption
        self.c_f.reverse()


def GeneratePortfolio():
    portfolio = []  # a list of "Loan" objects,each element is an object
    bondCollection = []  # a list of bond info,each element is a string recording the basic info of a single bond
    print("please input the information of a bond:")
    print("input by this pattern(separate by comma): [par,coupon_rate,coupon_frequency,T,market_price]")
    print("Note that:\ncoupon_frequency is the number of coupons issued per year(i.e. 0.5 for every 2 years,"
          "1 for annually,2 for semiannually,4 for quarterly).\nT can only be multiple of 0.25 (i.e. 2.75;9.25;7.5)."
          "\ncoupon_rate is annualized.\nAn example could be like: \" 100,0.1,2,1.75,90\",meaning that the par of "
          "this bond is 100, the annualized coupon rate is 10%,\nthe coupon is paid semiannually, the remaining "
          "life time of the bond is 1.75 years and the current market price of the bond is 90.")
    singleBond = str(input())
    bondCollection.append(singleBond)
    print("do you want to input one more bond? Y or N")
    kkk = str(input())
    while kkk == 'Y':
        print("please input the information of a bond(separate the info by comma) and please remember the rules above:")
        singleBond = str(input())
        bondCollection.append(singleBond)
        print("do you want to input one more bond? Y or N")
        kkk = str(input())
    basicDisCur = str(input("please input today's basic discount curve(separate by comma),the unit interval of the"
                            "\ncurve must be 1/4 year and you should provide a curve long enough to cover the longest"
                            "\nremaining life time of previous bonds:\nAn example would be like:\"0.05,0.06,0.07,0.05,"
                            "0.09,0.08,0.08,0.09,0.09\" for a discount curve of the following 2.25 years\n")).split(',')
    # it's a list of string now
    for i in range(len(basicDisCur)):
        basicDisCur[i] = float(basicDisCur[i])
    # it's now a list of float
    basicCreCur = str(input("\nplease input today's basic credit curve(separate by comma),the unit interval of the"
                            "\ncurve must be 1/4 year and you should provide a curve long enough to cover the longest"
                            "\nremaining life time of previous bonds:\n")).split(',')
    # it's a list of string now
    for i in range(len(basicCreCur)):
        basicCreCur[i] = float(basicCreCur[i])
    # it's now a list of float

    for i in range(len(bondCollection)):
        bondInfo = bondCollection[i].split(',')  # it's now a list of string
        for i in range(len(bondInfo)):
            bondInfo[i] = float(bondInfo[i])
        # it's now a list of float
        pri_model = Pricing_Model(par=bondInfo[0], cpn_r=bondInfo[1], freq=bondInfo[2], T=bondInfo[3], M_p=bondInfo[4],
                                  c_f=[], f_r=0.0, B_d=basicDisCur, B_c=basicCreCur, S_d=[], S_c=[])
        bond = Loan(Pri_M=pri_model, par=bondInfo[0], cpn_r=bondInfo[1], freq=bondInfo[2], T=bondInfo[3],
                    M_p=bondInfo[4], c_f=[], f_r=0.0, B_d=basicDisCur, B_c=basicCreCur, S_d=[], S_c=[])
        bond.CreateFollowingCashFlow()
        bond.Pri_M.c_f = bond.c_f
        bond.Pri_M.CalculateFundingRate()
        bond.Pri_M.f_r = float(bond.Pri_M.f_r)
        bond.f_r = bond.Pri_M.f_r
        portfolio.append(bond)
    print("The portfolio has now been constructed.\n")
    return portfolio


def main():
    portfolio = GeneratePortfolio()
    discountRateScenario = [1.00, 0.98, 0.95, 0.90, 0.80, 0.85, 0.90, 0.92, 0.93, 0.95]
    creditCurScenario = [1.0, 1.5, 2.8, 3.5, 3.0, 2.8, 2.4, 2.0, 1.5, 1.5]
    time = [0.00, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25]
    portfolioMarketValue = []
    DV01 = []
    PL = []

    sumModelPrice_lag = 0
    dv01 = 0

    for j in range(len(portfolio)):
        portfolio[j].UpdateShockedFromBasic(discountRateScenario[0], creditCurScenario[0])
        portfolio[j].Pri_M.S_d = portfolio[j].S_d
        portfolio[j].Pri_M.S_c = portfolio[j].S_c
        singlePV = portfolio[j].Pri_M.CalculateModelPrice()
        sumModelPrice_lag = sumModelPrice_lag + singlePV

        portfolio[j].UpdateShockedForDV01()
        portfolio[j].Pri_M.S_d = portfolio[j].S_d
        dv01 = dv01 + portfolio[j].Pri_M.CalculateModelPrice() - singlePV

    portfolioMarketValue.append(sumModelPrice_lag)
    DV01.append(dv01)
    PL.append(0)

    for i in range(1, len(creditCurScenario)):
        sumModelPrice_present = 0
        dv01 = 0
        sumCoupon = 0
        pl = 0

        for j in range(len(portfolio)):

            if len(portfolio[j].c_f) >= 1:
                sumCoupon = sumCoupon + portfolio[j].c_f.pop(0)
                portfolio[j].Pri_M.c_f = portfolio[j].c_f
            else:
                sumCoupon = sumCoupon + 0

            portfolio[j].UpdateShockedFromBasic(discountRateScenario[i], creditCurScenario[i])
            portfolio[j].Pri_M.S_d = portfolio[j].S_d
            portfolio[j].Pri_M.S_c = portfolio[j].S_c

            singlePV = portfolio[j].Pri_M.CalculateModelPrice()
            sumModelPrice_present = sumModelPrice_present + singlePV

            portfolio[j].UpdateShockedForDV01()
            portfolio[j].Pri_M.S_d = portfolio[j].S_d
            dv01 = dv01 + portfolio[j].Pri_M.CalculateModelPrice() - singlePV

        pl = sumModelPrice_present - sumModelPrice_lag + sumCoupon
        sumModelPrice_lag = sumModelPrice_present

        portfolioMarketValue.append(sumModelPrice_present)
        DV01.append(dv01)
        PL.append(pl)

    print("The analysis results are shown below：\nNote that the \'portfolio market price\' here means "
          "the price of the portfolio right after any payment of coupons or redemptions.\n")
    for i in range(len(time)):
        portfolioMarketValue[i] = round(portfolioMarketValue[i], 4)
        DV01[i] = round(DV01[i], 4)
        PL[i] = round(PL[i], 4)

    print("The portflio market price sequence is:")
    print(portfolioMarketValue)
    print("The DV01 sequence of the portfolio is:")
    print(DV01)
    print("The P&L sequence of the portfolio is:")
    print(PL)
    print("Below is a table with all the information mentioned above:\n")
    df = pd.DataFrame([time, portfolioMarketValue, DV01, PL],
                      index=['time(in years)', 'portfolioMarketValue', 'DV01', 'P&L'],
                     columns=['12/31/2017', '3/31/2018', '6/30/2018', '9/30/2018',
                               '12/31/2018', '3/31/2019', '6/30/2019', '9/30/2019',
                               '12/31/2019', '3/30/2020'])
    print(df)


main()