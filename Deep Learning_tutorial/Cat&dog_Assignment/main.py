from torch.utils.data import Dataset
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy
from torch.utils.data import Dataset
import glob
from PIL import Image
from torch.utils.data import DataLoader

from dataset import datasetloader
from model import CNN


#function to count number of parameters
def get_n_params(model):
    np=0
    for p in list(model.parameters()):
        np += p.nelement()
    return np

input_size  = 224*224*3   # images are 224*224 pixels and has 3 channels because of RGB color
output_size = 2      # there are 2 classes---Cat and dog

# number of subprocesses to use for data loading
num_workers = 4
# how many samples per batch to load
batch_size = 60


# define training and test data directories
#data_dir = '/home/aims/data_cat&dog'
data_dir = './Cat_Dog_DataSet/'
train_dir = os.path.join(data_dir, 'train/')
test_dir = os.path.join(data_dir, 'test/')


#create transformers
train_transform = transforms.Compose([transforms.RandomResizedCrop(size=256, scale=(0.8, 1.0)),
                                    transforms.RandomRotation(degrees=15),
                                    transforms.RandomHorizontalFlip(),
                                    transforms.CenterCrop(size=224),
                                    transforms.ToTensor()])
                                    #transforms.Normalize([0.485, 0.456, 0.406],
                                     #                    [0.229, 0.224, 0.225])])
test_transforms = transforms.Compose([transforms.RandomResizedCrop(size=256, scale=(0.8, 1.0)),
                                    transforms.RandomRotation(degrees=15),
                                    transforms.RandomHorizontalFlip(),
                                    transforms.CenterCrop(size=224),
                                    transforms.ToTensor()])
                                   # transforms.Normalize([0.485, 0.456, 0.406],
                                    #                     [0.229, 0.224, 0.225])])


#train_data = datasets.ImageFolder(train_dir, transform=train_transform)
#test_data = datasets.ImageFolder(test_dir, transform=test_transforms)


# train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size,
#      num_workers=num_workers, shuffle=True)
# test_loader = torch.utils.data.DataLoader(test_data, batch_size=batch_size, 
#      num_workers=num_workers)

image_size = (224, 224)
image_row_size = image_size[0] * image_size[1]


mean = [0.485, 0.456, 0.406]
std  = [0.229, 0.224, 0.225]
train_transform = transforms.Compose([
                                transforms.Resize(image_size), 
                                                    transforms.ToTensor(), 
                                transforms.Normalize(mean, std)])
test_transforms = transforms.Compose([
                                transforms.Resize(image_size), 
                                transforms.ToTensor(), 
                                transforms.Normalize(mean, std)])
print("bfore")
train_dataset = datasetloader(train_dir, transform=train_transform)
print(len(train_dataset))
test_dataset = datasetloader(test_dir, transform=test_transforms)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size,
     num_workers=num_workers, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, 
     num_workers=num_workers)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

accuracy_list = []

def train(epoch, model):
    model.train()
    
    for batch_idx, (data, target) in enumerate(train_loader):
        
        #print(data[0].shape)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % 100 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            
def test(model, perm=torch.arange(0, 224*224).long()):
    model.eval()
    test_loss = 0
    correct = 0
    for data, target in test_loader:
        
        output = model(data)
        test_loss += F.nll_loss(output, target, reduction='sum').item() # sum up batch loss                                                               
        pred = output.data.max(1, keepdim=True)[1] # get the index of the max log-probability                                                                 
        correct += pred.eq(target.data.view_as(pred)).cpu().sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)
    accuracy_list.append(accuracy)
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        accuracy))

# Training settings 
n_features = 2 # hyperparameter

model_cnn = CNN(input_size, n_features, output_size)
optimizer = optim.SGD(model_cnn.parameters(), lr=0.01, momentum=0.5)
print('Number of parameters: {}'.format(get_n_params(model_cnn)))

for epoch in range(0, 1):
    train(epoch, model_cnn)
    test(model_cnn)
