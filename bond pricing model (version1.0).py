# This is a bond pricing program by a simple model with funding rate
from scipy.optimize import fsolve

class Pricing_Model():
    def __init__(self,par=0,cpn_r=0,freq=0,T=0,M_p=0,c_f=0,f_r=0,B_d=0,B_c=0,S_d=0,S_c=0):
        self.par=par
        self.cpn_r=cpn_r
        self.freq=freq
        self.T=T
        self.M_p=M_p  ### market price
        self.c_f=c_f
        self.f_r=f_r
        self.B_d=B_d
        self.B_c=B_c
        self.S_d=S_d
        self.S_c=S_c


    def PV(self,C_F,Dis_Cur,Cre_Cur,F_R):
        T_d=[]#T_d means Total_discount rate curve
        for i in range(len(Dis_Cur)):
            T_d.append(Dis_Cur[i]+Cre_Cur[i]+F_R)
        PV=0.0
        for i in range(len(T_d)):
            PV=PV+C_F[i]/pow((1+T_d[i]),(float(i+1)/self.freq))
        return float(PV)





    def CalculateFundingRate(self):
        def f(x):
            x = float(x)
            return [
                self.PV(self.c_f, self.B_d, self.B_c, x)-self.M_p
            ]
        self.f_r=fsolve(f,[0.2])
        print("\nhe funding rate is %f"%(self.f_r))



    def CalculateModelPrice(self):
        result=0.0
        result=self.PV(self.c_f,self.S_d,self.S_c,self.f_r)
        print("\nBased on the shocked curves and funding rate, the new PV(model price) is: %f"%(result))
        return result






