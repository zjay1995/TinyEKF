'''
    Extended Kalman Filter in Python

    Copyright (C) 2016 Simon D. Levy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as 
    published by the Free Software Foundation, either version 3 of the 
    License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
'''

import numpy as np
from abc import ABCMeta, abstractmethod

class EKF(object):
    '''
    A abstrat class for the Extended Kalman Filter, based on the tutorial in
    http://home.wlu.edu/~levys/kalman_tutorial.
    '''
    __metaclass__ = ABCMeta

    def __init__(self, n, m, pval=0.1, qval=1e-4, rval=0.1):
        '''
        Creates a KF object with n states, m observables, and specified values for 
        prediction noise covariance pval, process noise covariance qval, and 
        measurement noise covariance rval.
        '''

        # No previous prediction noise covariance
        self.PP_pre = None

        # Current state is zero, with diagonal noise covariance matrix
        self.xx = np.zeros((n,1))
        self.PP_post = np.eye(n) * pval

        # Get state transition and measurement Jacobians from implementing class
        self.FF = self.getF(self.xx)
        self.HH = self.getH(self.xx)

        # Set up covariance matrices for process noise and measurement noise
        self.QQ = np.eye(n) * qval
        self.RR = np.eye(m) * rval
 
        # Identity matrix will be usefel later
        self.II = np.eye(n)

    def step(self, z):
        '''
        Runs one step of the EKF on observations z, where z is a tuple of length M.
        Returns a NumPy array representing the updated state.
        '''

        # Predict ----------------------------------------------------

        # $\hat{x}_k = f(\hat{x}_{k-1})$
        self.xx = self.f(self.xx)

        # $P_k = F_{k-1} P_{k-1} F^T_{k-1} + Q_{k-1}$
        self.PP_pre = self.FF * self.PP_post * self.FF.T + self.QQ

        self.PP_post = np.copy(self.PP_pre)

        # Update -----------------------------------------------------


        # $G_k = P_k H^T_k (H_k P_k H^T_k + R)^{-1}$
        GG = np.dot(self.PP_pre * self.HH.T, np.linalg.inv(self.HH * self.PP_pre * self.HH.T + self.RR))

        # $\hat{x}_k = \hat{x_k} + G_k(z_k - h(\hat{x}_k))$
        self.xx += np.dot(GG, (np.array(z) - self.h(self.xx).T).T)

        # $P_k = (I - G_k H_k) P_k$
        self.PP_post = np.dot(self.II - np.dot(GG, self.HH), self.PP_pre)

        #return self.x.asarray()
        return self.xx

    @abstractmethod
    def f(self, x):
        '''
        Your implementing class should define this method for the state transition function f(x),
        returning a NumPy array of n elements.  Typically this is just the identity function np.copy(x).
        '''
        raise NotImplementedError()    

    @abstractmethod
    def getF(self, x):
        '''
        Your implementing class should define this method for returning the n x n Jacobian matrix F of the 
        state transition function as a NumPy array.  Typically this is just the identity matrix np.eye(n).
        '''
        raise NotImplementedError()    

    @abstractmethod
    def h(self, x):
        '''
        Your implementing class should define this method for the observation function h(x), returning
        a NumPy array of m elements. For example, your function might include a component that
        turns barometric pressure into altitude in meters.
        '''
        raise NotImplementedError()    

    @abstractmethod
    def getH(self, x):
        '''
        Your implementing class should define this method for returning the m x n Jacobian matirx H of the 
        observation function as a NumPy array.
        '''
        raise NotImplementedError()    

# Linear Algebra support =============================================

class _Matrix(object):

    def __init__(self, r=0, c=0):

        self.data = np.zeros((r,c)) if r>0 and c>0 else None

    def __str__(self):

        return str(self.data)

    def __mul__(self, other):

        new = _Matrix()

        if type(other).__name__ in ['float', 'int']:
            new.data = np.copy(self.data)
            new.data *= other
        else:
            new.data = np.dot(self.data, other.data)

        return new

    def __add__(self, other):

        new = _Matrix()
        new.data = self.data + other.data
        return new

    def __sub__(self, other):

        new = _Matrix()
        new.data = self.data - other.data
        return new

    def __setitem__(self, key, value):

        self.data[key] = value

    def __getitem__(self, key):

        return self.data[key]

    def asarray(self):

        return np.asarray(self.data[:,0])

    def copy(self):

        new = _Matrix()
        new.data = np.copy(self.data)
        return new

    def transpose(self):

        new = _Matrix()
        new.data = self.data.T
        return new

    def invert(self):

        new = _Matrix()
        try:
            new.data = np.linalg.inv(self.data)
        except Exception as e:
            print(self.data)
            print(e)
            exit(0)
        return new

    @staticmethod
    def eye(n, m=0):

        I = _Matrix()

        if m == 0:
            m = n

        I.data = np.eye(n, m)

        return I

    @staticmethod
    def fromData(data):

        a = _Matrix()

        a.data = data

        return a

class _Vector(_Matrix):

    def __init__(self, n=0):

        self.data = np.zeros((n,1)) if n>0 else None

    @staticmethod
    def fromTuple(t):

        v = _Vector(len(t))

        for k in range(len(t)):
            v[k] = t[k]

        return v


    @staticmethod
    def fromData(data):

        v = _Vector()

        v.data = data

        return v





