import plotly.express as px
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import streamlit as st
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from PIL import Image


st.set_page_config(
    page_title="QBear Financial Insights",
    layout="wide",
    page_icon="🧸"
)

st.write('<div style="text-align : center;"><font size="35"><b>SCREENER</b></font></div>', unsafe_allow_html=True)
st.write('<div style="text-align : center;"><font size="3"><i>by - theqbearproject</i></font></div>', unsafe_allow_html=True)

st.markdown("""
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #530000;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)
logo = Image.open(r"C:\Users\asus\OneDrive\Desktop\Qbear\Qbear website\Q (1).jpg")
company_list = ["TATAMOTORS", "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY",
                "BDL", "TCS", "HINDUNILVR", "MARUTI", "LT", "VBL", "SUNPHARMA",
                "HCLTECH", "SBIN", "ITC", "ONGC", "TRENT"]

#st.sidebar.write('<div style="text-align : center;"><font size="10"><b>QBear</b></font></div>', unsafe_allow_html=True)
st.sidebar.image(logo, use_container_width=True )
selected_company = st.sidebar.selectbox('Choose your company', company_list)
st.sidebar.link_button('Back', "https://qbearproject.github.io/qbear-project.github.io/")
st.sidebar.markdown("---")
st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
st.sidebar.caption(
    """
    **Disclaimer:**  
    This app provides financial information for educational purposes only. 
    Forecasts are based on historical data and linear regression models, 
    which may not accurately predict future performance. 
    Past performance is not indicative of future results. 
    Consult a qualified financial advisor before making investment decisions.
    
    ***Data sources : Yahoo Finance***  

    
    """
)


try:
    ticker = yf.Ticker(f'{selected_company}.NS')
    df = ticker.history(period='max', interval='1d')
except Exception as e:
    st.error(f"Error loading company data. Please try again later.")
    st.stop()

class NewsFetcher:
    def __init__(self, comp):
        self.comp = comp

    def fetch_news(self):
        try:
            news_data = self.comp.get_news()
            if not news_data:
                st.info("No news available for this company.")
                return
            
            for i in range(min(5, len(news_data))):
                try:
                    article = news_data[i]
                    st.subheader(article['content']['title'])
                    st.write(article['content']['summary'])
                    st.write(f'<font size="1">{article["content"]["pubDate"]}</font>', unsafe_allow_html=True)
                    url = article['content']['canonicalUrl']['url']
                    st.link_button("Read more", url)
                    st.divider()
                except KeyError:
                    st.write("Error displaying news article.")
        except Exception as e:
            st.info("News data not available at the moment.")

class FundamentalsFetcher:
    def __init__(self, company):
        self.company = company

    def fetch_statements(self):
        try:
            incm_statement = self.company.financials
            bs = self.company.balance_sheet
            cf = self.company.cashflow
            
            df1 = pd.DataFrame(incm_statement)
            df2 = pd.DataFrame(bs)
            df3 = pd.DataFrame(cf)
            
            st.subheader('Income Statement')
            st.dataframe(df1)
            st.subheader('Balance Sheet')
            st.dataframe(df2)
            st.subheader('Cash Flow')
            st.dataframe(df3)
            return df1 
        except Exception as e:
            st.info("Financial statements data not available.")

class CompanyDetails:
    def __init__(self, comp):
        self.company = comp

    def fetch_details(self):
        try:
            info = self.company.info
            return info["longBusinessSummary"]
        except Exception as e:
            return "Company description not available."
        
    def other_details(self):
        try:
            fii_dii = self.company.info.get('heldPercentInstitutions', 'N/A')
            insiders = self.company.info.get('heldPercentInsiders', 'N/A')
            current_price = self.company.info.get('currentPrice', 'N/A')
            trailing_eps = self.company.info.get('trailingEps', 'N/A')
            forward_eps = self.company.info.get('forwardEps', 'N/A')
            pricetoBook = self.company.info.get('priceToBook', 'N/A')
            weekslow52 = self.company.info.get('fiftyTwoWeekLow', 'N/A')
            weekshigh52 = self.company.info.get('fiftyTwoWeekHigh', 'N/A')
            marketCap = self.company.info.get('marketCap', 'N/A')
            beta = self.company.info.get('beta', 'N/A')
            trailingPE = self.company.info.get('trailingPE', 'N/A')
            forwardPE = self.company.info.get('forwardPE', 'N/A')
            profitMargins = self.company.info.get('profitMargins', 'N/A')
            quick_ratio = self.company.info.get('quickRatio', 'N/A')
            current_ratio = self.company.info.get('currentRatio', 'N/A')
            de = self.company.info.get('debtToEquity', 'N/A')
            rev_growth = self.company.info.get('revenueGrowth', 'N/A')
            dividend_value = self.company.info.get('lastDividendValue', 'N/A')

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Cap", f"₹ {marketCap/1e9:.2f} Cr.")
                st.metric("Stock P/E", f"{trailingPE}")
                st.metric("ROCE", f"{profitMargins:.2f} %")
                st.metric("Dividend Yield", "1.76 %")

            with col2:
                st.metric("Current Price", f"₹ {current_price}")
                st.metric("Price to Book", f"₹ {pricetoBook:.2f}")
                st.metric("ROE", f"{de:.2f} %")
                st.metric("Dividend", f"₹{dividend_value}")

            with col3:
                st.metric("52 Week High / Low", f"₹ {weekshigh52} / {weekslow52}")
                st.metric("Debt to Equity", f"{de}")
                st.metric("Beta", f"{beta:.2f}")
                st.metric("Revenue Growth", f"{rev_growth*100} %")
        except Exception as e:
            st.info("Some data not available for this company.")

class plots:
    def __init__(self, company, data=None):
        self.company = company
        self.data = data

    def holdings_chart(self):
        try:
            fii_dii = self.company.info.get('heldPercentInstitutions', 0)*100
            insiders = self.company.info.get('heldPercentInsiders', 0)*100
            retailers = 100 - ((fii_dii + insiders))
            
            labels = ['FII/DII', 'Insiders', 'Retailers']
            values = [fii_dii, insiders, retailers]
            holdings_data = {'labels': labels, 'values': values}
            
            fig = px.pie(
                holdings_data,
                values='values',
                names='labels',
                title='',
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.3 
            )
            fig.update_traces(hovertemplate='<b>%{label}</b><br>Percentage: %{value:.2f}%<extra></extra>')
            fig.update_layout(
                margin=dict(t=60, b=20, l=20, r=20),
                annotations=[
                    dict(
                        text=f'Total: 100%',
                        x=0.5,
                        y=0.5,
                        font_size=12,
                        showarrow=False
                    )
                ]
            )

            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("Holdings data not available or incomplete.")

    def other_charts(self):
        col1, col2, col3 = st.columns([1,1,1])
        
        try:
            # Fetch financial statements
            incm_statement = self.company.financials
            
            # Define metrics to forecast
            metrics = {
                'Total Revenue': 'Revenue Forecasts',
                'EBITDA': 'EBITDA Forecasts',
                'Net Income': 'Income Forecasts'
            }
            
            forecast_results = {}
            
            for metric, title in metrics.items():
                if metric in incm_statement.index:
                    # Get historical data
                    data = incm_statement.loc[metric]
                    
                    # Create a clean series without NaN values
                    clean_data = data.dropna()
                    
                    # Skip if not enough data points
                    if len(clean_data) < 2:
                        forecast_results[metric] = {'error': f"Not enough data points ({len(clean_data)})"}
                        continue
                    
                    # Prepare DataFrame
                    df_metric = pd.DataFrame({
                        'Date': pd.to_datetime(clean_data.index),
                        metric: clean_data.values
                    }).sort_values('Date')
                    
                    # Extract years
                    df_metric['Year'] = df_metric['Date'].dt.year
                    
                    # Linear regression model
                    X = df_metric[['Year']]
                    y = df_metric[metric]
                    
                    try:
                        model = LinearRegression()
                        model.fit(X, y)
                        
                        # Generate future predictions (next 5 years)
                        last_year = df_metric['Year'].max()
                        future_years = np.arange(last_year + 1, last_year + 6)
                        future_predictions = model.predict(future_years.reshape(-1, 1))
                        
                        forecast_results[metric] = {
                            'historical': df_metric,
                            'future_years': future_years,
                            'future_predictions': future_predictions,
                            'title': title
                        }
                    except Exception as model_error:
                        forecast_results[metric] = {'error': f"Model error: {str(model_error)}"}
            
            # Plot charts
            for i, metric in enumerate(metrics.keys()):
                col = [col1, col2, col3][i]
                title = metrics[metric]
                
                with col:
                    st.subheader(title)
                    
                    if metric in forecast_results:
                        data = forecast_results[metric]
                        
                        if 'error' in data:
                            st.error(data['error'])
                            st.plotly_chart(go.Figure(), use_container_width=True)
                        else:
                            fig = go.Figure()
                            
                            # Historical data
                            fig.add_trace(go.Scatter(
                                x=data['historical']['Date'],
                                y=data['historical'][metric],
                                mode='lines+markers',
                                name='Historical',
                                line=dict(color='blue')
                            ))
                            
                            # Forecast data
                            future_dates = [datetime(year, 6, 30) for year in data['future_years']]
                            fig.add_trace(go.Scatter(
                                x=future_dates,
                                y=data['future_predictions'],
                                mode='lines+markers',
                                name='Forecast',
                                line=dict(color='red', dash='dot')
                            ))
                            
                            fig.update_layout(
                                xaxis_title='Year',
                                yaxis_title='Amount (₹)',
                                hovermode='x unified',
                                showlegend=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"{metric} data not available")
                        st.plotly_chart(go.Figure(), use_container_width=True)
        
        except Exception as e:
            # Fallback if any error occurs
            st.error(f"Error generating forecasts: {str(e)}")
            with col1:
                st.subheader('Revenue Forecasts')
                st.plotly_chart(go.Figure(), use_container_width=True)
            with col2:
                st.subheader('EBITDA Forecasts')
                st.plotly_chart(go.Figure(), use_container_width=True)
            with col3:
                st.subheader('Income Forecasts')
                st.plotly_chart(go.Figure(), use_container_width=True)


class Oscillator:
    def __init__(self, data):
        self.data = data
        self.indicator_df = pd.DataFrame()
        self.indicator_df['Close'] = self.data['Close']

    def comp_graph(self):
        try:
            figure = go.Figure()
            figure.update_layout(
                width=900,
                height=700,
                dragmode='zoom', 
                hovermode='x unified'
            )
            figure.add_trace(go.Scatter(x=self.indicator_df.index, y=self.data['Close'], name='Close Price'))
            figure.update_xaxes(rangeslider_visible=False,
                                rangeselector=dict(
                                    buttons=list([
                                        dict(count=3, label="3m", step="month"),
                                        dict(count=6, label="6m", step="month"),
                                        dict(count=1, label="YTD", step="year"),
                                        dict(count=5, label="5y", step="year"),
                                        dict(count=10, label="10y", step="year"),
                                        dict(step="all")
                                    ])))
            st.plotly_chart(figure, use_container_width=True)
        except Exception as e:
            st.info("Error generating price chart.")


class analyst_targets:

    def __init__(self, comp):
        self.company = comp

    def targets(self):

        try:
            
            currentPrice = self.company.info.get('currentPrice', 'N/A')
            target_high = self.company.info.get('targetHighPrice', 'N/A')
            target_low = self.company.info.get('targetLowPrice', 'N/A')
            target_mean = self.company.info.get('targetMeanPrice', 'N/A')
            target_median = self.company.info.get('targetMedianPrice', 'N/A')
            recomendation = self.company.info.get('recommendationKey', 'N/A')
            analyst_rating = self.company.info.get('recommendationMean', 'N/A')

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Price", f"₹ {currentPrice}")
                st.metric("Target Upper Bound ", f"₹ {target_high}")
                st.metric("Target Lower Bound", f"₹ {target_low}")
                

            with col2:
                st.metric("Target Mean Price", f"₹ {target_mean}")
                st.metric("Target Median Price", f"₹ {target_median}")
                
                st.metric("Analysts Ratings ", f"{analyst_rating}")
            st.divider()


            rec_color = "#2ecc71" if recomendation.lower() == 'buy' else "#e74c3c" if recomendation.lower() == 'sell' else "#f39c12"
            st.markdown(f"<h2 style='text-align: center; color: {rec_color};'>RECOMMENDATION: {recomendation.upper()}</h2>", 
                        unsafe_allow_html=True)

                
            
        except Exception as e:
            st.info("This company may be left for analysis")





col1, col2 = st.columns([14,4])

with col1:
    try:
        st.header(f"{selected_company}")
        st.caption(f"{ticker.info.get('website', 'Website not available')}")
        Oscillator(df).comp_graph()
        st.divider()

        st.header('About the company')
        st.write(CompanyDetails(ticker).fetch_details())
        st.header(f"Important metrics")
        CompanyDetails(ticker).other_details()

        st.header(f"Financial Statements - {selected_company}")
        st.divider()
        FundamentalsFetcher(ticker).fetch_statements()
        st.divider()
        st.header(f"Holdings - {selected_company}")
        plots(ticker).holdings_chart()
        st.divider()
        st.header(f'Forecasts - {selected_company}')
        plots(ticker).other_charts()
        st.divider()
        st.header(f'Analysis and Results - {selected_company}')
        analyst_targets(ticker).targets()
        st.divider()
    except Exception as e:
        st.error("Error loading main content. Please try again later.")

with col2:
    try:
        st.write(f"<h3>News</h3>", unsafe_allow_html=True)
        NewsFetcher(ticker).fetch_news()
    except Exception as e:
        st.info("Error loading news section.")

st.markdown("""
    <style>
        section[data-testid="stException"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<br><br><br><br>

© 2025 The QBear project. All rights reserved.

""", unsafe_allow_html=True)
