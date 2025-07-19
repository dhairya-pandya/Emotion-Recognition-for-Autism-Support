from huggingface_hub import snapshot_download
import os

# The model we want to download (with the CORRECT username)
model_id = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"

# The directory to save the model files
local_dir = "speech-emotion-model"

print(f"Downloading model '{model_id}' to '{local_dir}'...")

# Download the model and its configuration files
snapshot_download(
    repo_id=model_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False # Set to False to download actual files
)

print("Model download complete!")