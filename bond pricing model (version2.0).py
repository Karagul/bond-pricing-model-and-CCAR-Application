# -*- coding: utf-8 -*-

# This is a bond pricing program by a simple model with funding rate
from scipy.optimize import fsolve

class Pricing_Model():
    def __init__(self, par=0, cpn_r=0, freq=0, T=0, M_p=0, c_f=0, f_r=0, B_d=0, B_c=0, S_d=0, S_c=0):
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
        for i in range(len(T_d)):
            PV = PV + C_F[i] / pow((1 + T_d[i]), (float(i + 1) / self.freq))
        return PV

    def CalculateFundingRate(self):
        def f(x):
            x = float(x)
            return [
                self.PV(self.c_f, self.B_d, self.B_c, x) - self.M_p
            ]

        self.f_r = fsolve(f, [0.2])
        print("\nThe funding rate is %f" % (self.f_r))

    def CalculateModelPrice(self):
        result = 0.0
        result = self.PV(self.c_f, self.S_d, self.S_c, self.f_r)
        print("\nBased on the shocked curves and funding rate, the new PV(model price) is: %f" % (result))
        return result


class Loan():
    def __init__(self, Pri_M=0, par=0, cpn_r=0, freq=0, T=0, M_p=0, c_f=0, f_r=0, B_d=0, B_c=0, S_d=0, S_c=0):
        self.Pri_M = Pri_M
        self.par = par
        self.cpn_r = cpn_r
        self.freq = freq
        self.T = T
        self.M_p = M_p  ### market price
        self.c_f = c_f
        self.f_r = f_r
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

    def CreatFollowingCashFlow(self):
        coupon = (self.cpn_r / self.freq) * self.par  # since the self.cpn_r means the annualized coupon rate,
        redemption = coupon + self.par  # so we need to make a little adjustment to calculate the real coupon rate
        self.c_f = [coupon] * int((self.T * self.freq - 1))  # for one interval.
        self.c_f.append(redemption)

    def UpdateBasicMarketInfo(self, B_d=0, B_c=0):
        self.B_d = B_d
        self.B_c = B_c

    def UpdateShockedMarketInfo(self, S_d=0, S_c=0):
        self.S_d = S_d
        self.S_c = S_c

    def ActivatePricingModel(self):
        self.Pri_M = Pricing_Model(self.par, self.cpn_r, self.freq, self.T, self.M_p, self.c_f, self.f_r, self.B_d,
                                   self.B_c, self.S_d, self.S_c)
        self.Pri_M.CalculateFundingRate()

        self.f_r = self.Pri_M.f_r
        self.Pri_M.CalculateModelPrice()

    def GetLatestModelPrice(self):
        x = self.Pri_M.CalculateModelPrice()
        return x




