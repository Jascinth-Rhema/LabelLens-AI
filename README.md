#  LabelLens AI

### AI-Powered Food & Skincare Label Analyzer

LabelLens AI is a Streamlit-based application that helps users understand food and skincare product labels using OCR, ingredient analysis, nutrition analysis, and personalized recommendations.
---

##  features

### 📷 Scan Product Labels
- Upload an image of a product label
- Capture a label using camera
- Extract text using OCR
- Automatically identify ingredients

###  Ingredient Analysis
- Detect known ingredients
- Explain ingredient functions
- Identify potentially concerning ingredients
- Provide easy-to-understand safety information

###  Nutrition Analysis
- Extract nutrition information from labels
- Analyze calories, protein, carbohydrates, sugar, fat, fibre, and sodium
- Scale nutrition values based on quantity consumed
- Show daily reference percentages
- Provide simple nutrition guidance

###  Product Comparison
- Compare two products
- View ingredient and nutrition information
- Easily understand differences between products

###  Personalized Recommendations
Users can select:
- Skin tone
- Skin concerns
- Hair concerns
- Lip concerns
- Budget

The application then provides relevant product recommendations.

###  Explore
- Explore ingredients
- Learn about common food and skincare ingredients
- Understand ingredient purposes and potential concerns

###  Scan History
- Save previous scans
- View previously analyzed products
- Review past results

---

## 🛠️ Technologies Used

- Python
- Streamlit
- SQLite
- Tesseract OCR
- Pytesseract
- Pillow
- Pandas
- RapidFuzz

---

## Project Structure

```text
LabelLens-AI/
│
├── app.py
├── ai_explainer.py
├── database.py
├── diagnostics.py
├── guides.py
├── ingredient_matcher.py
├── nutrition.py
├── ocr_engine.py
├── personalization.py
├── text_processor.py
├── unknown_explainer.py
│
├── data/
│   └── ingredients.csv
│
├── requirements.txt
├── render-build.sh
├── .gitignore
└── README.md
```

---

##  Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Jascinth-Rhema/LabelLens-AI.git
cd LabelLens-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

#### Windows

```powershell
.venv\Scripts\activate
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser at:

```text
https://labellens-ai-1-b8v7.onrender.com/
```

---

##  OCR Requirement

LabelLens AI uses **Tesseract OCR** to extract text from product labels.

### Windows

Install Tesseract OCR separately and make sure it is available in your system PATH.

### Linux / Render

Tesseract can be installed using:

```bash
apt-get update
apt-get install -y tesseract-ocr
```

---

##  Deployment

LabelLens AI can be deployed using platforms such as:

- Streamlit Community Cloud
- Render
- Hugging Face Spaces

For Render, the application can be started with:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

---

##  Project Objective

The main goal of LabelLens AI is to make product labels easier to understand.

Instead of requiring users to understand complicated ingredient names and nutrition tables, the application converts label information into simple and understandable insights.

---

##  Author

**Jascinth Rhema**

GitHub:  
https://github.com/Jascinth-Rhema

---


LabelLens AI provides general informational guidance and is not a substitute for professional medical, nutritional, dermatological, or healthcare advice.
```

### Git-la README add panna

`README.md` file create pannitu **above code paste** pannunga.

Then:

```powershell
git add README.md
git commit -m "Add project README"
git push
```

