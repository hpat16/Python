# python imports
import os
from tqdm import tqdm

# torch imports
import torch
import torch.nn as nn
import torch.optim as optim

# helper functions for computer vision
import torchvision
import torchvision.transforms as transforms
import numpy as np


class LeNet(nn.Module):
    def __init__(self, input_shape=(32, 32), num_classes=100):
        super(LeNet, self).__init__()
        # layer 1
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5, stride=1, padding=0, bias=True)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        # layer 2
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5, stride=1, padding=0, bias=True)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        # layer 3   
        self.flatten = nn.Flatten()
        # layer 4   
        self.fc1 = nn.Linear(16 * 5 * 5, 256, bias=True)   
        self.relu3 = nn.ReLU()
        # layer 5
        self.fc2 = nn.Linear(256, 128, bias=True)   
        self.relu4 = nn.ReLU()
        # layer 6
        self.fc3 = nn.Linear(128, num_classes, bias=True)

    def forward(self, x):
        shape_dict = {}
        
        result = self.pool1(self.relu1(self.conv1(x)))
        shape_dict[1] = result.shape
        result = self.pool2(self.relu2(self.conv2(result)))
        shape_dict[2] = result.shape
        result = self.flatten(result)
        shape_dict[3] = result.shape
        result = self.relu3(self.fc1(result))
        shape_dict[4] = result.shape
        result = self.relu4(self.fc2(result))
        shape_dict[5] = result.shape
        result = self.fc3(result)
        shape_dict[6] = result.shape
        
        return result, shape_dict


def count_model_params():
    '''
    return the number of trainable parameters of LeNet.
    '''
    model = LeNet()
    model_params = 0.0
    
    for name, param in model.named_parameters():
        if param.requires_grad:
            model_params += np.prod(param.shape)
    
    return model_params/1e6

def train_model(model, train_loader, optimizer, criterion, epoch):
    """
    model (torch.nn.module): The model created to train
    train_loader (pytorch data loader): Training data loader
    optimizer (optimizer.*): A instance of some sort of optimizer, usually SGD
    criterion (nn.CrossEntropyLoss) : Loss function used to train the network
    epoch (int): Current epoch number
    """
    model.train()
    train_loss = 0.0
    for input, target in tqdm(train_loader, total=len(train_loader)):
        ###################################
        # fill in the standard training loop of forward pass,
        # backward pass, loss computation and optimizer step
        ###################################

        # 1) zero the parameter gradients
        optimizer.zero_grad()
        # 2) forward + backward + optimize
        output, _ = model(input)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        # Update the train_loss variable
        # .item() detaches the node from the computational graph
        # Uncomment the below line after you fill block 1 and 2
        train_loss += loss.item()

    train_loss /= len(train_loader)
    print('[Training set] Epoch: {:d}, Average loss: {:.4f}'.format(epoch+1, train_loss))

    return train_loss


def test_model(model, test_loader, epoch):
    model.eval()
    correct = 0
    with torch.no_grad():
        for input, target in test_loader:
            output, _ = model(input)
            pred = output.max(1, keepdim=True)[1]
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_acc = correct / len(test_loader.dataset)
    print('[Test set] Epoch: {:d}, Accuracy: {:.2f}%\n'.format(
        epoch+1, 100. * test_acc))

    return test_acc