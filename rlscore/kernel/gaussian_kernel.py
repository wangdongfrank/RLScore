import numpy as np
from numpy import mat
from numpy import float64
from scipy import sparse as sp
from rlscore.utilities import array_tools


class GaussianKernel(object):
    """Gaussian (RBF) kernel.
    
    k(xi,xj) = e^(-gamma*<xi-xj,xi-xj>) + bias

    Parameters
    ----------
    train_features: {array-like, sparse matrix}, shape = [n_samples, n_features]
        Data matrix
    gamma : float, optional (default 1.0)
        Kernel width
    bias : float, optional (default 0.)
        Constant added to each kernel evaluation
    basis_vectors : array of integers, shape = [n_bvectors] or None, optional (default None)
        Indices for the subset of rows of X to be used as basis vectors. If set to None,
        by default basis_vectors = range(n_samples).
    """
      
    def __init__(self, train_features, gamma=1.0, bias=0.0, basis_vectors=None):
        if gamma <= 0.:
            raise Exception('ERROR: nonpositive kernel parameter for Gaussian kernel\n')
        if basis_vectors != None:
            self.train_X = basis_vectors
        else:
            self.train_X = train_features
        if sp.issparse(self.train_X):
            self.train_norms = ((self.train_X.T.multiply(self.train_X.T)).sum(axis=0)).T
        else:
            self.train_norms = np.mat((np.multiply(self.train_X.T, self.train_X.T).sum(axis=0))).T  
        self.gamma = gamma
        self.bias = bias
        
    def createKernel(cls, **kwargs):
        """Initializes a kernel object from the arguments."""
        new_kwargs = {}
        new_kwargs["train_features"] = kwargs["train_features"]
        if kwargs.has_key('basis_vectors'):
            new_kwargs['basis_vectors'] = kwargs['basis_vectors']
        if "gamma" in kwargs:
            new_kwargs["gamma"] = float(kwargs["gamma"])
        if "bias" in kwargs:
            new_kwargs["bias"] = float(kwargs["bias"])
        kernel = cls(**new_kwargs)
        return kernel
    createKernel = classmethod(createKernel)   
        
#    def kernel(self, x, z):
#        #Note, current implementation overrides the kernel matrix building methods
#        #of AbstractKernel, so that this method is never called when building the
#        #kernel matrix. This is left just to document what the kernel function
#        #itself is like.
#        """Kernel function is evaluated with the given arguments x and z."""
#        f = x-z
#        return np.exp(-self.gamma * (f.T * f)[0,0])
            

    def getKM(self, X):
        """Returns the kernel matrix between the basis vectors and X.
        
        Parameters
        ----------
        X: {array-like, sparse matrix}, shape = [n_samples, n_features]
        
        Returns
        -------
        K : array, shape = [n_samples, n_bvectors]
            kernel matrix
        """
        test_X = X 
        if sp.issparse(test_X):
            test_X = array_tools.spmat_resize(test_X, self.train_X.shape[1])
        else:
            test_X = array_tools.as_dense_matrix(test_X)
        gamma = self.gamma
        m = self.train_X.shape[0]
        n = test_X.shape[0]
        #The Gaussian kernel matrix is constructed from a linear kernel matrix
        linkm = self.train_X * test_X.T
        linkm = array_tools.as_dense_matrix(linkm)
        if sp.issparse(test_X):
            test_norms = ((test_X.T.multiply(test_X.T)).sum(axis=0)).T
        else:
            test_norms = (np.multiply(test_X.T, test_X.T).sum(axis=0)).T
        K = mat(np.ones((m, 1), dtype = float64)) * test_norms.T
        K = K + self.train_norms * mat(np.ones((1, n), dtype = float64))
        K = K - 2 * linkm
        K = - gamma * K
        K = np.exp(K)
        if self.bias != 0:
            K += self.bias
        return K.A.T