def main():
    Choice = 'Y'
    while (Choice == 'Y') or (Choice == 'y'):
        ppp = -10
        while ppp < 0:
            try:
                par = float(input("please input the par value(in $):\n"))
                if par < 0:
                    print("your par value is negative, please input again\n")
                    ppp = -1
                    continue
                ppp = 1
            except ValueError:
                print("your input has something isn't a decimal number, please input again.\n")
                ppp = -1

        ppp = -10
        while ppp < 0:
            try:
                cpn_r = float(input("please input the annualized coupon rate (in decimal,not in percentage)\n"))
                if cpn_r < 0 or cpn_r > 1:
                    print("your coupon rate exceeds the interval of [0,1], please inpu again\n")
                    ppp = -1
                    continue
                ppp = 1
            except ValueError:
                print("your input has something isn't a decimal number, please input again.\n")
                ppp = -1

        ppp = -10
        while ppp < 0:
            try:
                freq = float(input(
                    "please input the coupon frequency per year(i.e. 0.5 for every 2 years,1 for annually,"
                    "2 for semiannually,4 for quarterly)\n"))
                if freq < 0:
                    print("your coupon frequency is negative, please input again\n")
                    ppp = -1
                    continue
                ppp = 1
            except ValueError:
                print("your input has something isn't a valid value, please input again.\n")
                ppp = -1

        ppp = -10
        while ppp < 0:
            try:
                T = float(input("please input the remaining life time to maturity(in years and you can only choose " 
                                "values being multiple of the previously input frequency)\n"))
                if T < 0:
                    print("your remaining life time to maturity is negative, please input again\n")
                    ppp = -1
                    continue
                if (T % (1 / freq)) != 0.0:
                    print("your remaining life time is not a multiple of your input frequency, please input again\n")
                    ppp = -1
                    continue
                ppp = 1
            except ValueError:
                print("your input has something isn't a valid value, please input again.\n")
                ppp = -1

        ppp = -10
        while ppp < 0:
            try:
                M_p = float(input("please input the market price(in $)\n"))
                if M_p < 0:
                    print("your market price is negative, please input again\n")
                    ppp = -1
                    continue
                ppp = 1
            except ValueError:
                print("your input has something isn't a decimal number, please input again.\n")
                ppp = -1

        print("\nNow please enter the basic discount curve according to the coupon frequency you've just input.")
        num = int(
            T * freq)  # actually, T*freq will always be an integer,but we still need to adjust the variable type here
        B_d = []
        B_c = []
        S_d = []
        S_c = []
        for i in range(num):
            i = i + 1  # Note that this regulation is very necessary!
            unit = ''
            if (i % 10) == 1:
                unit = "st"
            elif (i % 10) == 2:
                unit = "nd"
            elif (i % 10) == 3:
                unit = "rd"
            else:
                unit = "th"

            year = ''
            if (i / freq) <= 1:
                year = "year"
            else:
                year = "years"

            ppp = -10
            while ppp < 0:
                try:
                    v = float(input("please input the %d" % i + unit + " element of the BASIC DISCOUNT "
                                                                       "CURVE,\nwhich is also the annualized discount"
                                                                       " rate for the term "
                                                                       "of %f " % (i / freq) + year + "\n"))
                    if v < 0 or v > 1:
                        print("your discount rate exceeds the interval [0,1], "
                              "meaning it's invalid, please input again\n")
                        ppp = -1
                        continue
                    ppp = 1
                except ValueError:
                    print("your input has something isn't a decimal number, please input again.\n")
                    ppp = -1

            ppp = -10
            while ppp < 0:
                try:
                    u = float(input("please input the %d" % i + unit + " element of the BASIC CREDIT CURVE,\nwhich "
                                                                         "is also the credit spread for the term "
                                                                         "of %f " % (i / freq) + year + "\n"))
                    if u < 0 or u > 1:
                        print("your credit spread exceeds the interval [0,1], hence it's invalid, please input again\n")
                        ppp = -1
                        continue
                    ppp = 1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp = -1
            B_d.append(v)
            B_c.append(u)
            S_d.append(v)
            S_c.append(u)

        print("\nNow let's shock the basis discount curve.This is your BASIC DISCOUNT CURVE:\n")
        print(B_d)
        Quit = ''
        while Quit != 'Y':
            ppp = -10
            while ppp < 0:
                try:
                    x = int(input("\ninput which element you want to change(i.e. enter 2 if you want to change"
                                  " the second element):\n"))
                    if x < 1 or x > len(S_d):
                        print("you've chosen an index that exceeds the boundary of the curve, input again.\n")
                        ppp = -1
                        continue
                    ppp = 1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp = -1
            ppp = -10
            while ppp < 0:
                try:
                    y = float(input("input the new value of this element of the curve:\n"))
                    if y < 0 or y > 1:
                        print("your new value exceeds the valid interval [0,1], input again.\n")
                        ppp = -1
                        continue
                    ppp = 1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp = -1
            S_d.pop(x - 1)
            S_d.insert(x - 1, y)
            print("now this is your current SHOCKED DISCOUNT CURVE after your shift.\n")
            print(S_d)

            ppp = -10
            while ppp < 0:
                try:
                    Quit = str(input("\nHave you finished regulating the BASIC DISCOUNT CURVE to form a new "
                                     "SHOCKED DISCOUNT CURVE? Input \'Y\' or \'N\'.\n"))
                    ppp = 1
                except SyntaxError:
                    print("you've entered something invalid, please enter your choice again")
                    ppp = -1

        print("\nNow let's shock the basic credit curve.This is your BASIC CREDIT CURVE:\n")
        print(S_c)
        QUIT = ''
        while QUIT != 'Y':
            ppp = -10
            while ppp < 0:
                try:
                    x = int(input("\ninput which element you want to change(i.e. enter 2 if you want to change "
                                  "the second element):\n"))
                    if x < 1 or x > len(S_c):
                        print("you've chosen an index that exceeds the boundary of the curve, input again.\n")
                        ppp = -1
                        continue
                    ppp = 1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp = -1
            ppp = -10
            while ppp < 0:
                try:
                    y = float(input("input the new value of this element of the curve:\n"))
                    if y < 0 or y > 1:
                        print("your new value exceeds the valid interval [0,1], input again.\n")
                        ppp = -1
                        continue
                    ppp = 1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp = -1
            S_c.pop(x - 1)
            S_c.insert(x - 1, y)
            print("now this is your current SHOCKED CREDIT CURVE after your shift.\n")
            print(S_c)

            ppp = -10
            while ppp < 0:
                try:
                    QUIT = str(input("\nHave you finished regulating the BASIC CREDIT CURVE to form a new"
                                     " SHOCKED CREDIT CURVE? Input \'Y\' or \'N\'.\n"))
                    ppp = 1
                except SyntaxError:
                    print("you've entered something invalid, please enter your choice again\n")
                    ppp = -1

        pri_m = Pricing_Model(par, cpn_r, freq, T, M_p, 0, 0, B_d, B_c, S_d, S_c)
        loan = Loan(pri_m, par, cpn_r, freq, T, M_p, 0, 0, B_d, B_c, S_d, S_c)
        print("\nNow let's check the information. The basic info of the loan/bond are shown as follow:\n")
        print("par=%f" % loan.par + ",coupon rate=%f" % loan.cpn_r + ",coupon frequency=%f" % loan.freq +
              ",remaining time to maturity=%f" % loan.T + ",market price=%f" % loan.M_p + "\n")

        loan.CreatFollowingCashFlow()
        print("This is the cash flow of this loan:")
        print(loan.c_f)
        print("\nThis is the basic discount curve:")
        print(loan.B_d)
        print("\nThis is the basic credit curve:")
        print(loan.B_c)
        print("\nThis is the shocked discount curve:")
        print(loan.S_d)
        print("\nThis is the shocked credit curve:")
        print(loan.S_c)

        loan.ActivatePricingModel()

        Choice = str(input("\nNow you've gone through the whole process of pricing a single bond. Do you "
                           "want to calculate another one? Input \'Y\' or \'N\'.\n"))


main()