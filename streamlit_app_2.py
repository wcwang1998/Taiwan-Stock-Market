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
    ｜<a href="https://yahoo.com.tw">Industries</a>
    ｜Created by 
    <a href="https://www.linkedin.com/in/weichieh1998/">Jack Wang</a>
    """, 
    unsafe_allow_html=True,
    )
update = a2.button("Update Data", help='Click to update data')

# ---------------------------------- Industries --------------------------------- #

# def tw_industries():
if update:
    st.experimental_memo.clear()
    st.experimental_singleton.clear()

    with st.spinner('Updating Data...'):

        # Turnover Ratio
        @st.experimental_singleton
        def turnover_ratio():
            # 建構爬取網站及參數
            url = 'https://pscnetsecrwd.moneydj.com/b2brwdCommon/jsondata/c6/fb/f2/twstockdata.xdjjson?x=afterhours-market0003-1&revision=2018_07_31_1'
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
                }

            res = requests.get(url=url, headers=header)
            res.encoding = res.apparent_encoding
            res = res.json()

            # 爬取資料
            res1 = res['ResultSet']['Result']
            # print(res1)

            # create df
            df = pd.DataFrame(columns=['Industries', 'today value', 'ytr value'])
            ind = []
            today = []
            ytr = []
            date = []

            # 將資料寫進df
            for x in res1:
                temp_ind = x['V4']
                temp_today = float(x['V5'])
                temp_ytr = float(x['V6'])
                temp_date = x['V2']

                ind.append(temp_ind)
                today.append(temp_today)
                ytr.append(temp_ytr)
                date.append(temp_date)
                # print(x['V4'],x['V5'],x['V6'])

            df['Industries'] = ind
            df['today value'] = today
            df['ytr value'] = ytr
            df['date'] = date

            # calculate data needed
            df['today pct'] = df['today value'] / df.iloc[30,1]
            df['ytr pct'] = df['ytr value'] / df.iloc[30,2]
            df['pct change'] = df['today pct'] - df['ytr pct']
            df = df.sort_values('today pct', ascending=False)

            # convert data type: float into pct
            df['today pct'] = df['today pct'].map(lambda x:format(x,'.2%'))
            df['ytr pct'] = df['ytr pct'].map(lambda x:format(x,'.2%'))
            df['pct change'] = df['pct change'].map(lambda x:format(x,'.2%'))
            # display(df)

            # Make fig
            trace1 = go.Bar(x=df['Industries'][1:], 
                            y=df['today pct'][1:], 
                            name='<b>Today Turnover Ratio</b>',
                            marker_color = '#457b9d',
                            )
            trace2 = go.Bar(x=df['Industries'][1:], 
                            y=df['ytr pct'][1:], 
                            name='<b>Yesterday Turnover Ratio</b>',
                            marker_color = '#e9c46a',
                            )
            trace3 = go.Scatter(x=df['Industries'][1:], 
                                y=df['pct change'][1:], 
                                name='<b>Percentage Difference</b>',
                                marker_color = '#d62828',
                                yaxis="y2",
                                mode = 'lines+markers',
                                )
            update = "Data Updated: "+df.iloc[0,3]

            data1 = [trace1, trace2, trace3]
            layout = go.Layout(title="<b>Turnover Ratio</b>",
                                title_x=0.5,
                                title_font_size=20,
                                template="ygridoff",
                                showlegend=True,
                                xaxis=dict(title=update),
                                yaxis=dict(title="<b>Percentage(%)</b>"),
                                yaxis2=dict(title="<b>Percentage Difference(%)</b>", overlaying="y", side="right",),
                                legend=dict(x=0.25, y=1.025, yanchor="bottom", orientation="h"),
                                paper_bgcolor='rgba(255,255,255,0.5)',
                                plot_bgcolor='rgba(255,255,255,0.5)',
                                # margin=dict(l=45, r=50, t=50, b=40),
                                hovermode="x unified"
                                )

            fig = go.Figure(data=data1, layout=layout)
            fig.update_xaxes(showgrid = True, tickangle = 90)

            return fig
        
        turnover_ratio_fig = turnover_ratio()
        st.plotly_chart(turnover_ratio_fig, use_container_width=True)

        @st.experimental_singleton
        def industries_index():
            # 建構爬取網站及參數
            url = 'http://stock.pchome.com.tw/market/sto0'
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
                }

            res = requests.get(url=url, headers=header)
            res.encoding = res.apparent_encoding

            # 用正則表達式爬取
            patt = r'<td class="ct"><a href=".*?">(.*?)</a></td>.*?<td class="ct">.*?</td>.*?<td class="ct"><span class=".*?">.*?</span></td>.*?<td class="ct"><span class=".*?">.*?</span></td>.*?<td class="ct"><span class=".*?">(.*?)</span></td>'
            res_1 = re.findall(pattern=patt, string=res.text, flags=re.S)
            # print(res_1)

            # create db
            df = pd.DataFrame(columns=['Industries', 'pct change','color'])
            ind = []
            pct = []
            color = []

            for x in res_1:
                temp_ind = x[0]
                temp_pct = x[1].replace('- -','')
                temp_pct = float(x[1].replace('%',''))

                if temp_pct >= 0.0:
                    color.append('#f94144')
                else:
                    color.append('#43aa8b')

                ind.append(temp_ind)
                pct.append(temp_pct)

            df['Industries'] = ind
            df['color'] = color
            df['pct change'] = pct
            df['pct change'] = df['pct change'].fillna(0)
            df = df.sort_values('pct change', ascending=False)

            # filter up, down, & TAIEX
            df.at[0,'color'] = '#e9c46a'
            up = df.loc[df['pct change']>=0]
            down = df.loc[df['pct change']<0]
            # display(df)

            # Make fig
            trace1 = go.Bar(x=up['Industries'], 
                            y=up['pct change'], 
                            name='Rising',
                            marker_color = up['color'],
                            text=up['pct change'],
                            textposition="outside",
                            cliponaxis=False
                            )
            trace2 = go.Bar(x=down['Industries'], 
                            y=down['pct change'], 
                            name='Falling',
                            marker_color = down['color'],
                            text=down['pct change'],
                            textposition="outside",
                            cliponaxis=False
                            )

            data1 = [trace1, trace2]
            layout = go.Layout(title="<b>Industries Index Change Rate</b>",
                                title_x=0.5,
                                title_font_size=20,
                                template="ygridoff",
                                showlegend=False,
                                # xaxis=dict(title=update),
                                yaxis=dict(title="<b>Percentage(%)</b>"),
                                # yaxis2=dict(title="<b>Percentage Difference(%)</b>", overlaying="y", side="right",),
                                # legend=dict(x=0.6, y=1.025, yanchor="bottom", orientation="h"),
                                paper_bgcolor='rgba(255,255,255,0.5)',
                                plot_bgcolor='rgba(255,255,255,0.5)',
                                # margin=dict(l=45, r=50, t=50, b=40),
                                hovermode="x unified",
                                )

            fig = go.Figure(data=data1, layout=layout)
            fig.update_xaxes(showgrid = True, tickangle = 90)

            return fig

        industries_index_fig = industries_index()
        st.plotly_chart(industries_index_fig, use_container_width=True)

        @st.experimental_singleton
        def net_buy_sell(url, title):
            url = url
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            }

            res = requests.get(url=url, headers=header)
            res.encoding = res.apparent_encoding
            # print(res.text)

            # 用正則表達式爬取
            patt = r'<TR>.*?<td class=".*?">.*?</TD>.*?<td class=".*?"><a href=".*?">(.*?)</a></TD>.*?<td class=".*?">(.*?)</TD>.*?<td class=".*?">.*?</TD>.*?<td class=".*?">.*?</td>.*?<td class=".*?">.*?</TD>.*?<td class=".*?"><a href=".*?">(.*?)</a></TD>.*?<td class=".*?">(.*?)</TD>.*?<td class=".*?">.*?</TD>.*?<td class=".*?">.*?</td>.*?</tR>'
            res_1 = re.findall(pattern=patt, string=res.text, flags=re.S)
            # print(res_1)

            # create db
            df = pd.DataFrame(columns=['stock', 'shares', 'color'])
            stock = []
            shares = []
            color = []

            for x in res_1[:10]:
                temp_stock = x[0]
                temp_shares = int(x[1].replace(',',''))

                if temp_shares >= 0.0:
                    color.append('#f94144')
                else:
                    color.append('#43aa8b')

                stock.append(temp_stock)
                shares.append(temp_shares)

                temp_stock = x[2]
                temp_shares = int(x[3].replace(',',''))

                if temp_shares >= 0.0:
                    color.append('#f94144')
                else:
                    color.append('#43aa8b')

                stock.append(temp_stock)
                shares.append(temp_shares)

            df['stock'] = stock
            df['shares'] = shares
            df['color'] = color
            df = df.sort_values('shares', ascending=False)
            # display(df)

            # Make fig
            trace1 = go.Bar(x=df['stock'], 
                    y=df['shares'], 
                    # name='Rising',
                    marker_color = df['color'],
                    text=df['shares'],
                    textposition="outside",
                    cliponaxis=False
                    )

            data1 = [trace1]
            layout = go.Layout(title=title,
                        title_x=0.5,
                        title_font_size=20,
                        template="ygridoff",
                        showlegend=False,
                        # xaxis=dict(title=update),
                        yaxis=dict(title="<b>Shares</b>"),
                        # yaxis2=dict(title="<b>Percentage Difference(%)</b>", overlaying="y", side="right",),
                        # legend=dict(x=0.6, y=1.025, yanchor="bottom", orientation="h"),
                        paper_bgcolor='rgba(255,255,255,0.5)',
                        plot_bgcolor='rgba(255,255,255,0.5)',
                        # margin=dict(l=45, r=50, t=50, b=40),
                        hovermode="x unified",
                        )

            fig = go.Figure(data=data1, layout=layout)
            fig.update_xaxes(showgrid = True, tickangle = 90)

            # fig.show()

            return fig
        
        # Foreign investors
        fig1 = net_buy_sell('http://fubon-ebrokerdj.fbs.com.tw/z/zg/zgk.djhtm?A=d&B=0&C=1', "<b>Foreign Investors Net Buying/Selling</b>")
        # Securities Trust
        fig2 = net_buy_sell('http://fubon-ebrokerdj.fbs.com.tw/Z/ZG/ZGK_DB.djhtm', "<b>Securities Trust Net Buying/Selling</b>")
        # Securities Dealers
        fig3 = net_buy_sell('http://fubon-ebrokerdj.fbs.com.tw/Z/ZG/ZGK_DD.djhtm', "<b>Securities Dealers Net Buying/Selling</b>")

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)

# --------------------------------- Update data --------------------------------- #

# if update:
#     st.legacy_caching.caching.clear_cache()
#     tw_industries()


