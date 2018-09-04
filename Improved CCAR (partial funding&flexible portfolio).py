#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This whole model is rooted in a quarter base.

from scipy.optimize import fsolve
import pandas as pd


class Pricing_Model():
    def __init__(self, par=0, cpn_r=0, freq=0, T=0, M_p=0, ini_ff=1, faci_fee=0.1, ffchain=[], 
                 nominal_c_f=[], real_c_f=[], f_r=0.0, B_d=[], B_c=[], S_d=[], S_c=[]):
        self.par = par
        self.cpn_r = cpn_r
        self.freq = freq
        self.T = T
        self.M_p = M_p                  # market price
        self.ini_ff = ini_ff            # initial funding factor
        self.ffchain = ffchain          # funding factor chain
        self.faci_fee = faci_fee        # facility fee
        self.nominal_c_f = nominal_c_f  # nominal cash flow. Nominal cash flow means the original cash flow 
                                        # regardless of the partially funding issue, namely, it's the cash  
                                        # flow if the bond is fully funded in the first place.
        self.real_c_f = real_c_f        # real cash flow. Real cash flow is the cash flow in the consideration 
                                        # of partial funding factor.
        self.f_r = f_r                  # funding rate
        self.B_d = B_d
        self.B_c = B_c
        self.S_d = S_d
        self.S_c = S_c

    def PV(self, C_F, Dis_Cur, Cre_Cur, F_R):
        T_d = []  # T_d means Total_discount rate curve,namely basic_discount_curve+basic_credit_curve
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
                self.PV(self.nominal_c_f, self.B_d, self.B_c, x) - self.M_p
            ]

        self.f_r = fsolve(f, [0.2])
        # print("\nThe funding rate is %f" % (self.f_r))

    def CalculateModelPrice(self,ff):
        result = 0.0
        result = self.PV(self.nominal_c_f, self.S_d, self.S_c, self.f_r)
        result = result*ff-(result-self.par)*(1-ff)
        #print("\nBased on the shocked curves, current funding factor and funding rate, the new PV(model price) is: %f" % result)
        return result


class Loan():
    def __init__(self, Pri_M, par=0, cpn_r=0, freq=0, T=0, M_p=0, ini_ff=1, faci_fee=0.1, ffchain=[], 
                 nominal_c_f=[], real_c_f=[], f_r=0.0, B_d=[], B_c=[], S_d=[], S_c=[]):
        self.Pri_M = Pri_M
        self.par = par
        self.cpn_r = cpn_r
        self.freq = freq
        self.T = T
        self.M_p = M_p                  # market price
        self.ini_ff = ini_ff            # initial funding factor
        self.ffchain = ffchain          # funding factor chain
        self.faci_fee = faci_fee        # facility fee
        self.nominal_c_f = nominal_c_f  # nominal cash flow
        self.real_c_f = real_c_f        # real cash flow
        self.f_r = f_r                  # funding rate
        self.B_d = B_d
        self.B_c = B_c
        self.S_d = S_d
        self.S_c = S_c

    def UpdateBasicBondInfo(self, Pri_M=0, par=0, cpn_r=0, freq=0, T=0, M_p=0, ini_ff=1, faci_fee=0.1):
        self.Pri_M = Pri_M
        self.par = par
        self.cpn_r = cpn_r
        self.freq = freq
        self.T = T
        self.M_p = M_p
        self.ini_ff = ini_ff
        self.faci_fee = faci_fee
        

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

    def CreateNominalCashFlow(self): #this is to generate the original cash flow assuming a 100% funding rate
        coupon = (self.cpn_r / self.freq) * self.par
        redemption = coupon + self.par
        self.nominal_c_f = [0] * int(self.T * 4)
        for i in range(int(self.T * 4)):
            if (i % (4 / self.freq)) == 0:
                self.nominal_c_f[i] = coupon
        self.nominal_c_f[0] = redemption
        self.nominal_c_f.reverse()
    
    def CreateFundingFactorChain(self):
        self.ffchain=[0]*int(len(self.nominal_c_f))
        for i in range(len(self.ffchain)):
            self.ffchain[i]=float(self.ini_ff+(i+1)*(1-self.ini_ff)/(self.T*4))
            self.ffchain[i]=round(self.ffchain[i],4)
            
    def CreateRealCashFlow(self):
        self.real_c_f=[0]*int(len(self.nominal_c_f))
        for i in range(len(self.real_c_f)):
            self.real_c_f[i]=self.nominal_c_f[i]*self.ffchain[i]+self.nominal_c_f[i]*(1-self.ffchain[i])*self.faci_fee
            self.real_c_f[i]=round(self.real_c_f[i],4)
            
