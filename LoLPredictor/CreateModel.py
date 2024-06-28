import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


class PredictionModel(nn.Module):
    def __init__(self, input_size, hidden_sizes, output_size):
        super(PredictionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_sizes[0])
        self.fc2 = nn.Linear(hidden_sizes[0], hidden_sizes[1])
        if len(hidden_sizes) > 2:
            self.fc3 = nn.Linear(hidden_sizes[1], hidden_sizes[2])
            self.fc4 = nn.Linear(hidden_sizes[2], output_size)
        else:
            self.fc3 = None
            self.fc4 = nn.Linear(hidden_sizes[1], output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        if self.fc3:
            x = F.relu(self.fc3(x))
        x = torch.sigmoid(self.fc4(x))
        return x



def createAndTrainModel(input_size, hidden_sizes, lr=0.001, epochs=100):

    model = PredictionModel(input_size, hidden_sizes, 1)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        pass


    torch.save(model.state_dict(), 'model.pth')

    raise NotImplementedError

input_size = 2*167 + 1
hidden_sizes = [2*167 + 1, 2*167 + 1] # Also try: [128, 64]

