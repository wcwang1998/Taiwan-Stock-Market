# ---------------------------------- import library --------------------------------- #

import streamlit as st
import pandas as pd
import finlab
from finlab import data
import requests
import re
import datetime
import numpy as np                  
import plotly.graph_objs as go  
import plotly.express as px
import yfinance as yf

# ---------------------------------- basic parameters --------------------------------- #

finlab.login(api_token="vdrky4XWtsiNiSybGA8xwZVNH7xVzDmsYEUyRSGkAyvYqDuUeKWWPSJxE2YnwHeJ#free")

st.set_page_config(
    page_title="Taiwan Stock Market Dashboard",
    page_icon=r"https://upload.cc/i1/2021/12/31/RtxJjG.png",
    layout="wide",
    # initial_sidebar_state="expanded",
    menu_items={
        'About': "# Created by Jack Wang.\n Linkedin: https://www.linkedin.com/in/weichieh1998/"
     }
)

# ---------------------------------- Title --------------------------------- #

a1, a2 = st.columns([1,8])
a1.image(r"https://upload.cc/i1/2021/12/31/ePSKUF.png", use_column_width=True, output_format="auto")
a2.title("Taiwan Stock Market")
a2.markdown(
    """
    <a href="https://share.streamlit.io/wcwang1998/taiwan-stock-market---index/main/streamlit_app_1.py">Index</a>
    ｜<a href="https://share.streamlit.io/wcwang1998/taiwan-stock-market/main/streamlit_app_2.py">Industries</a>
    ｜<a href="https://yahoo.com.tw">Stocks</a>
    ｜Created by 
    <a href="https://www.linkedin.com/in/weichieh1998/">Jack Wang</a>
    """, 
    unsafe_allow_html=True,
    )
update = a2.button("Update Data", help='Click to update data')

# ---------------------------------- Index --------------------------------- #