"""
Actually in this model, there is a problem, which is that in the function of the coupon calculation: C*FF+facilityRate*(1-FF)
the FF should be the funding factor of last time spot instead of the current time spot.
"""
            

def GeneratePortfolio():
    portfolio = []  # a list of "Loan" objects,each element is an object
    bondCollection = []  # a list of bond info,each element is a string recording the basic info of a single bond
    print("please input the information of a bond first.")
    print("input by this pattern(separate by comma): \n[par,coupon_rate,coupon_frequency,T,market_price,"
          "\ninitial_funding_rate,facility_fee]")
    print("Note that:\ncoupon_frequency is the number of coupons issued per year\n(i.e. 0.5 for every 2 years,"
          "1 for annually,2 for semiannually,\n4 for quarterly).T is the remaining life time of the bond and \n"
          "can only be multiple of 0.25 (i.e. 2.75;9.25;7.5).coupon_rate\nis annualized.\nAn example could be like:\n"
          "\"100,0.1,2,1.75,90,0.3,0.1\",meaning that the par of this bond\nis 100, the annualized coupon rate"
          "is 10%,the coupon is paid\nsemiannually, the remaining life time of the bond is 1.75 years,\nthe "
          "current market price of the bond is 90, the initial funding \nrate when the bond is add to the "
          "portfolio is 0.3 and the facility\nfee is 0.1.")
    print("please input here:\n")
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
        
    basicDisCur = str(input("please input today's basic discount curve(separate by comma),the\nunit interval of the"
                            "curve must be 1/4 year and you should provide\na curve long enough to cover the longest "
                            "remaining life time of\nprevious bonds.\nAn example would be like:\n\"0.05,0.06,0.07,0.05,"
                            "0.09,0.08,0.08,0.09,0.09\" for a discount \ncurve of the following 2.25 years\n")).split(',')
    # it's a list of string now
    for i in range(len(basicDisCur)):
        basicDisCur[i] = float(basicDisCur[i])
    # it's now a list of float
    basicCreCur = str(input("\nplease input today's basic credit curve(separate by comma),the\nunit interval of the"
                            "curve must be 1/4 year and you should\nprovide a curve long enough to cover the longest"
                            "remaining life\ntime of previous bonds:\n")).split(',')
    # it's a list of string now
    for i in range(len(basicCreCur)):
        basicCreCur[i] = float(basicCreCur[i])
    # it's now a list of float


    for i in range(len(bondCollection)):
        bondInfo = bondCollection[i].split(',')  # it's now a list of string
        for i in range(len(bondInfo)):
            bondInfo[i] = float(bondInfo[i])
        # it's now a list of float
        pri_model = Pricing_Model(par=bondInfo[0], cpn_r=bondInfo[1], freq=bondInfo[2], T=bondInfo[3], 
                                  M_p=bondInfo[4], ini_ff=bondInfo[5], faci_fee=bondInfo[6], ffchain=[], 
                                  nominal_c_f=[],real_c_f=[], f_r=0.0, B_d=basicDisCur, B_c=basicCreCur, 
                                  S_d=[], S_c=[])
        
        bond = Loan(Pri_M=pri_model, par=bondInfo[0], cpn_r=bondInfo[1], freq=bondInfo[2], T=bondInfo[3],
                    M_p=bondInfo[4], ini_ff=bondInfo[5], faci_fee=bondInfo[6], ffchain=[], nominal_c_f=[],
                    real_c_f=[], f_r=0.0, B_d=basicDisCur, B_c=basicCreCur, S_d=[], S_c=[])
        
        bond.CreateNominalCashFlow()
        bond.Pri_M.nominal_c_f = bond.nominal_c_f  # So far, the nominal cash flow has been generated
        bond.Pri_M.CalculateFundingRate()
        bond.f_r = float(bond.Pri_M.f_r)           # So far, the funding rate has been generated
        bond.CreateFundingFactorChain()
        bond.Pri_M.ffchain=bond.ffchain            # So far, the funding factor chain has been generated
        bond.CreateRealCashFlow()
        bond.Pri_M.real_c_f=bond.real_c_f          # So far, the real cash flow has been generated.
        
        portfolio.append(bond) # as we can see, the "portfolio" is a list of "bond class object"
        
        result=[portfolio,basicDisCur,basicCreCur]
    print("The portfolio has now been constructed.\n")
    return result

