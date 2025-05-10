try:
    print("Attempting to import transformers...")
    from transformers import AutoTokenizer # Import just one component for simplicity
    print("Transformers import successful!")
    print(f"Tokenizer path: {AutoTokenizer.__file__}")
except ImportError as e:
    print(f"ImportError occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")