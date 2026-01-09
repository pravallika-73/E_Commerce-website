from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import io

app = Flask(__name__)

# ---------- LOAD DATA ----------

df = pd.read_csv("data/larger_sales_dataset.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
df = df.dropna(subset=["Order Date", "Order ID", "Total Price"])

# ---------- KPI FUNCTION ----------

def compute_kpis(dataframe, start_date=None, end_date=None):
    d = dataframe.copy()

    if start_date is not None:
        d = d[d["Order Date"] >= start_date]
    if end_date is not None:
        d = d[d["Order Date"] <= end_date]

    total_sales = d["Total Price"].sum()
    num_orders = d["Order ID"].nunique()
    aov = total_sales / num_orders if num_orders > 0 else 0

    sales_by_date = (
        d.groupby(d["Order Date"].dt.date)["Total Price"]
        .sum()
        .reset_index()
        .rename(columns={"Order Date": "date", "Total Price": "total_sales"})
    )

    sales_by_category = (
        d.groupby("Product Category")["Total Price"]
        .sum()
        .reset_index()
        .rename(columns={"Product Category": "category", "Total Price": "total_sales"})
        .sort_values("total_sales", ascending=False)
    )

    return {
        "total_sales": float(total_sales),
        "num_orders": int(num_orders),
        "aov": float(aov),
        "sales_by_date": sales_by_date.to_dict(orient="records"),
        "sales_by_category": sales_by_category.to_dict(orient="records"),
    }

# ---------- ROUTES ----------

# Main page
@app.route("/")
def index():
    return render_template("index.html")

# KPI API for dashboard
@app.route("/api/kpis")
def kpis_api():
    start = request.args.get("start")
    end = request.args.get("end")

    start_date = pd.to_datetime(start) if start else None
    end_date = pd.to_datetime(end) if end else None

    result = compute_kpis(df, start_date, end_date)
    return jsonify(result)

@app.route("/api/sales_by_month")
def sales_by_month():
    start = request.args.get("start")
    end = request.args.get("end")

    start_date = pd.to_datetime(start) if start else None
    end_date = pd.to_datetime(end) if end else None

    d = df.copy()
    if start_date is not None:
        d = d[d["Order Date"] >= start_date]
    if end_date is not None:
        d = d[d["Order Date"] <= end_date]

    d["YearMonth"] = d["Order Date"].dt.to_period("M")
    sales_month = (
        d.groupby("YearMonth")["Total Price"]
        .sum()
        .reset_index()
    )
    sales_month["YearMonth"] = sales_month["YearMonth"].astype(str)

    result = sales_month.rename(
        columns={"YearMonth": "month", "Total Price": "total_sales"}
    ).to_dict(orient="records")

    return jsonify(result)

# CSV report download
@app.route("/api/report/csv")
def report_csv():
    start = request.args.get("start")
    end = request.args.get("end")

    start_date = pd.to_datetime(start) if start else None
    end_date = pd.to_datetime(end) if end else None

    d = df.copy()
    if start_date is not None:
        d = d[d["Order Date"] >= start_date]
    if end_date is not None:
        d = d[d["Order Date"] <= end_date]

    report_df = d[
        [
            "Order ID",
            "Order Date",
            "Product Category",
            "Quantity",
            "Unit Price",
            "Total Price",
            "Payment Type",
            "Order Status",
        ]
    ]

    buffer = io.StringIO()
    report_df.to_csv(buffer, index=False)
    buffer.seek(0)

    filename = f"sales_report_{start}_{end}.csv"
    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename,
    )

# (PDF route completely removed/commented)

# ---------- MAIN ----------

if __name__ == "__main__":
    app.run(debug=True)