# def update_tw_index_data():
if update:
    st.cache_data.clear()
    st.cache_resource.clear()
    
    with st.spinner('Updating Data...'):
        # Index
        @st.cache_data
        def tw_index():

            tw_close = data.get('taiex_total_index:收盤指數') #抓取加權收盤指數
            today_tw_close = tw_close.iloc[-1,0] #選擇最後一筆資料

            tw_close['change'] = tw_close['TAIEX'] - tw_close['TAIEX'].shift(1) #計算點數變化
            tw_close['pct_change'] = tw_close['TAIEX'].pct_change() #計算漲跌百分比

            tw_num_change = round(tw_close['change'][-1],2) #取最新的點數變化
            tw_pct_change = round(tw_close['pct_change'][-1]*100,2) #取最新的漲跌百分比
            tw_change = str(tw_num_change)+" ("+str(tw_pct_change)+"%)"

            return [today_tw_close,tw_change,tw_close]

        today_tw_close = tw_index()[0]
        tw_change = tw_index()[1]
        
        # OTC
        @st.cache_data
        def tw_OTC():

            tw_otc = data.get('stock_index_price:收盤指數')
            tw_otc['change'] = tw_otc['上櫃櫃買指數'] - tw_otc['上櫃櫃買指數'].shift(1)
            tw_otc['pct_change'] = tw_otc['上櫃櫃買指數'].pct_change()

            today_tw_otc = tw_otc['上櫃櫃買指數'][-1]
            tw_otc_num_change = round(tw_otc['change'][-1],2)
            tw_otc_pct_change = round(tw_otc['pct_change'][-1]*100,2)
            tw_otc_change = str(tw_otc_num_change)+" ("+str(tw_otc_pct_change)+"%)"

            return [today_tw_otc,tw_otc_change,tw_otc]

        today_tw_otc = tw_OTC()[0]
        tw_otc_change = tw_OTC()[1]
        tw_otc = tw_OTC()[2]
        today_date = tw_otc.index[-1]
        today_date = today_date.strftime('%Y-%m-%d')

        # up&down
        @st.cache_data
        def tw_up_down():

            #建構爬取網站及參數
            url = 'https://histock.tw/%E5%8F%B0%E8%82%A1%E5%A4%A7%E7%9B%A4'
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
                }

            res = requests.get(url=url, headers=header)
            res.encoding = res.apparent_encoding

            #用正則表達式爬取
            patt = r'<tr class="alt-row">.*?<th class="alt">上市</th>.*?<td id="tseRaise" class="hide">(.*?)</td>.*?<td id="tseFall" class="hide">(.*?)</td>.*?<td class="clr-rd2">(.*?)</td>.*?<td class="clr-rd2">(.*?)</td>.*?<td>.*?</td>.*?<td class="clr-gr">(.*?)</td>.*?<td class="clr-gr">(.*?)</td>.*?<td class="clr-rd">.*?</td>.*?<td class="clr-gr">.*?</td>'
            res_1 = re.findall(pattern=patt, string=res.text, flags=re.S)

            for data in res_1:
                tw_up_pct = data[0]
                tw_up_stop = data[2]
                tw_up_num = data[3]
                tw_up = tw_up_num+"("+tw_up_stop+")"

                tw_down_pct = data[1]
                tw_down_num = data[4]
                tw_down_stop = data[5]
                tw_down = tw_down_num+"("+tw_down_stop+")"
            
            return [tw_up,tw_up_pct,tw_down,tw_down_pct]

        tw_up = tw_up_down()[0]
        tw_up_pct = tw_up_down()[1]
        tw_down = tw_up_down()[2]
        tw_down_pct = tw_up_down()[3]

        # Display
        b0, b1, b2, b3, b4 = st.columns(5)
        b0.metric(label="Data Updated:", value=today_date)
        b1.metric(label="TAIEX", value=today_tw_close, delta=tw_change, delta_color="inverse")
        b2.metric(label="TWO (OTC)", value=today_tw_otc, delta=tw_otc_change, delta_color="inverse")
        b3.metric(label="Increase", value=tw_up, delta=tw_up_pct, delta_color="inverse")
        b4.metric(label="Decrease", value=tw_down, delta=tw_down_pct, delta_color="normal")
        
        # TAIEX figure
        @st.experimental_singleton
        def tw_figure():
            
            # Define date
            mask = '%Y-%m-%d'
            lastBusDay = datetime.date.today()
            weekday = datetime.date.weekday(lastBusDay)
            last_year = lastBusDay - datetime.timedelta(days = 365)

            if weekday == 5:      #if it's Saturday
                lastBusDay = lastBusDay - datetime.timedelta(days = 1) #then make it Friday
                last_year = lastBusDay - datetime.timedelta(days = 365)
            elif weekday == 6:      #if it's Sunday
                lastBusDay = lastBusDay - datetime.timedelta(days = 2); #then make it Friday
                last_year = lastBusDay - datetime.timedelta(days = 365)
            elif weekday == 0:
                last_year = lastBusDay - datetime.timedelta(days = 365)

            lastBusDay = lastBusDay.strftime(mask)
            last_year = last_year.strftime(mask)

            # download data
            twii = yf.Ticker("^TWII")
            df = twii.history(start=last_year, end=lastBusDay)

            # calculate MA
            df['ma_5'] = df['Close'].rolling(5).mean()
            df['ma_10'] = df['Close'].rolling(10).mean()
            df['ma_20'] = df['Close'].rolling(20).mean()
            df['ma_60'] = df['Close'].rolling(60).mean()

            # define volume color
            df['diag']=np.empty(len(df))  
            df.diag[df.Close>df.Open]='#f94144' #red
            df.diag[df.Close<=df.Open]='#70B77E'  #green

            # design fig
            trace0 = go.Scatter(x=df.index, y=df.ma_5, name='<b>5MA</b>', line_width=1)
            trace1 = go.Scatter(x=df.index, y=df.ma_10, name='<b>10MA</b>', line_width=1)
            trace2 = go.Scatter(x=df.index, y=df.ma_20, name='<b>20MA</b>', line_width=1)
            trace3 = go.Scatter(x=df.index, y=df.ma_60, name='<b>60MA</b>', line_width=1)
            candlestick = go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'],
                                        increasing_line_color='red',
                                        decreasing_line_color='green',
                                        name="<b>TAIEX</b>")
            vol = go.Bar(x=df.index, y=df.Volume, marker_color=df.diag, yaxis="y2", name='<b>Volume</b>')                           

            # make fig
            data = [candlestick, trace0, trace1, trace2, trace3, vol]
            layout = go.Layout(title="<b>TAIEX</b>",
                            title_x=0.5,
                            title_font_size=20,
                            xaxis1_rangeslider_visible=True,
                            template="ygridoff",
                            showlegend=True,
                            yaxis=dict(title="<b>TAIEX</b>"),
                            yaxis2=dict(title="<b>Volume</b>", overlaying="y", side="right", range=[0,50000000]),
                            legend=dict(x=0.6, y=1.025, yanchor="bottom", orientation="h"),
                            #    autosize=False,
                            #    width=600,
                            #    height=600,
                            paper_bgcolor='rgba(255,255,255,0.5)',
                            plot_bgcolor='rgba(255,255,255,0.5)',
                            margin=dict(l=40, r=50, t=50, b=40),
                            hovermode="x unified"
                            )

            fig = go.Figure(data=data, layout=layout)

            # set rangeslider 
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])],
                            showgrid = True,
                            rangeselector = dict(
                                buttons=list([
                                        dict(count=1,label="1m",step="month",stepmode="backward"),
                                        dict(count=3,label="3m",step="month",stepmode="backward"),
                                        dict(count=6,label="6m",step="month",stepmode="backward"),
                                        dict(count=1,label="1y",step="year",stepmode="backward"),
                                        dict(step="all")
                                        ])
                            ))

            taiex_plot = fig

            return taiex_plot

        taiex_plot = tw_figure()
        st.plotly_chart(taiex_plot, use_container_width=True)

        # institutional investor
        @st.cache_resource
        def institutional_investor():

            # Define date
            mask = '%Y-%m-%d'
            lastBusDay = datetime.date.today()
            weekday = datetime.date.weekday(lastBusDay)
            last_year = lastBusDay - datetime.timedelta(days = 365)

            if weekday == 5:      #if it's Saturday
                lastBusDay = lastBusDay - datetime.timedelta(days = 1) #then make it Friday
                last_year = lastBusDay - datetime.timedelta(days = 365)
            elif weekday == 6:      #if it's Sunday
                lastBusDay = lastBusDay - datetime.timedelta(days = 2); #then make it Friday
                last_year = lastBusDay - datetime.timedelta(days = 365)
            elif weekday == 0:
                last_year = lastBusDay - datetime.timedelta(days = 365)

            lastBusDay = lastBusDay.strftime(mask)
            last_year = last_year.strftime(mask)

            # download taiwan stock data
            twii = yf.Ticker("^TWII")
            df = twii.history(start=last_year, end=lastBusDay)['Close']
            # print(df)

            # institutional investor data
            inst_investors = data.get('institutional_investors_trading_all_market_summary:買賣超')
            inst_investors['上市自營商(合計)'] = inst_investors['上市自營商(自行買賣)'] + inst_investors['上市自營商(避險)']
            inst_investors['三大法人(合計)'] = inst_investors['上市自營商(合計)'] + inst_investors['上市投信'] + inst_investors['上市外資及陸資(不含外資自營商)']
            # print(inst_investors[['上市外資及陸資(不含外資自營商)','上市投信','上市自營商(合計)','三大法人(合計)']][-245:])

            # Make fig
            trace1 = go.Bar(x=inst_investors.index[-245:], 
                            y=inst_investors['上市外資及陸資(不含外資自營商)'][-245:], 
                            name='<b>Foreign Investors</b>',
                            marker_color = '#0a9396',
                            )
            trace2 = go.Bar(x=inst_investors.index[-245:], 
                            y=inst_investors['上市投信'][-245:], 
                            name='<b>Securities Trust</b>', 
                            marker_color = '#e9c46a',
                            )
            trace3 = go.Bar(x=inst_investors.index[-245:], 
                            y=inst_investors['上市自營商(合計)'][-245:], 
                            name='<b>Securities Dealers</b>', 
                            marker_color = '#e76f51',
                            )               
                                        
            data1 = [trace1, trace2, trace3]
            layout = go.Layout(title="<b>Institutional Investors</b>",
                                title_x=0.5,
                                title_font_size=20,
                                barmode='stack',
                                xaxis1_rangeslider_visible=True,
                                template="ygridoff",
                                showlegend=True,
                                yaxis=dict(title="<b>TW dollars</b>"),
                                legend=dict(x=0.65, y=1.025, yanchor="bottom", orientation="h"),
                                paper_bgcolor='rgba(255,255,255,0.5)',
                                plot_bgcolor='rgba(255,255,255,0.5)',
                                margin=dict(l=45, r=50, t=50, b=40),
                                hovermode="x unified"
                                )

            fig = go.Figure(data=data1, layout=layout)

            # set rangeslider 
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])],
                            showgrid = True,
                            rangeselector = dict(
                            buttons=list([
                                    dict(count=1,label="1m",step="month",stepmode="backward"),
                                    dict(count=3,label="3m",step="month",stepmode="backward"),
                                    dict(count=6,label="6m",step="month",stepmode="backward"),
                                    dict(count=1,label="1y",step="year",stepmode="backward"),
                                    dict(step="all")
                                    ])
                            ))
            institutional_investor_plot = fig

            return institutional_investor_plot
        
        institutional_investor_plot = institutional_investor()
        st.plotly_chart(institutional_investor_plot, use_container_width=True)

        # buy on margin & short sell
        @st.cache_resource
        def margin_short():
            # get data
            margin_short = data.get('margin_balance:融資券總餘額')
            margin_short['融資增加'] = margin_short['上市融資交易金額'] - margin_short['上市融資交易金額'].shift(1)
            margin_short['融券增加'] = margin_short['上市融券交易張數'] - margin_short['上市融券交易張數'].shift(1)
            # print(margin_short)

            # Make buy_on_margin fig
            trace1 = go.Scatter(x=margin_short.index[-245:], 
                                y=margin_short['上市融資交易金額'][-245:], 
                                name='<b>Buy on Margin</b>',
                                marker_color = '#9e2a2b',
                                )
            trace2 = go.Bar(x=margin_short.index[-245:], 
                            y=margin_short['融資增加'][-245:], 
                            name='<b>Change</b>',
                            marker_color = '#ff595e',
                            yaxis="y2"
                            )

            data1 = [trace1, trace2]
            layout = go.Layout(title="<b>Buy on Margin</b>",
                                title_x=0.5,
                                title_font_size=20,
                                barmode='stack',
                                xaxis1_rangeslider_visible=True,
                                template="ygridoff",
                                showlegend=True,
                                yaxis=dict(title="<b>TW dollars</b>"),
                                yaxis2=dict(title="<b>Change</b>", overlaying="y", side="right",),
                                legend=dict(x=0.85, y=1.025, yanchor="bottom", orientation="h"),
                                paper_bgcolor='rgba(255,255,255,0.5)',
                                plot_bgcolor='rgba(255,255,255,0.5)',
                                margin=dict(l=45, r=50, t=50, b=40),
                                hovermode="x unified"
                                )

            fig = go.Figure(data=data1, layout=layout)

            # set rangeslider 
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])],
                            showgrid = True,
                            rangeselector = dict(
                            buttons=list([
                                    dict(count=1,label="1m",step="month",stepmode="backward"),
                                    dict(count=3,label="3m",step="month",stepmode="backward"),
                                    dict(count=6,label="6m",step="month",stepmode="backward"),
                                    dict(count=1,label="1y",step="year",stepmode="backward"),
                                    dict(step="all")
                                    ])
                            ))
            buy_on_margin = fig
            # buy_on_margin.show()

            # Make short_sell fig
            trace1 = go.Scatter(x=margin_short.index[-245:], 
                                y=margin_short['上市融券交易張數'][-245:], 
                                name='<b>Short Sell</b>',
                                marker_color = '#036666',
                                )
            trace2 = go.Bar(x=margin_short.index[-245:], 
                            y=margin_short['融券增加'][-245:], 
                            name='<b>Change</b>',
                            marker_color = '#78c6a3',
                            yaxis="y2"
                            )

            data2 = [trace1, trace2]
            layout = go.Layout(title="<b>Short Sell</b>",
                                title_x=0.5,
                                title_font_size=20,
                                barmode='stack',
                                xaxis1_rangeslider_visible=True,
                                template="ygridoff",
                                showlegend=True,
                                yaxis=dict(title="<b>TW dollars</b>"),
                                yaxis2=dict(title="<b>Change</b>", overlaying="y", side="right",),
                                legend=dict(x=0.9, y=1.025, yanchor="bottom", orientation="h"),
                                paper_bgcolor='rgba(255,255,255,0.5)',
                                plot_bgcolor='rgba(255,255,255,0.5)',
                                margin=dict(l=45, r=0, t=50, b=40),
                                hovermode="x unified"
                                )

            fig = go.Figure(data=data2, layout=layout)

            # set rangeslider 
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])],
                            showgrid = True,
                            rangeselector = dict(
                            buttons=list([
                                    dict(count=1,label="1m",step="month",stepmode="backward"),
                                    dict(count=3,label="3m",step="month",stepmode="backward"),
                                    dict(count=6,label="6m",step="month",stepmode="backward"),
                                    dict(count=1,label="1y",step="year",stepmode="backward"),
                                    dict(step="all")
                                    ])
                            ))
            short_sell = fig
            # short_sell.show()
            return [buy_on_margin,short_sell]
        
        buy_on_margin = margin_short()[0]
        short_sell = margin_short()[1]
        st.plotly_chart(buy_on_margin, use_container_width=True)
        st.plotly_chart(short_sell, use_container_width=True)

        # taiex vs otc: pct change
        tw_close = tw_index()[2]
        tw_otc = tw_OTC()[2]

        @st.cache_resource
        def taiex_vs_otc():
            y1 = tw_close['pct_change'].iloc[-250:].apply('{:.2%}'.format)
            y2 = tw_otc['pct_change'].iloc[-250:].apply('{:.2%}'.format)

            merge = pd.DataFrame(columns=['index','otc'])
            merge['index'] = y1
            merge['otc'] = y2

            trace0 = go.Scatter(
                x = merge.index,
                y = merge['index'],
                mode = 'lines+markers',
                name = '<b>TAIEX</b>',
                line_color = '#6096ba',
                marker_symbol = 4,
            )
            trace1 = go.Scatter(
                x = merge.index,
                y = merge['otc'],
                mode = 'lines+markers',
                name = '<b>OTC</b>',
                line_color = '#fcbf49',
            )

            data = [trace0, trace1]

            layout = go.Layout(
                            title="<b>TAIEX vs. OTC</b>",
                            title_x=0.5,
                            title_font_size=20,
                            template="ygridoff",
                            # xaxis_title="<b>Date</b>",
                            yaxis_title="<b>Percentage change(%)</b>",
                            # legend=dict(xanchor="right",yanchor="top"),
                            paper_bgcolor='rgba(255,255,255,0.5)',
                            plot_bgcolor='rgba(255,255,255,0.5)',
                            margin=dict(l=40, r=0, t=30, b=40),
                            hovermode="x unified",
                            legend=dict(x=0.85, y=0.9, yanchor="bottom", orientation="h"),
                            )     

            fig = go.Figure(data=data, layout=layout)  

            fig.update_xaxes(rangeslider_visible=True,
                        rangeselector = dict(
                            buttons=list([
                                    dict(count=1,label="1m",step="month",stepmode="backward"),
                                    dict(count=3,label="3m",step="month",stepmode="backward"),
                                    dict(count=6,label="6m",step="month",stepmode="backward"),
                                    dict(count=1,label="1y",step="year",stepmode="backward"),
                                    dict(step="all")
                                    ])
                        )
            )
            
            taiex_vs_otc_plot = fig

            return taiex_vs_otc_plot

        taiex_vs_otc_plot = taiex_vs_otc()
        st.plotly_chart(taiex_vs_otc_plot, use_container_width=True)

        # tw_treemap
        @st.cache_resource
        def tw_treemap():
            def df_date_filter(df, start=None, end=None):
                if start:
                    df = df[df.index >= start]
                if end:
                    df = df[df.index <= end]
                return df

            def create_treemap_data(start, end, item, clip=None):
                close = data.get('price:收盤價')
                basic_info = data.get('company_basic_info')
                turnover = data.get('price:成交金額')
                close_data = df_date_filter(close, start, end)
                turnover_data = df_date_filter(turnover, start, end).iloc[1:].sum() / 100000000
                return_ratio = (close_data.iloc[-1] / close_data.iloc[-2]).dropna().replace(np.inf, 0)
                return_ratio = round((return_ratio - 1) * 100, 2)

                concat_list = [close_data.iloc[-1], turnover_data, return_ratio]
                col_names = ['stock_id', 'close', 'turnover', 'return_ratio']
                if item not in ["return_ratio", "turnover_ratio"]:
                    try:
                        custom_item = df_date_filter(data.get(item), start, end).iloc[-1].fillna(0)
                    except Exception as e:
                        # logger.error('data error, check the data is existed between start and end.')
                        # logger.error(e)
                        return None
                    if clip:
                        custom_item = custom_item.clip(*clip)
                    concat_list.append(custom_item)
                    col_names.append(item)

                df = pd.concat(concat_list, axis=1).dropna()
                df = df.reset_index()
                df.columns = col_names

                basic_info_df = basic_info.copy()
                basic_info_df['stock_id_name'] = basic_info_df['stock_id']+basic_info_df['公司簡稱']

                df = df.merge(basic_info_df[['stock_id', 'stock_id_name', '產業類別', '市場別', '實收資本額(元)']], how='left',
                            on='stock_id')
                df = df.rename(columns={'產業類別': 'category', '市場別': 'market', '實收資本額(元)': 'base'})
                df = df.dropna(thresh=5)
                df['market_value'] = round(df['base'] / 10 * df['close'] / 100000000, 2)
                df['turnover_ratio'] = df['turnover'] / (df['turnover'].sum()) * 100
                df['country'] = 'TW-Stock'
                return df


            def plot_tw_stock_treemap(start=None, end=None, area_ind='market_value', item='return_ratio', clip=None,
                                    color_scales='Temps'):
                df = create_treemap_data(start, end, item, clip)
                if df is None:
                    return None
                df['custom_item_label'] = round(df[item], 2).astype(str)

                if area_ind not in ["market_value", "turnover", "turnover_ratio"]:
                    return None

                if item in ['return_ratio']:
                    color_continuous_midpoint = 0
                else:
                    color_continuous_midpoint = np.average(df[item], weights=df[area_ind])

                fig = px.treemap(df,
                                path=['country', 'market', 'category', 'stock_id_name'],
                                values=area_ind,
                                color=item,
                                color_continuous_scale=color_scales,
                                color_continuous_midpoint=color_continuous_midpoint,
                                custom_data=['custom_item_label', 'close', 'turnover'],
                                # title='Treemap',
                                width=1600,
                                height=800)

                fig.update_traces(textposition='middle center',
                                textfont_size=18,
                                texttemplate="%{label}(%{customdata[1]})<br>%{customdata[0]}",
                                )
                
                fig.update_layout(title_text="<b>Taiwan Stock Market TreeMap</b>", 
                                title_x=0.5, 
                                title_font_size=20, 
                                title_xanchor="center",
                                margin=dict(l=40, r=0, b=40)
                                )

                return fig

            # 台股漲跌與市值板塊圖
            db = data.get('price:收盤價')

            start= db.index[-2] #@param {type:"date"}
            end = db.index[-1] #@param {type:"date"}
            area_ind="turnover_ratio" #@param ["market_value","turnover","turnover_ratio"] {allow-input: true}
            item="return_ratio" #@param ["return_ratio", "turnover_ratio"] {allow-input: true}
            clip = 1000 #@param {type:"number"}

            # global tw_treemap_plot
            tw_treemap_plot = plot_tw_stock_treemap(start,end,area_ind,item,clip)
            
            return tw_treemap_plot

        tw_treemap_plot = tw_treemap()
        st.plotly_chart(tw_treemap_plot, use_container_width=True)

# --------------------------------- Update data --------------------------------- #

# if update:
#     st.experimental_memo.clear()
#     st.experimental_singleton.clear()
#     update_tw_index_data()

