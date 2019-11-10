import argparse 
import numpy as np 
np.set_printoptions(suppress=True)


def generate_data(n, lower, upper):
    """
    Generates an array of random profits and weights, and ratios thereof.
    """
    # making sure that user input was sensible
    assert(lower > 0)
    assert(n > 0)
    assert(upper > lower)

    #generate some data
    items = np.zeros((n,3))
    items[:,0:2] = np.random.randint(lower, upper, size=(n, 2))
    items[:,2] = items[:,0] / items[:,1]
    items = items[items[:,2].argsort()[::-1]]

    return items

def branch_and_bound(items, W):

    print(items)
    n = len(items)
    cstar = 0
    k = 0
    xstar = np.zeros(n)
    x = np.zeros(n)
    w = items[:,1]

    while(True):
        for i in range(k, n):
            x[i] = np.floor((W - np.dot(np.array(w),np.array(x)))/w[i])
        print(x)

        reward = np.dot(items[:,0],x)
        if reward > cstar :
            cstar = reward
            xstar = np.copy(x)
        
        l = n-1
        stay_in_loop = True
        while(stay_in_loop):
            stay_in_loop = False
            if not np.max(x[0:l]) > 0 :
                return xstar, cstar
            else:
                k = np.argmax(x[0:l])
                assert(x[k] > 0)
                x[k] = x[k] - 1

                ub = np.dot(items[0:k,0], x[0:k]) + items[k+1, 0]/items[k+1,1] * (W - np.dot(items[0:k,1],x[0:k]))

                if ub < cstar + 1 :
                    l = k - 1
                    stay_in_loop = True

def main(n, W, lower, upper):
    
    items = generate_data(n, lower, upper)

    # if you're making up the values, we need to figure out a reasonable capacity
    if W == 0:
        W = np.floor(0.8*np.sum(items[:, 1]))
        print("Die berechnete Rucksack-Kapazität ist: ",W)

    xstar, cstar = branch_and_bound(items, W)
    print("Die errechnete Lösung war ",xstar, " mit dem Zielfunktionswert ",cstar)




if __name__ == "__main__":
    """
    The knapsack instance can either be created from a file with items in them,
    or randomly generated. 
    The capacity of the knapsack has to be provided as a command line argument.
    If no capacity is provided, one will be calculated as 80% of the sum of weights.
    """

    parser = argparse.ArgumentParser(description='Invokes Branch and Bound for the Knapsack Problem')
    parser.add_argument('-n','--number', help='number of items to be generated', required=False, default=8)
    parser.add_argument('-w','--capacity', help='capacity of the knapsack', required=False)
    parser.add_argument('-u','--upper', help='upper bound of numbers', required=False, default=100)
    parser.add_argument('-l','--lower', help='lower bound of numbers', required=False, default=0)
    parser.add_argument('-f','--file', help='file to read numbers from', required=False, default='nofile')

    args = vars(parser.parse_args())

    if(args['file'] == 'nofile'):
        main(n=5, W=0, lower=1, upper=100)
    else:
        W = args['capacity']
        with open(args['file'], "w") as f:
            data = f.readlines()
            items = []
            for elem in data:
                profit, weight = " ".split(elem)
                items.append([int(profit), int(weight)])
            items = np.array(items)
            xstar, cstar = branch_and_bound(items, W)
            print("Die errechnete Lösung war ",xstar, " mit dem Zielfunktionswert ",cstar)