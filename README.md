# 📊 E-Commerce Order Analysis Web Application (Django + Pandas + Matplotlib)

This is a complete **Data Analysis Web Application** built using **Django**, **Pandas**, **NumPy**, and **Matplotlib**.  
Users can upload an Excel file containing e-commerce order data, and the application automatically:

✔ Cleans the dataset  
✔ Performs data analysis  
✔ Generates insights & summary statistics  
✔ Creates visualization charts  
✔ Displays an interactive dashboard  
✔ Allows downloading of cleaned Excel data  

This project is perfect for beginners learning **Python, Django, Data Analysis, Excel, Visualization**, and **Backend Web Development**.

---

## 🚀 Features

### 📁 1. File Upload (Excel)
- Supports `.xlsx`, `.xls`, and `.csv`
- Automatically detects and cleans messy column names
- Converts datatypes (date, quantity, price)

### 🧹 2. Data Cleaning using Pandas
- Removes invalid values
- Fixes missing data
- Normalizes column names
- Converts data to proper numeric and datetime formats

### 📈 3. Data Analysis
Using Pandas, the app analyzes:

- Total Sales  
- Total Orders  
- Top City by Revenue  
- Sales by Category  
- Sales by Month  
- Payment Method Share  
- Top-Selling Products  

### 📊 4. Data Visualization using Matplotlib
The app generates charts:

- Sales by City (Bar Chart)  
- Sales by Category (Pie Chart)  
- Monthly Sales Trend (Line Chart)  
- Payment Method Share (Pie Chart)  
- Top 10 Products (Horizontal Bar Chart)

All charts are:
- Saved as PNG files  
- Also displayed as **base64 images** (guaranteed to show in browser)  

### 🖥 5. Interactive Dashboard
Shows:
- Summary Cards  
- All Charts  
- Download Cleaned File Button  

### 📂 6. Cleaned Excel Download
After processing, a cleaned Excel file is automatically generated and available to download.

---

## 🔧 Tech Stack

### **Backend**
- Python  
- Django (Models, Views, Templates, Static Files)  

### **Data Processing**
- Pandas  
- NumPy  

### **Visualization**
- Matplotlib  

### **Frontend**
- HTML  
- CSS  
- (No JavaScript used — beginner-friendly)

---

## 📁 Project Structure (Important Folders Only)

---

## 🛠 How to Run the Project (Step-by-Step)

### 1️⃣ Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

shell
Copy code

### 2️⃣ Install required packages
pip install -r requirements.txt

shell
Copy code

### 3️⃣ Run migrations
python manage.py migrate

shell
Copy code

### 4️⃣ Start the development server
python manage.py runserver

shell
Copy code

### 5️⃣ Open browser
http://127.0.0.1:8000

## 🙌 Author  
**Rashith K**  
Beginner Python & Data Analysis Learner  

---

## 🏁 Conclusion  
This project demonstrates how to combine **Django + Pandas + Matplotlib** to build a real working **data analysis web application** — perfect for student portfolios, resumes, and learning backend development.