def GenerateNewPortfolio(ba_d,ba_c):
    Newportfolio=[]
    NewbondCollection = [] 
    print("please input the information of a new bond here:")
    NewsingleBond = str(input())
    NewbondCollection.append(NewsingleBond)
    print("do you want to input one more bond? Y or N")
    kkk = str(input())
    while kkk == 'Y':
        print("please input the information of a new bond:")
        NewsingleBond = str(input())
        NewbondCollection.append(NewsingleBond)
        print("do you want to input one more bond? Y or N")
        kkk = str(input())
    
    for i in range(len(NewbondCollection)):
        NewbondInfo = NewbondCollection[i].split(',')  # it's now a list of string
        for i in range(len(NewbondInfo)):
            NewbondInfo[i] = float(NewbondInfo[i])
     
        pri_model = Pricing_Model(par=NewbondInfo[0], cpn_r=NewbondInfo[1], freq=NewbondInfo[2], T=NewbondInfo[3], 
                              M_p=NewbondInfo[4], ini_ff=NewbondInfo[5], faci_fee=NewbondInfo[6], ffchain=[], 
                              nominal_c_f=[],real_c_f=[], f_r=0.0, B_d=ba_d, B_c=ba_c, S_d=[], S_c=[])
    
        bond = Loan(Pri_M=pri_model, par=NewbondInfo[0], cpn_r=NewbondInfo[1], freq=NewbondInfo[2], T=NewbondInfo[3],
                    M_p=NewbondInfo[4], ini_ff=NewbondInfo[5], faci_fee=NewbondInfo[6], ffchain=[], nominal_c_f=[],
                    real_c_f=[], f_r=0.0, B_d=ba_d, B_c=ba_c, S_d=[], S_c=[])
        
        bond.CreateNominalCashFlow()
        bond.Pri_M.nominal_c_f = bond.nominal_c_f  # So far, the nominal cash flow has been generated
        bond.Pri_M.CalculateFundingRate()
        bond.f_r = float(bond.Pri_M.f_r)           # So far, the funding rate has been generated
        bond.CreateFundingFactorChain()
        bond.Pri_M.ffchain=bond.ffchain            # So far, the funding factor chain has been generated
        bond.CreateRealCashFlow()
        bond.Pri_M.real_c_f=bond.real_c_f          # So far, the real cash flow has been generated.
        Newportfolio.append(bond) # as we can see, the "portfolio" is a list of "bond class object"
    return Newportfolio 
        

