import torch
import transformers
import nltk

def verify_installations():
    print('Verifying NLP library installations...')
    print('PyTorch version:', torch.__version__)
    print('CUDA available:', torch.cuda.is_available() if hasattr(torch.cuda, 'is_available') else 'N/A')
    print('Transformers version:', transformers.__version__)
    print('NLTK version:', nltk.__version__)

    print('\nDownloading required NLTK data...')
    nltk.download('punkt')

    print('\nTesting PyTorch tensor creation...')
    test_tensor = torch.tensor([1, 2, 3])
    print('Test tensor created:', test_tensor)

    print('\nAll libraries successfully installed and verified!')

if __name__ == '__main__':
    verify_installations()