class Loan():
    def __init__(self,Pri_M=0,par=0,cpn_r=0,freq=0,T=0,M_p=0,c_f=0,f_r=0,B_d=0,B_c=0,S_d=0,S_c=0):
        self.Pri_M=Pri_M
        self.par=par
        self.cpn_r=cpn_r
        self.freq=freq
        self.T=T
        self.M_p=M_p  ### market price
        self.c_f=c_f
        self.f_r=f_r
        self.B_d=B_d
        self.B_c=B_c
        self.S_d=S_d
        self.S_c=S_c

    def UpdateBasicBondInfo(self):
        ppp=-10
        while ppp<0:
            try:
                l=float(input("please input the par value(in $):\n"))
                if l<0:
                    print("your par value is negative, please input again\n")
                    ppp=-1
                    continue
                ppp=1
            except ValueError:
                print("your input has something isn't a decimal number, please input again.\n")
                ppp=-1

        ppp=-10
        while ppp<0:
            try:
                m=float(input("please input the annualized coupon rate (in decimal,not in percentage)\n"))
                if m<0 or m>1:
                    print("your coupon rate exceeds the interval of [0,1], please inpu again\n")
                    ppp=-1
                    continue
                ppp=1
            except ValueError:
                print("your input has something isn't a decimal number, please input again.\n")
                ppp=-1

        ppp=-10
        while ppp<0:
            try:
                n=float(input("please input the coupon frequency per year(i.e. 0.5 for every 2 years,1 for annually,2 for semiannually,4 for quarterly)\n"))
                if n<0:
                    print("your coupon frequency is negative, please input again\n")
                    ppp=-1
                    continue
                ppp=1
            except ValueError:
                print("your input has something isn't a valid value, please input again.\n")
                ppp=-1

        ppp=-10
        while ppp<0:
            try:
                o=float(input("please input the remaining life time to maturity(in years and you can only choose values being multiple of the previously input frequency)\n"))
                if o<0:
                    print("your remaining life time to maturity is negative, please input again\n")
                    ppp=-1
                    continue
                if (o%(1/n))!=0.0:
                    print("your remaining life time is not a multiple of your input frequency, please input again\n")
                    ppp=-1
                    continue
                ppp=1
            except ValueError:
                print("your input has something isn't a valid value, please input again.\n")
                ppp=-1

        ppp=-10
        while ppp<0:
            try:
                p=float(input("please input the market price(in $)\n"))
                if p<0:
                    print("your market price is negative, please input again\n")
                    ppp=-1
                    continue
                ppp=1
            except ValueError:
                print("your input has something isn't a decimal number, please input again.\n")
                ppp=-1

        self.par=l
        self.cpn_r=m
        self.freq=n
        self.T=o
        self.M_p=p


    def CreatFollowingCashFlow(self):
        coupon=(self.cpn_r/self.freq)*self.par   #since the self.cpn_r means the annualized coupon rate,
        redemption=coupon+self.par  #so we need to make a little adjustment to calculate the real coupon rate
        self.c_f=[coupon]*int((self.T*self.freq-1)) # for one interval.
        self.c_f.append(redemption)


    def UpdateBasicMarketInfo(self):
        print("\nNow please enter the basic discout curve according to the coupon frequency you've just input.")
        num=int(self.T*self.freq) #actually, T*freq will always be an integer,but we still need to adjust the variable type here
        self.B_d=[]
        self.B_c=[]
        self.S_d=[]
        self.S_c=[]
        for i in range(num):
            i=i+1  #Note that this regulation is very necessary!
            unit=''
            if (i%10)==1:
                unit="st"
            elif (i%10)==2:
                unit="nd"
            elif (i%10)==3:
                unit="rd"
            else:
                unit="th"

            year=''
            if (i/self.freq)<2:
                year="year"
            else:
                year="years"

            ppp=-10
            while ppp<0:
                try:
                    v=float(input("please input the %d"%(i)+unit+" element of the BASIC DISCOUNT CURVE,\nwhich is also the annualized discount rate for the term of %f "%(i/self.freq)+year+"\n"))
                    if v<0 or v>1:
                        print("your discount rate exceeds the interval [0,1], meaning it's invalid, please input again\n")
                        ppp=-1
                        continue
                    ppp=1
                except ValueError:
                    print("your input has something isn't a decimal number, please input again.\n")
                    ppp=-1

            ppp=-10
            while ppp<0:
                try:
                    u=float(input("please input the %d"%(i)+unit+" element of the BASIC CREDIT CURVE,\nwhich is also the credit spread for the term if %f "%(i/self.freq)+year+"\n"))
                    if u<0 or u>1:
                        print("your credit spread exceeds the interval [0,1], hence it's invalid, please input again\n")
                        ppp=-1
                        continue
                    ppp=1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp=-1

            self.B_d.append(v)
            self.B_c.append(u)
            self.S_d.append(v)
            self.S_c.append(u)


    def UpdateShockedMarketInfo(self):

        print("\nNow let's shock the basis discount curve.This is your BASIC DISCOUNT CURVE:\n")
        print(self.B_d)
        Quit=''
        while Quit!=('Y' or 'y'):
            ppp=-10
            while ppp<0:
                try:
                    x=int(input("input which element you want to change(i.e. enter 2 if you want to change the second element):\n"))
                    if x<1 or x>len(self.S_d):
                        print("you've chosen an index that exceeds the boundary of the curve, input again.\n")
                        ppp=-1
                        continue
                    ppp=1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp=-1
            ppp=-10
            while ppp<0:
                try:
                    y=float(input("input the new value of this element of the curve:\n"))
                    if y<0 or y>1:
                        print("your new value exceeds the valid interval [0,1], input again.\n")
                        ppp=-1
                        continue
                    ppp=1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp=-1

            self.S_d.pop(x-1)
            self.S_d.insert(x-1,y)
            print("now this is your current SHOCKED DISCOUNT CURVE after your shift.\n")
            print(self.S_d)

            ppp=-10
            while ppp<0:
                try:
                    Quit=str(input("Have you finished regulating the BASIC DISCOUNT CURVE to form a new SHOCKED DISCOUNT CURVE? Input \'Y\' or \'N\'.\n"))
                    ppp=1
                except SyntaxError:
                    print("you've entered something invalid, please enter your choice again")
                    ppp=-1


        print("\nNow let's shock the basic credit curve.This is your BASIC CREDIT CURVE:\n")
        print(self.S_c)
        QUIT=''
        while QUIT!=('Y' or 'y'):
            ppp=-10
            while ppp<0:
                try:
                    x=int(input("input which element you want to change(i.e. enter 2 if you want to change the second element):\n"))
                    if x<1 or x>len(self.S_c):
                        print("you've chosen an index that exceeds the boundary of the curve, input again.\n")
                        ppp=-1
                        continue
                    ppp=1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp=-1
            ppp=-10
            while ppp<0:
                try:
                    y=float(input("input the new value of this element of the curve:\n"))
                    if y<0 or y>1:
                        print("your new value exceeds the valid interval [0,1], input again.\n")
                        ppp=-1
                        continue
                    ppp=1
                except ValueError:
                    print("your input has something isn't a number, please input again.\n")
                    ppp=-1

            self.S_c.pop(x-1)
            self.S_c.insert(x-1,y)
            print("now this is your current SHOCKED CREDIT CURVE after your shift.\n")
            print(self.S_c)

            ppp=-10
            while ppp<0:
                try:
                    QUIT=str(input("Have you finished regulating the BASIC CREDIT CURVE to form a new SHOCKED CREDIT CURVE? Input \'Y\' or \'N\'.\n"))
                    ppp=1
                except SyntaxError:
                    print("you've entered something invalid, please enter your choice again")
                    ppp=-1


    def ActivatePricingModel(self):
        self.Pri_M=Pricing_Model(self.par,self.cpn_r,self.freq,self.T,self.M_p,self.c_f,self.f_r,self.B_d,self.B_c,self.S_d,self.S_c)
        self.Pri_M.CalculateFundingRate()

        self.f_r=self.Pri_M.f_r
        self.Pri_M.CalculateModelPrice()



def main():
    loan=Loan()
    loan.UpdateBasicBondInfo()
    print("\nThe basic info of the loan/bond are shown as follow:\n")
    print("par,coupon rate,coupon frequency,remaining time to maturity,market price\n")
    print(loan.par,loan.cpn_r,loan.freq,loan.T,loan.M_p)

    loan.CreatFollowingCashFlow()
    print("\nThis is the cash flow of this loan:\n")
    print(loan.c_f)

    loan.UpdateBasicMarketInfo()
    print("\nThis is the basic discount curve:\n")
    print(loan.B_d)
    print("\nThis is the basic credit curve:\n")
    print(loan.B_c)

    loan.UpdateShockedMarketInfo()
    print("\nThis is the shocked discount curve:\n")
    print(loan.S_d)
    print("\nThis is the shocked credit curve:\n")
    print(loan.S_c)
    print("\nMeanwhile the basic discount curve is:\n")
    print(loan.B_d)
    print("\nAnd the basic credit curve is:\n")
    print(loan.B_c)

    loan.ActivatePricingModel()


main()