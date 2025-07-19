# === 📦 Imports ===
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchaudio
from torchaudio.datasets import LIBRISPEECH
from torchaudio.transforms import MelSpectrogram, Resample
from torch.nn.utils.rnn import pad_sequence
import os

# === ⚙ Hyperparameters ===
SAMPLE_RATE = 16000
N_MELS = 128
BATCH_SIZE = 4
NUM_EPOCHS = 10
LEARNING_RATE = 1e-3
BLANK_IDX = 0

# === 🔤 Text Transform ===
class TextTransform:
    def _init_(self):
        self.chars = ['<blank>'] + list("_abcdefghijklmnopqrstuvwxyz'")
        self.char2idx = {c: i for i, c in enumerate(self.chars)}
        self.idx2char = {i: c for i, c in enumerate(self.chars)}

    def text_to_int(self, text):
        return [self.char2idx[c] for c in text.lower() if c in self.char2idx]

    def int_to_text(self, labels):
        return ''.join([self.idx2char[i] for i in labels]).replace('_', ' ')

text_transform = TextTransform()

# === 🎧 Audio Feature Extractor ===
mel_transform = MelSpectrogram(sample_rate=SAMPLE_RATE, n_mels=N_MELS)

# === 📁 Dataset Loader ===
class LibriSpeechDataset(torch.utils.data.Dataset):
    def _init_(self, root, url="test-clean", download=True):
        self.dataset = LIBRISPEECH(root=root, url=url, download=download)

    def _getitem_(self, idx):
        waveform, sample_rate, transcript, *_ = self.dataset[idx]
        if sample_rate != SAMPLE_RATE:
            waveform = Resample(orig_freq=sample_rate, new_freq=SAMPLE_RATE)(waveform)
        mel = mel_transform(waveform).squeeze(0).transpose(0, 1)  # [time, features]
        target = torch.tensor(text_transform.text_to_int(transcript))
        return mel, target

    def _len_(self):
        return len(self.dataset)

def collate_fn(batch):
    mels, targets = zip(*batch)
    mels = pad_sequence(mels, batch_first=True)
    targets = pad_sequence(targets, batch_first=True)
    input_lengths = torch.tensor([m.size(0) for m in mels])
    target_lengths = torch.tensor([t.size(0) for t in targets])
    return mels, targets, input_lengths, target_lengths

dataset = LibriSpeechDataset()
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)

# === 🧠 Model ===
class SpeechRecognizer(nn.Module):
    def _init_(self, input_dim=128, hidden_dim=256, output_dim=29):
        super()._init_()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=2, bidirectional=True, batch_first=True)
        self.classifier = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, x):
        x, _ = self.lstm(x)
        return self.classifier(x).log_softmax(2)  # CTC needs log_softmax

model = SpeechRecognizer()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# === 🧮 Loss & Optimizer ===
criterion = nn.CTCLoss(blank=BLANK_IDX, zero_infinity=True)
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

# === 🏋 Training Loop (10 Epochs) ===
print("🚀 Training for 10 epochs")
for epoch in range(NUM_EPOCHS):
    model.train()
    total_loss = 0
    for mels, targets, input_lengths, target_lengths in dataloader:
        mels, targets = mels.to(device), targets.to(device)
        input_lengths, target_lengths = input_lengths.to(device), target_lengths.to(device)

        optimizer.zero_grad()
        outputs = model(mels)              # [B, T, C]
        outputs = outputs.permute(1, 0, 2) # [T, B, C] for CTC

        loss = criterion(outputs, targets.flatten(), input_lengths, target_lengths)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    avg_loss = total_loss / len(dataloader)
    print(f"🎯 Epoch [{epoch+1}/{NUM_EPOCHS}] - Loss: {avg_loss:.4f}")

# === 🧪 Inference ===
def greedy_decoder(output):
    pred = torch.argmax(output, dim=2)  # [B, T]
    decoded = []
    for p in pred:
        prev = BLANK_IDX
        seq = []
        for idx in p:
            if idx != prev and idx != BLANK_IDX:
                seq.append(idx.item())
            prev = idx
        decoded.append(text_transform.int_to_text(seq))
    return decoded

# === 🔍 Evaluate a Sample ===
print("\n🔍 Evaluating on sample:")
model.eval()
with torch.no_grad():
    mel, target = dataset[0]
    mel = mel.unsqueeze(0).to(device)
    output = model(mel)
    decoded = greedy_decoder(output)
    print("📢 Predicted :", decoded[0])
    print("📝 Ground Truth:", text_transform.int_to_text(target.tolist()))