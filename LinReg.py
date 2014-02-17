class LinReg(object):
    ''' This object is used to do all functions of linear regression
        on a data object. It contains all values of theta internally
        and has methods to properly  compute these values of theta'''

    def __init__(self, data):
        '''     '''
        from learningData import learningData
        self.cost = 0
        self.theta = [0] * (data.n + 1)
        self.gradient = [0] * (data.n + 1)

    def calcCost(self, data):
        ''' This method calculates the cost and gradient of
            h(theta, X) - y '''
        cost = 0
        gradSum = 0

        for im in range(0,data.m):
            x = data.X[im]
            hTheta = self.theta[0]
            for inn in range(0,data.n):
                hTheta += x[inn] * self.theta[inn+1]
            cost += (hTheta - data.y[im])*(hTheta - data.y[im])
            gradSum += (hTheta - data.y[im])
        self.cost = cost/(2.0 * data.m)
        self.gradient[0] = gradSum/(2.0 * data.m)
        for inn in range(0,data.n):
            self.gradient[inn+1] = gradSum*x[inn]/(2.0 * data.m)


    def gradientDescent(self,data,alpha):
        ''' This method solves for theta by doing gradient descent
            on the data '''

        iteration = 0
        costMatrix = []
        while (iteration < 100):
            iteration += 1
            self.calcCost(data)
            costMatrix.append(self.cost)
            for inn in range (0, data.n + 1):
                self.theta[inn]  -= alpha * self.gradient[inn]
        return(costMatrix)
        
