gas, temp, flame = 11.0, 26.0, 40

def cal(gas, temp, flame, sense_gas, sense_temp):
    sglist = [0, 0.25, 0.5, 1.0, 1.5, 1.75]
    stlist = [0, 0.25, 0.5, 1.0, 1.5, 1.75]
    percent = 100 * (gas * sglist[sense_gas] + temp * stlist[sense_temp] + flame) / (60 + 30 + 200)
    
    if percent > 85:
        return percent, 5
    elif percent > 70:
        return percent, 4
    elif percent > 50:
        return percent, 3
    elif percent > 30:
        return percent, 2
    else:
        return percent, 1

if __name__ == "__main__" :
    while True:
        a,b,c,d,e = map(int, input('가스, 온도, 불꽃, 가스민감, 온도민감').split())
        print(cal(a,b,c,d,e))
