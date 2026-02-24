import os
from pathlib import Path
from io import BytesIO
import base64

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.urls import reverse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import UploadFileForm

# Where to save charts inside your project static
CHART_DIR = Path(settings.BASE_DIR) / 'orders' / 'static' / 'orders' / 'charts'
CHART_DIR.mkdir(parents=True, exist_ok=True)

def _fig_to_base64():
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=120)
    buffer.seek(0)
    img_data = buffer.getvalue()
    buffer.close()
    return base64.b64encode(img_data).decode('utf-8')

@login_required
def home(request):
    return render(request, 'orders/home.html')


@login_required
def upload(request):
    """
    Upload view: accepts file, reads with pandas, cleans, saves cleaned file,
    generates charts and stores summary + charts in session then redirect to dashboard.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']

            # Save the uploaded file to MEDIA/uploads/
            uploads_dir = Path(settings.MEDIA_ROOT) / 'uploads'
            uploads_dir.mkdir(parents=True, exist_ok=True)
            upload_path = uploads_dir / f.name
            with open(upload_path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)

            # Read file into DataFrame
            if f.name.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(upload_path)
            else:
                df = pd.read_csv(upload_path)

            # Basic cleaning & normalization
            df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
            # Coerce numeric
            if 'quantity' in df.columns:
                df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
            else:
                df['quantity'] = 1
            if 'price' in df.columns:
                df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
            else:
                df['price'] = 0.0

            # parse order_date if present
            if 'order_date' in df.columns:
                df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

            df['total'] = df['quantity'] * df['price']
            df.dropna(how='all', inplace=True)   #Removes rows where everything is empty.
            
            #HANDLE TEXT COLUMN NaN
            text_cols = df.select_dtypes(include='object').columns
            df[text_cols] = df[text_cols].fillna('Unknown')
            if 'order_date' in df.columns:
                df['order_date'].fillna(df['order_date'].mode()[0], inplace=True)
            
            #REMOVE INVALID SALES ROWS
            df = df[(df['quantity'] >= 0) & (df['price'] >= 0)]
            #STANDARDIZE OTHER TEXT COLUMNS
            for col in ['product', 'payment_mode', 'customer_name']:
                if col in df.columns:
                    df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.title()
        )
            
            if 'city' in df.columns:
                df['city'] = ( df['city'].astype(str).str.strip().str.lower().str.title())
               # remove extra spaces  # convert to lowercase # Capitalize (Delhi, Mumbai)
            
    


            if df.empty:
                 return render(request, 'orders/upload.html', {'error': 'Uploaded file has no valid numeric data.'})

            # Save cleaned file to MEDIA for download
            cleaned_name = f"cleaned_{f.name}"
            cleaned_path = Path(settings.MEDIA_ROOT) / cleaned_name
            df.to_excel(cleaned_path, index=False)

            # Generate charts and base64 versions
            charts = generate_charts(df)

            summary = {
                'total_orders': int(df.shape[0]),
                'total_sales': float(df['total'].sum()),
                'top_city': df.groupby('city')['total'].sum().idxmax() if 'city' in df.columns and not df.groupby('city')['total'].sum().empty else ''
            }

            # store for dashboard
            request.session['summary'] = summary
            request.session['charts'] = charts
            request.session['cleaned_name'] = cleaned_name

            return redirect('orders:dashboard')
    else:
        form = UploadFileForm()

    return render(request, 'orders/index.html', {'form': form})


@login_required
def dashboard(request):
    summary = request.session.get('summary')
    charts = request.session.get('charts', {})
    cleaned_name = request.session.get('cleaned_name')

    cleaned_url = f"{settings.MEDIA_URL}{cleaned_name}" if cleaned_name else None

    return render(request, 'orders/dashboard.html', {
        'summary': summary,
        'charts': charts,
        'cleaned_url': cleaned_url
    })


def signup(request):
    """
    Simple signup view — creates a User (username, email, password).
    Passwords are hashed by Django automatically.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('orders:signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('orders:signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('orders:login')

    return render(request, 'orders/signup.html')
    

def generate_charts(df):
    """
    Generate charts (saved to static folder) and return base64 inline strings in a dict.
    """
    charts = {}

    # Remove old charts
    for f in CHART_DIR.glob("*.png"):
        try:
            f.unlink()
        except Exception:
            pass

    # Sales by city (bar)
    if 'city' in df.columns:
        city = df.groupby('city')['total'].sum().sort_values(ascending=False)
        if not city.empty:
            plt.figure(figsize=(7,4))
            city.plot(kind='bar')
            plt.title('Sales by City')
            plt.tight_layout()
            plt.savefig(CHART_DIR / 'sales_by_city.png')
            charts['sales_by_city'] = _fig_to_base64()
            plt.close()

    # Sales by category (bar/pie)
    if 'category' in df.columns:
        cat = df.groupby('category')['total'].sum().sort_values(ascending=False)
        if not cat.empty:
            plt.figure(figsize=(7,4))
            cat.plot(kind='bar')
            plt.title('Sales by Category')
            plt.tight_layout()
            plt.savefig(CHART_DIR / 'sales_by_category.png')
            charts['sales_by_category'] = _fig_to_base64()
            plt.close()

    # Monthly trend
    if 'order_date' in df.columns:
        try:
            df['month'] = df['order_date'].dt.to_period('M')
            monthly = df.groupby('month')['total'].sum()
            if not monthly.empty:
                plt.figure(figsize=(7,4))
                monthly.index = monthly.index.astype(str)
                monthly.plot(kind='line', marker='o')
                plt.title('Monthly Sales Trend')
                plt.tight_layout()
                plt.savefig(CHART_DIR / 'monthly_trend.png')
                charts['monthly_trend'] = _fig_to_base64()
                plt.close()
        except Exception:
            pass

    # Payment methods (pie)
    if 'payment' in df.columns or 'payment_method' in df.columns:
        key = 'payment' if 'payment' in df.columns else 'payment_method'
        pay = df.groupby(key)['total'].sum()
        if not pay.empty:
            plt.figure(figsize=(6,6))
            pay.plot(kind='pie', autopct='%1.1f%%')
            plt.ylabel('')
            plt.title('Payment Method Share')
            plt.tight_layout()
            plt.savefig(CHART_DIR / 'payment_share.png')
            charts['payment_share'] = _fig_to_base64()
            plt.close()

    # Top products
    if 'product' in df.columns or 'product_name' in df.columns:
        key = 'product' if 'product' in df.columns else 'product_name'
        prod = df.groupby(key)['quantity'].sum().sort_values(ascending=False).head(10)
        if not prod.empty:
            plt.figure(figsize=(7,4))
            prod.plot(kind='bar')
            plt.title('Top Products by Quantity')
            plt.tight_layout()
            plt.savefig(CHART_DIR / 'top_products.png')
            charts['top_products'] = _fig_to_base64()
            plt.close()

    return charts
