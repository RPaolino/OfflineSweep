import numpy as np

r'''
Creating the random variables. Since we don't need anything more than sampling,
I decided to not use "scipy.stats" but to keep the code as simple as possible.
'''

class constant():
    def __init__(self, k):
        self.k=k
    def rvs(self, size=1):
        return np.array([self.k]*size)

class categorical():
    def __init__(self, support, probs):
        self.support=support
        self.probs = probs
    def rvs(self, size=1):
        return np.random.choice(a=self.support, p=self.probs, size=size)

class int_uniform():
    def __init__(self, low, high):
        self.low, self.high = low, high
    def rvs(self, size=1):
        return np.random.randint(self.low, self.high, size)  

class uniform():
    def __init__(self, low, high):
        self.low, self.high = low, high
    def rvs(self, size=1):
        return np.random.uniform(self.low, self.high, size)   

class q_uniform(uniform):
    def __init__(self, low, high, q):
        super.__init__(low, high)
        self.q = q 
    def rvs(self, size=1):
        return np.round(super.rvs(size)/self.q)*self.q
    
class log_uniform():
    def __init__(self, low, high):
        self.low, self.high = low, high
    def rvs(self, size=1):
        return np.exp(np.random.uniform(self.low, self.high, size))
    
class q_log_uniform(log_uniform):
    def __init__(self, low, high, q):
        super.__init__(low, high)
        self.q = q 
    def rvs(self, size=1):
        return np.round(super.rvs(size)/self.q)*self.q
    
class inv_log_uniform():
    def __init__(self, low, high):
        self.low, self.high = low, high
    def rvs(self, size=1):
        return np.exp(-np.random.uniform(self.low, self.high, size))

class log_uniform_values():
    def __init__(self, low, high):
        self.low, self.high = np.log(low), np.log(high)
    def rvs(self, size=1):
        return np.exp(np.random.uniform(self.low, self.high, size))
    
class q_log_uniform_values(log_uniform_values):
    def __init__(self, low, high, q):
        super.init(low, high)
        self.q = q
    def rvs(self, size=1):
        return np.round(super.rvs(size)/self.q)*self.q

class inv_log_uniform_values():
    def __init__(self, low, high, q):
        self.low, self.high = -np.log(high), -np.log(low)
        self.q = q
    def rvs(self, size=1):
        return np.exp(-np.random.uniform(self.low, self.high, size))

class normal():
    def __init__(self, mean, sigma):
        self.mean, self.sigma = mean, sigma
    def rvs(self, size=1):
        return np.random.normal(self.mean, self.sigma, size)
    
class q_normal(normal):
    def __init__(self, mean, sigma, q):
        super.__init__(mean, sigma)
        self.q = q
    def rvs(self, size=1):
        return np.round(super.rvs(size)/self.q)*self.q

class log_normal():
    def __init__(self, mean, sigma):
        self.mean, self.sigma = mean, sigma
    def rvs(self, size=1):
        return np.random.lognormal(self.mean, self.sigma, size)
    
class q_log_normal(log_normal):
    def __init__(self, mean, sigma, q):
        super.__init__(mean, sigma)
        self.q = q
    def rvs(self, size=1):
        return np.round(super.rvs(size)/self.q)*self.q