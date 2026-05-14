# Real-Time Fake News AI 🚨

A professional, real-time fake news detection system powered by **DistilBERT**, **HuggingFace Transformers**, and **Streamlit**. Designed with a futuristic UI and built for high performance on local machines.

## Features ✨

- **DistilBERT Deep Learning**: Fine-tuned sequence classification model.
- **Live News Analysis**: Integration with NewsAPI to fetch and verify headlines from BBC, Reuters, etc.
- **Futuristic Streamlit UI**: Glassmorphism design, interactive components, and real-time inference.
- **Explanation System**: Confidence scoring and highlighting of sensational/suspicious keywords.
- **Optimized for Laptops**: Lightweight processing and batch sizes for standard hardware.

## Project Structure 📁

```text
real_time_fake_news_ai/
├── data/                   # Place Fake.csv and True.csv here
├── models/
│   └── saved_model/        # Trained DistilBERT model is saved here
├── utils/
│   ├── preprocessing.py    # Text cleaning and dataset balancing
│   ├── predict.py          # Inference and explanation logic
│   └── news_fetcher.py     # NewsAPI integration
├── app.py                  # Streamlit application
├── train_model.py          # Model training pipeline
├── requirements.txt        # Python dependencies
└── README.md
```

## Setup & Installation 🚀

### 1. Install Dependencies
Ensure you have Python 3.8+ installed. Run:
```bash
pip install -r requirements.txt
```

### 2. Prepare Dataset
Download the Kaggle Fake News dataset.
Place `Fake.csv` and `True.csv` into the `data/` directory.

### 3. Train the Model
Run the training script to fine-tune DistilBERT on your dataset. This will save the optimized model to `models/saved_model/`.
```bash
python train_model.py
```

### 4. Run the Streamlit UI
Launch the real-time web application:
```bash
streamlit run app.py
```

### 5. Live News Fetching
To use the Live News Analysis tab, you need a NewsAPI key. 
1. Get a free API key from [NewsAPI.org](https://newsapi.org/).
2. You can either enter it directly in the UI, or set it as an environment variable:
   - Windows: `set NEWSAPI_KEY=your_key_here`
   - Mac/Linux: `export NEWSAPI_KEY=your_key_here`

## Target Metrics 🎯
- Accuracy: 85% - 95%
- Inference Time: < 1 second per article on CPU.