def main():
    X=GeneratePortfolio()
    portfolio = X[0]
    BASIC_D=X[1]
    BASIC_C=X[2]
    
    discountRateScenario = [1.00, 0.98, 0.95, 0.90, 0.80, 0.85, 0.90, 0.92, 0.93, 0.95]
    creditCurScenario = [1.0, 1.5, 2.8, 3.5, 3.0, 2.8, 2.4, 2.0, 1.5, 1.5]
    time = [0.00, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25]
    portfolioMarketValue = []
    DV01 = []
    PL = []

    sumModelPrice_lag = 0.0
    dv01 = 0.0
    
    for j in range(len(portfolio)):
        portfolio[j].UpdateShockedFromBasic(discountRateScenario[0], creditCurScenario[0])
        portfolio[j].Pri_M.S_d = portfolio[j].S_d
        portfolio[j].Pri_M.S_c = portfolio[j].S_c
        singlePV = float(portfolio[j].Pri_M.CalculateModelPrice(ff=portfolio[j].Pri_M.ini_ff))
        sumModelPrice_lag = sumModelPrice_lag + singlePV
        
        portfolio[j].UpdateShockedForDV01()
        portfolio[j].Pri_M.S_d = portfolio[j].S_d
        dv01 = dv01 + float(portfolio[j].Pri_M.CalculateModelPrice(ff=portfolio[j].Pri_M.ini_ff)) - float(singlePV)
     
    portfolioMarketValue.append(sumModelPrice_lag)
    DV01.append(dv01)
    PL.append(0.0)
    

    for i in range(1, len(creditCurScenario)):
        sumModelPrice_present = 0.0
        dv01 = 0.0
        sumCoupon = 0.0
        pl = 0.0
       
        for j in range(len(portfolio)):
            
            if len(portfolio[j].real_c_f)==len(portfolio[j].nominal_c_f):
                if len(portfolio[j].real_c_f) >= 1:
                    sumCoupon = sumCoupon + portfolio[j].real_c_f.pop(0)
                    portfolio[j].Pri_M.real_c_f = portfolio[j].real_c_f
                    portfolio[j].nominal_c_f.pop(0)
                    portfolio[j].Pri_M.nominal_c_f = portfolio[j].nominal_c_f
                    
                else:
                    sumCoupon = sumCoupon + 0.0
            else:
                print("ERROR! The length of the nominal_c_f doesn't equal to the length of real_c_f\n")
                
            if len(portfolio[j].ffchain)>=1:
                portfolio[j].UpdateShockedFromBasic(discountRateScenario[i], creditCurScenario[i])
                portfolio[j].Pri_M.S_d = portfolio[j].S_d
                portfolio[j].Pri_M.S_c = portfolio[j].S_c
                singlePV = float(portfolio[j].Pri_M.CalculateModelPrice(ff=portfolio[j].Pri_M.ffchain[0]))
                sumModelPrice_present = float(sumModelPrice_present) + float(singlePV)
                
                portfolio[j].UpdateShockedForDV01()
                portfolio[j].Pri_M.S_d = portfolio[j].S_d
                dv01 = dv01 + float(portfolio[j].Pri_M.CalculateModelPrice(ff=portfolio[j].Pri_M.ffchain[0])) - float(singlePV)
                
                portfolio[j].ffchain.pop(0)
                portfolio[j].Pri_M.ffchain=portfolio[j].ffchain
                
        pl = float(sumModelPrice_present) - float(sumModelPrice_lag) + float(sumCoupon)
        sumModelPrice_lag = float(sumModelPrice_present)
        
        portfolioMarketValue.append(sumModelPrice_present)
        DV01.append(dv01)
        PL.append(pl)
        
        ###### Below, we try to add some new bonds into the portfolio:
        
        print("We've finish the validation of season %d" %i+" and we now have "
                    "a chance to add some new bonds into the existing portfolio.")
        KKK=str(input("Do you want to add some more bonds this time?(Y or N)\n"))
        if KKK == 'Y':
            Temp=GenerateNewPortfolio(BASIC_D,BASIC_C)
            for i in range(len(Temp)):
                portfolio.append(Temp[i])
        ### The portfolio has been updated.
        ###### Now we've successfully added some new bonds into the portfolio
    
    print("The analysis results are shown below：\nNote that the \'portfolio market price\' here means "
          "the price of the portfolio right after any payment of coupons or redemptions.\n")
    
    for i in range(len(time)):
        time[i]=round(time[i],2)
        portfolioMarketValue[i] = round(portfolioMarketValue[i], 4)
        DV01[i] = round(DV01[i],4)
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