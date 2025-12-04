import os
from pathlib import Path
from io import BytesIO
import base64

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UploadFileForm

# Static folder where charts are saved
CHART_DIR = Path(settings.BASE_DIR) / 'orders' / 'static' / 'orders' / 'charts'
CHART_DIR.mkdir(parents=True, exist_ok=True)


# base64 helper for displaying chart
def get_base64_image():
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
    buffer.seek(0)
    img_png = buffer.getvalue()
    base64_img = base64.b64encode(img_png).decode('utf-8')
    buffer.close()
    return base64_img


def home(request):
    return render(request, 'orders/home.html')


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']

            # save uploaded file to /media/uploads/
            uploads_dir = Path(settings.MEDIA_ROOT) / 'uploads'
            uploads_dir.mkdir(parents=True, exist_ok=True)
            upload_path = uploads_dir / f.name
            with open(upload_path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)

            # read file into pandas
            if f.name.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(upload_path)
            else:
                df = pd.read_csv(upload_path)

            # clean columns
            df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

            df['quantity'] = pd.to_numeric(df.get('quantity', 1), errors='coerce').fillna(1).astype(int)
            df['price'] = pd.to_numeric(df.get('price', 0.0), errors='coerce').fillna(0.0)
            df['order_date'] = pd.to_datetime(df.get('order_date'), errors='coerce')
            df['total'] = df['quantity'] * df['price']

            # save cleaned excel
            cleaned_path = Path(settings.MEDIA_ROOT) / f"cleaned_{f.name}"
            df.to_excel(cleaned_path, index=False)

            # generate charts (both saved + base64)
            charts_base64 = generate_charts(df)

            summary = {
                'total_orders': int(df.shape[0]),
                'total_sales': float(df['total'].sum()),
                'top_city': df.groupby('city')['total'].sum().idxmax() if 'city' in df.columns else ''
            }

            request.session['summary'] = summary
            request.session['charts_base64'] = charts_base64
            request.session['cleaned_file'] = cleaned_path.name

            return redirect('orders:dashboard')

    form = UploadFileForm()
    return render(request, 'orders/index.html', {'form': form})


def dashboard(request):
    summary = request.session.get('summary')
    charts = request.session.get('charts_base64')
    cleaned_file = request.session.get('cleaned_file')

    return render(request, 'orders/dashboard.html', {
        'summary': summary,
        'charts': charts,
        'cleaned_url': f"{settings.MEDIA_URL}{cleaned_file}" if cleaned_file else None
    })


def generate_charts(df):
    """SAVE charts + RETURN base64 images for displaying."""
    charts = {}

    # remove old charts
    for f in CHART_DIR.glob("*.png"):
        try:
            f.unlink()
        except:
            pass

    # ---------- 1. Sales by City ----------
    if 'city' in df.columns:
        city = df.groupby('city')['total'].sum().sort_values(ascending=False)
        if not city.empty:
            plt.figure(figsize=(7,4))
            city.plot(kind='bar')
            plt.title('Sales by City')
            # save chart file
            plt.savefig(CHART_DIR / 'sales_by_city.png')
            # base64 for dashboard
            charts['sales_by_city'] = get_base64_image()
            plt.close()

    # ---------- 2. Sales by Category ----------
    if 'category' in df.columns:
        cat = df.groupby('category')['total'].sum().sort_values(ascending=False)
        if not cat.empty:
            plt.figure(figsize=(7,4))
            cat.plot(kind='bar')
            plt.title('Sales by Category')
            plt.savefig(CHART_DIR / 'sales_by_category.png')
            charts['sales_by_category'] = get_base64_image()
            plt.close()

    # ---------- 3. Monthly Trend ----------
    if 'order_date' in df.columns:
        df['month'] = df['order_date'].dt.to_period('M')
        monthly = df.groupby('month')['total'].sum()
        if not monthly.empty:
            plt.figure(figsize=(7,4))
            monthly.index = monthly.index.astype(str)
            monthly.plot(kind='line', marker='o')
            plt.title('Monthly Sales Trend')
            plt.savefig(CHART_DIR / 'monthly_trend.png')
            charts['monthly_trend'] = get_base64_image()
            plt.close()

    # ---------- 4. Payment Share ----------
    if 'payment' in df.columns:
        pay = df.groupby('payment')['total'].sum()
        if not pay.empty:
            plt.figure(figsize=(6,6))
            pay.plot(kind='pie', autopct='%1.1f%%')
            plt.title('Payment Method Share')
            plt.ylabel('')
            plt.savefig(CHART_DIR / 'payment_share.png')
            charts['payment_share'] = get_base64_image()
            plt.close()

    # ---------- 5. Top Products ----------
    if 'product' in df.columns:
        prod = df.groupby('product')['quantity'].sum().sort_values(ascending=False).head(10)
        if not prod.empty:
            plt.figure(figsize=(7,4))
            prod.plot(kind='bar')
            plt.title('Top Products')
            plt.savefig(CHART_DIR / 'top_products.png')
            charts['top_products'] = get_base64_image()
            plt.close()

    return charts
