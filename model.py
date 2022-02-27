import os
import torch
import process
import numpy as np

##########
# GLOBAL #
##########

#######
# API #
#######

def initialize_parameters_xavier(size):
    """
    Takes a tuple containing the size of a matrix and initializes weights according to Xavier rule
    Return: Variable
    """
    dim = size[0]
    std = 1.0 / np.sqrt(dim/2.0)
    return torch.randn(*size)


def transform_dataframe_to_tensor(df):
    """
    Transforms a DataFrame into a Tensor
    Return: Tensor
    """
    return torch.Tensor(df.values)

class CVAE:
    """
    Conditional Variational Autoencoder
    """
    minibatch_size : int
    latent_space_size : int
    sample_dim : int
    conditional_dim : int
    hidden_dim : int
    learning_rate : float
    count : int

    def __init__(self,minibatch=18,latent=12,sample=9,conditional=3,hidden=9,count=0,lr=1e-3):
        """
        Initializes hyperparameters for the model
        Return: None
        """
        self.minibatch_size = minibatch
        self.latent_space_size = latent
        self.sample_dim = sample
        self.conditional_dim = conditional
        self.hidden_dim = hidden
        self.count = count
        self.learning_rate = lr
        self.x_to_h_weights = initialize_parameters_xavier([sample+conditional,hidden])
        self.x_to_h_bias = torch.zeros(hidden,requires_grad=True)
        self.h_to_latent_mu = initialize_parameters_xavier([hidden,latent])
        self.h_to_latent_mu_bias = torch.zeros(latent,requires_grad=True)
        self.h_to_latent_var = initialize_parameters_xavier([hidden,latent])
        self.h_to_latent_var_bias = torch.zeros(latent,requires_grad=True)
        self.latent_to_h_weights = initialize_parameters_xavier([latent+conditional,hidden])
        self.latent_to_h_bias = torch.zeros(hidden,requires_grad=True)
        self.hidden_to_sample_weights = initialize_parameters_xavier([hidden,sample])
        self.hidden_to_sample_bias = torch.zeros(sample,requires_grad=True)
        params = [
            self.x_to_h_weights,
            self.x_to_h_bias,
            self.h_to_latent_mu,
            self.h_to_latent_mu_bias,
            self.h_to_latent_var,
            self.h_to_latent_var_bias,
            self.latent_to_h_weights,
            self.latent_to_h_bias,
            self.hidden_to_sample_weights,
            self.hidden_to_sample_bias
        ]
        solver = torch.optim.Adam(params,lr=lr)

    def encode(self,X,c):
        """
        Encodes a vector containing sample and conditional data into the latent space
        Return: tuple of Tensors
        """
        # Feed input through hidden layer
        input = torch.cat([X,c],1)
        h = torch.nn.functional.relu(input @ self.x_to_h_weights + self.x_to_h_bias)

        # Feed hidden layer output through latent space layer
        latent_mu = h @ self.h_to_latent_mu + self.h_to_latent_mu_bias
        latent_var = h @ self.h_to_latent_var + self.h_to_latent_var_bias
        return latent_mu,latent_var

    def sample_from_latent(self,mu,var):
        """
        Samples a random latent space vector based on distribution inputs
        Return: Tensor
        """
        eps = torch.randn(self.minibatch_size,self.latent_space_size)
        return mu + torch.exp(var/2)*eps

    def decode(self,z,c):
        """
        Decodes a latent space vector using conditionals to return a matching sample
        Return: Tensor
        """
        input = torch.cat([z,c],1)
        h = torch.nn.functional.relu(input @ self.latent_to_h_weights + self.latent_to_h_bias)
        return torch.nn.functional.sigmoid(h @ self.hidden_to_sample_weights + self.hidden_to_sample_bias)

    def calculate_loss(self,y,X,mu,var):
        """
        Calculates loss
        Return: Tensor
        """
        reconstruction = torch.nn.functional.cross_entropy(y,X,size_average=False) / self.minibatch_size
        kl = torch.mean(0.5*torch.sum(torch.exp(var)+mu**2-1.0-var,1))
        return reconstruction + kl

    def fit(self,df,verbose=0):
        """
        Trains model on given dataframe
        Return: tuple of Tensors
        """
        # split data between samples and conditionals
        samples,conditionals = process.split_samples_from_conditionals(df,self.conditional_dim)

        # convert dataframes to tensors
        samples = transform_dataframe_to_tensor(samples)
        conditionals = transform_dataframe_to_tensor(conditionals)
        
        for i in range(0,len(samples)-self.minibatch_size,self.minibatch_size):
            if verbose:
                print(f"Fitting batch {i} of {len(samples)//self.minibatch_size+1}")

            # identify the next training batch
            X,c = samples[i:i+self.minibatch_size],conditionals[i:i+self.minibatch_size]

            # forward pass
            mu,var = self.encode(X,c)
            latent = self.sample_from_latent(mu,var)
            y = self.decode(latent,c)

            # calculate loss
            loss = self.calculate_loss(y,X,mu,var)
            if verbose:
                print(f"Associated cross entropy loss: {loss}")

            # backward pass
            loss.backward()
            self.solver.step()
            for p in self.params:
                if p.grad is not None:
                    p.grad = p.grad.data.new().resize_as_(p.grad.data).zero_()
        
        # set final values for latent space distribution
        self.mu = mu
        self.var = var

    def sample(self,c):
        """
        Samples from trained latent space with given conditionals
        Return: Tensor
        """
        return self.decode(self.sample_from_latent(self.mu,self.var),c)

##########
# DRIVER #
##########

if __name__ == "__main__":
    # specify the path to data directory
    data_directory_path = os.path.join("data")        
    
    # extract all data into a dataframe
    df = process.extract_data(data_directory_path)

    # initialize model
    model = CVAE()

    # fit data to model
    model.fit(df,verbose=1)

    # sample from fitted data
    model.sample([5,0,3])