import pandas as pd
import geopandas as gpd
import plotly.express as px

from dash import Dash, dcc, html, Input, Output 
import dash_bootstrap_components as dbc

#load data from saved excel files (f.ex. data scaled by population) with index

df = pd.read_excel("Data/df_merged.xlsx", index_col = [0,1,2])
df_per_area = pd.read_excel("Data/df_by_area.xlsx", index_col = [0,1,2])
df_per_pop = pd.read_excel("Data/df_by_population.xlsx", index_col = [0,1,2])

#zeros are removed from the beginning key_1 when loading from excel file. They needed to be added again.
df = df.reset_index(inplace=False)
df["key_1"] = df["key_1"].map(lambda x: "0"+str(x) if len(str(x))<6 else str(x))
df_per_pop = df_per_pop.reset_index(inplace=False)
df_per_pop["key_1"] = df_per_pop["key_1"].map(lambda x: "0"+str(x) if len(str(x))<6 else str(x))
df_per_area = df_per_area.reset_index(inplace=False)
df_per_area["key_1"] = df_per_area["key_1"].map(lambda x: "0"+str(x) if len(str(x))<6 else str(x))

#importing Berlin Bezirksregionen spatial data
Bezirksregionen_spatial = gpd.read_file("./Data/LOR/lor_shp_2019/Bezirksregion_EPSG_25833.shp")
Bezirksregionen_spatial.crs = "epsg:25833"
Bezirksregionen_spatial = Bezirksregionen_spatial.to_crs(epsg=4326)

#cleaning dataframe
Bezirksregionen_spatial = Bezirksregionen_spatial.rename(columns={'SCHLUESSEL': 'key_2'})
Bezirksregionen_spatial = Bezirksregionen_spatial[['key_2', 'geometry']]

#merging spatial data with df_keys on key_2
df_keys = pd.read_excel("Data/df_keys.xlsx", index_col = [0])
df_keys["key_1"] = df_keys["key_1"].map(lambda x: "0"+str(x) if len(str(x))<6 else str(x))
df_keys["key_2"] = df_keys["key_2"].map(lambda x: "0"+str(x) if len(str(x))<6 else str(x))
Bezirksregionen_spatial = pd.merge(Bezirksregionen_spatial, df_keys, on = ['key_2', 'key_2'])
df_spatial = Bezirksregionen_spatial.dissolve(by='key_1')
df_spatial.reset_index(inplace=True)

#simplify geometry to run dashboard choropleth map faster
df_spatial["geometry"] = df_spatial["geometry"].simplify(1)

#merging spatial data with df on key_1
df_spatial_temp = df_spatial.copy()
df_spatial = pd.merge(df_spatial, df, on = ['key_1', 'key_1'])
df_spatial_per_pop = pd.merge(df_spatial_temp, df_per_pop, on = ['key_1', 'key_1'])
df_spatial_per_area = pd.merge(df_spatial_temp, df_per_area, on = ['key_1', 'key_1'])


#load prediction data from saved excel files with index
df_pred_prophet = pd.read_excel("Data/df_prophet_predictions.xlsx", index_col = [0,1,2])

#load Random Forest algorithm's feature_importances
#df_RF_feature_importances = pd.read_excel("Data/df_RF_feature_importances.xlsx", index_col = [0])
df_RF_feature_importances = pd.read_excel("Data/H20AutoML_treemodels_importances.xlsx", index_col = [0])

#rename variables to make them more easily comprehensible for dashboard readers

df_spatial = df_spatial.rename(columns={"E insgesamt": "Total Population",
                                        "weiblich": "Female Population",
                                        "männlich": "Male Population",
                                        "E_U1": "Population  Infants",
                                        "E_1U6": "Population ages 1-6",
                                        "E_6U15": "Population ages 6-15",
                                        "E_15U18": "Population ages 15-18",
                                        "E_18U25": "Population ages 18-25",
                                        "E_25U35": "Population ages 25-35",
                                        "E_35U45": "Population ages 35-45",
                                        "E_45U55": "Population ages 45-55",
                                        "E_55U65": "Population ages 55-65",
                                        "E_65U80": "Population ages 65-80",
                                        "E_80U110": "Population ages 80-110",
                                        "WLEINF": "Simple residential area",
                                        "WLMIT": "Average residential area",
                                        "WLGUT": "Good residential area",
                                        "WLNZORD": "Residential area without allocation",
                                        "area": "Area in square kilometers",
                                        "num_street_lights": "Number of street lights",
                                        "Einzelhandel mit Tabakwaren" : "Tobacco retail dealers",
                                        "Einzelhandel mit Getränken" : "Liquor stores",
                                        "Ausschank von Getränken" : "Bars, pubs and clubs",
                                        "Spiel-, Wett- und Lotteriewesen" : "Casinos and betting stores",
                                        "Unfall mit Leichtverletzten": "Accidents with minor injuries",
                                        "Unfall mit Schwerverletzten": "Accidents with major injuries",
                                        "Unfall mit Getöteten": "Accidents resulting in deaths",
                                       })

df_spatial_per_pop = df_spatial_per_pop.rename(columns={"weiblich": "Female Population",
                                        "männlich": "Male Population",
                                        "E_U1": "Population  Infants",
                                        "E_1U6": "Population ages 1-6",
                                        "E_6U15": "Population ages 6-15",
                                        "E_15U18": "Population ages 15-18",
                                        "E_18U25": "Population ages 18-25",
                                        "E_25U35": "Population ages 25-35",
                                        "E_35U45": "Population ages 35-45",
                                        "E_45U55": "Population ages 45-55",
                                        "E_55U65": "Population ages 55-65",
                                        "E_65U80": "Population ages 65-80",
                                        "E_80U110": "Population ages 80-110",
                                        "WLEINF": "Simple residential area",
                                        "WLMIT": "Average residential area",
                                        "WLGUT": "Good residential area",
                                        "WLNZORD": "Residential area without allocation",
                                        "area": "Area in square kilometers",
                                        "num_street_lights": "Number of street lights",
                                        "Einzelhandel mit Tabakwaren" : "Tobacco retail dealers",
                                        "Einzelhandel mit Getränken" : "Liquor stores",
                                        "Ausschank von Getränken" : "Bars, pubs and clubs",
                                        "Spiel-, Wett- und Lotteriewesen" : "Casinos and betting stores",
                                        "Unfall mit Leichtverletzten": "Accidents with minor injuries",
                                        "Unfall mit Schwerverletzten": "Accidents with major injuries",
                                        "Unfall mit Getöteten": "Accidents resulting in deaths",
                                       })

df_spatial_per_area = df_spatial_per_area.rename(columns={"E insgesamt": "Total Population",
                                        "weiblich": "Female Population",
                                        "männlich": "Male Population",
                                        "E_U1": "Population  Infants",
                                        "E_1U6": "Population ages 1-6",
                                        "E_6U15": "Population ages 6-15",
                                        "E_15U18": "Population ages 15-18",
                                        "E_18U25": "Population ages 18-25",
                                        "E_25U35": "Population ages 25-35",
                                        "E_35U45": "Population ages 35-45",
                                        "E_45U55": "Population ages 45-55",
                                        "E_55U65": "Population ages 55-65",
                                        "E_65U80": "Population ages 65-80",
                                        "E_80U110": "Population ages 80-110",
                                        "WLEINF": "Simple residential area",
                                        "WLMIT": "Average residential area",
                                        "WLGUT": "Good residential area",
                                        "WLNZORD": "Residential area without allocation",
                                        "num_street_lights": "Number of street lights",
                                        "Einzelhandel mit Tabakwaren" : "Tobacco retail dealers",
                                        "Einzelhandel mit Getränken" : "Liquor stores",
                                        "Ausschank von Getränken" : "Bars, pubs and clubs",
                                        "Spiel-, Wett- und Lotteriewesen" : "Casinos and betting stores",
                                        "Unfall mit Leichtverletzten": "Accidents with minor injuries",
                                        "Unfall mit Schwerverletzten": "Accidents with major injuries",
                                        "Unfall mit Getöteten": "Accidents resulting in deaths",
                                       })

#Create Dashboard with Plotly Express and Dash Bootstrap Components

dff = df_spatial.copy()
dff_per_pop = df_spatial_per_pop.copy()
dff_per_area = df_spatial_per_area.copy()

df_names = ["Total", "Per capita", "Per square kilometer"]

dff_predictions = df_pred_prophet.copy()

Bezirksregionen_names = []
for Bezirksregion in dff_predictions.index.get_level_values('Bezirksregion').unique():
    temp = [{"label": Bezirksregion, "value": Bezirksregion},]
    Bezirksregionen_names = Bezirksregionen_names+temp
    
variable_names = []
for variable in dff.columns:
    if variable != "Total Population" and variable != "Area in square kilometers" and variable != "key_1" and variable != "geometry" and variable != "key_2" and variable != "year" and variable != "Bezirksregion":
        temp = [{"label": variable, "value": variable},]
        variable_names = variable_names+temp

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

title = dcc.Markdown(children = "Berlin Crime Dashboard", style={'color': 'white', 'text-align': 'center'})

title_fig1 = dcc.Markdown(children = "Top 5 types of crimes committed in each district", style={'color': 'white', 'text-align': 'center'})
title_fig2 = dcc.Markdown(children = "Districts with highest crime rates for each type of crime", style={'color': 'white', 'text-align': 'center'})
title_fig3 = dcc.Markdown(children = "Crime rates and prediction 2012-2025 for each district", style={'color': 'white', 'text-align': 'center'})
title_fig4 = dcc.Markdown(children = "H2O AutoML best tree model's variable importance for each type of crime", style={'color': 'white', 'text-align': 'center'})
title_fig5 = dcc.Markdown(children = "Crime Map Berlin", style={'color': 'white', 'text-align': 'center'})


dropdown_region_top = dcc.Dropdown(id="slct_dropdown_region_top",
                                 searchable=True,
                                 options=Bezirksregionen_names,
                                 multi=False,
                                 value="Parkviertel",
                                 style={'width': "100%",
                                       'backgroundColor': 'black', 
                                        'color': 'black'})

pie_top_region = dcc.Graph(id='fig_pie_top_region',style={'display': 'inline-block'})

slider_top_region = dcc.Slider(min=dff['year'].min(),
                        max=dff['year'].max(),
                        step=None,
                        value=dff['year'].max(),
                        marks={str(year): str(year) for year in dff['year'].unique()},
                        id='slct_slider_top_region')

dropdown_type_top = dcc.Dropdown(id="slct_dropdown_type_top",
                                 searchable=True,                                 
                                 options=variable_names[:17],
                                 multi=False,
                                 value="Straftaten insgesamt",
                                 style={'width': "100%",
                                       'backgroundColor': 'black', 
                                        'color': 'black'})

barchart_top_type = dcc.Graph(id='fig_barchart_top_type',style={'display': 'inline-block'})

slider_top_type = dcc.Slider(min=dff['year'].min(),
                        max=dff['year'].max(),
                        step=None,
                        value=dff['year'].max(),
                        marks={str(year): str(year) for year in dff['year'].unique()},
                        id='slct_slider_top_type')


dropdown_region_pred = dcc.Dropdown(id="slct_dropdown_region_pred",
                                    searchable=True,
                                    options=Bezirksregionen_names,
                                    multi=False,
                                    value="Alexanderplatz",
                                    style={'width': "100%",
                                       'backgroundColor': 'black', 
                                        'color': 'black',
                                        'display': 'inline-block'},)

dropdown_type_pred = dcc.Dropdown(id="slct_dropdown_type_pred",
                                  searchable=True,
                                  options=variable_names[:17],
                                  multi=False,
                                  value="Raub",
                                  style={'width': "100%",
                                       'backgroundColor': 'black', 
                                        'color': 'black'})

graph_barchart_prediction = dcc.Graph(id='fig_barchart_prediction',style={'display': 'inline-block'})

dropdown_type_RF_importance = dcc.Dropdown(id="slct_dropdown_type_RF_importance",
                                  searchable=True,
                                  options=variable_names[:17],
                                  multi=False,
                                  value="Sachbeschädigung insgesamt",
                                  style={'width': "100%",
                                       'backgroundColor': 'black', 
                                        'color': 'black'})

pie_RF_importance = dcc.Graph(id='fig_pie_RF_importance',style={'display': 'inline-block'})

dropdown_df_map = dcc.Dropdown(id="slct_dropdown_df_map",
                                 searchable=True,
                                 options=df_names,
                                 multi=False,
                                 value="Per square kilometer",
                                 style={'width': "100%",
                                       'backgroundColor': 'black', 
                                        'color': 'black',
                                        'justify-content': 'center'})

dropdown_type_map = dcc.Dropdown(id="slct_dropdown_type_map",
                                 searchable=True,
                                 options=variable_names,
                                 multi=False,
                                 value="Sachbeschädigung durch Graffiti",
                                 style={'width': "100%",
                                       'backgroundColor': 'black', 
                                        'color': 'black',
                                        'justify-content': 'center'})
            
graph_map = dcc.Graph(id='fig_map', figure={}, style={})

slider_map = dcc.Slider(min=dff['year'].min(),
                        max=dff['year'].max(),
                        step=None,
                        value=dff['year'].max(),
                        marks={str(year): str(year) for year in dff['year'].unique()},
                        id='slct_slider_map')
app.layout = html.Div(dbc.Card(dbc.CardBody([dbc.Row([title]), 
                                             html.Br(),
                                             dbc.Row([
                                                 dbc.Col([title_fig1], width = 5),
                                                 dbc.Col([], width = 1),
                                                 dbc.Col([title_fig2], width=5),                                             
                                             ]),
                                             dbc.Row([
                                                 dbc.Col([dropdown_region_top], width = 5),
                                                 dbc.Col([], width = 1),
                                                 dbc.Col([dropdown_type_top], width=5),
                                             ]),
                                             dbc.Row([
                                                 dbc.Col([pie_top_region], width = 5),
                                                 dbc.Col([], width = 1),
                                                 dbc.Col([barchart_top_type], width = 5),
                                             ]),
                                             dbc.Row([
                                                 dbc.Col([slider_top_region], width=4),
                                                 dbc.Col([], width = 2),
                                                 dbc.Col([slider_top_type], width=4),
                                             ]),
                                             html.Br(),
                                             dbc.Row([
                                                 dbc.Col([title_fig3], width = 5),
                                                 dbc.Col([], width = 1),
                                                 dbc.Col([title_fig4], width=5),                                             
                                             ]),
                                             dbc.Row([
                                                 dbc.Col([dropdown_region_pred], width=5),
                                                 dbc.Col([], width = 1),
                                                 dbc.Col([dropdown_type_RF_importance], width = 5),
                                             ]),
                                             dbc.Row([
                                                 dbc.Col([dropdown_type_pred], width = 5),
                                                 dbc.Col([], width = 6),
                                             ]),
                                             dbc.Row([
                                                 dbc.Col([pie_RF_importance], width = 5),                                                
                                                 dbc.Col([], width = 1),
                                                 dbc.Col([graph_barchart_prediction], width = 5),
                                             ]),
                                             html.Br(),
                                             dbc.Row([
                                                 dbc.Col([], width = 2),
                                                 dbc.Col([title_fig5], width = 7),
                                                 dbc.Col([], width=2),                                             
                                             ]),
                                             dbc.Row([
                                                 dbc.Col([], width = 3),
                                                 dbc.Col([dropdown_df_map], width = 5),
                                                 dbc.Col([], width = 3),
                                             ]),
                                             dbc.Row([
                                                 dbc.Col([], width = 3),
                                                 dbc.Col([dropdown_type_map], width = 5),
                                                 dbc.Col([], width = 3),
                                             ]),
                                             dbc.Row([graph_map]),
                                             dbc.Row([
                                                 dbc.Col([], width = 2),
                                                 dbc.Col([slider_map], width = 7)]),
                                                 dbc.Col([], width = 2),
                                             ]), color = 'black',),)

# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output('fig_pie_top_region', 'figure'),
            Output('fig_barchart_top_type', 'figure'),
            Output('fig_pie_RF_importance', 'figure'),
            Output('fig_barchart_prediction', 'figure'),
            Output('fig_map', 'figure')],
    
    [Input('slct_dropdown_region_top', 'value'), Input('slct_slider_top_region', 'value'),
         Input('slct_dropdown_type_top', 'value'), Input('slct_slider_top_type', 'value'),
         Input('slct_dropdown_region_pred', 'value'), Input('slct_dropdown_type_pred', 'value'), Input('slct_dropdown_type_RF_importance', 'value'),
         Input('slct_dropdown_df_map', 'value'), Input('slct_dropdown_type_map', 'value'), Input('slct_slider_map', 'value')]
)
def update_graph(slct_dropdown_region_top, slct_slider_top_region,
                 slct_dropdown_type_top, slct_slider_top_type,
                 slct_dropdown_region_pred, slct_dropdown_type_pred, slct_dropdown_type_RF_importance,
                 slct_dropdown_df_map, slct_dropdown_type_map, slct_slider_map):
    
    dff = df_spatial.copy()
    dff_per_pop = df_spatial_per_pop.copy()
    dff_per_area = df_spatial_per_area.copy()
    dff_predictions = df_pred_prophet.copy()
    dff_RF_feature_imp = df_RF_feature_importances.copy().T
    
    dff_top_region_columns = dff[dff["year"] == slct_slider_top_region][dff["Bezirksregion"] == slct_dropdown_region_top].columns.values.tolist()[6:22]
    dff_top_region = dff[dff["year"] == slct_slider_top_region][dff["Bezirksregion"] == slct_dropdown_region_top].iloc[:,6:22].iloc[:1].values.flatten().tolist()
    srs = pd.Series(dff_top_region)
    top_idx = srs.nlargest(5).index.values.tolist()
    remaining_idx = srs.nsmallest(11).index.values.tolist()
    remaining_sum = sum(srs[remaining_idx])
    values_pie = srs[top_idx].tolist()+[remaining_sum]
    names_pie = [dff_top_region_columns[i] for i in top_idx]+['Remaining']
    
    dff_RF_feature_imp = dff_RF_feature_imp[slct_dropdown_type_RF_importance]
    top_features = dff_RF_feature_imp.nlargest(5)
    top_features["remaining"] = 1-sum(top_features)

    dff_top_type = dff[dff["year"] == slct_slider_top_type].nlargest(10, slct_dropdown_type_top)

    dff_pred_region = dff_predictions[dff_predictions.index.get_level_values("Bezirksregion") == slct_dropdown_region_pred]

    dff_map_year = dff[dff["year"] == slct_slider_map][slct_dropdown_type_map]  
    dff_per_pop_map_year = dff_per_pop[dff_per_pop["year"] == slct_slider_map][slct_dropdown_type_map] 
    dff_per_area_map_year = dff_per_area[dff_per_area["year"] == slct_slider_map][slct_dropdown_type_map]  
    dfs = {"Total": dff_map_year, "Per capita": dff_per_pop_map_year, "Per square kilometer": dff_per_area_map_year}
 
    fig1 = px.pie(values=values_pie, names=names_pie, color_discrete_sequence=px.colors.sequential.RdBu)
    fig1.update_layout(autosize=False, width=600, height=470,)
    fig1.update_layout(template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',)
    fig1.update_traces(textposition='inside', textinfo='percent')
    fig1.update_traces(pull=[0, 0, 0, 0, 0, 0.1])

    fig2 = px.bar(dff_top_type,
                  x = dff_top_type["Bezirksregion"],
                  y = slct_dropdown_type_top,)
    fig2.update_traces(hovertemplate = "District: %{x} <br>Value: %{y}")
    fig2.update_xaxes(title_text = '')
    fig2.update_layout(template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',)
    fig2.update_layout(autosize=False, width=600, height=470,)
    fig2.update_traces(marker_color='darkgreen')
    
    fig3 = px.bar(dff_pred_region,
                 x = dff_pred_region.index.get_level_values('year').unique(),
                 y = slct_dropdown_type_pred,
                 color = (["actual"]*9)+(['forecast']*5),
                 color_discrete_map={
                     'actual': 'darkgreen',
                     'forecast': 'darkred'},
                 labels={'x': 'Year'})
    fig3.update_traces(hovertemplate = "Year: %{x} <br>Value: %{y}")
    fig3.update_layout(showlegend=True)
    fig3.update_layout(template='plotly_dark',
                       plot_bgcolor= 'rgba(0, 0, 0, 0)',
                       paper_bgcolor= 'rgba(0, 0, 0, 0)',)
    fig3.update_layout(autosize=False, width=600, height=400,)

    fig4 = px.pie(values=top_features, names=top_features.index, color_discrete_sequence=px.colors.sequential.RdBu)
    fig4.update_layout(autosize=False, width=600, height=470,)
    fig4.update_layout(template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',)
    fig4.update_traces(textposition='inside', textinfo='percent')
    fig4.update_traces(pull=[0, 0, 0, 0, 0, 0.1])
    
    fig5 = px.choropleth(dfs[slct_dropdown_df_map],
                        geojson=dff.geometry,
                        locations = dfs[slct_dropdown_df_map].index,
                        color = slct_dropdown_type_map,
                        height=500,
                        color_continuous_scale="Hot",
                        hover_name = dff[dff['year'] == slct_slider_map]["Bezirksregion"])  
    
    fig5.update_geos(fitbounds="locations",
                    visible=True)
    fig5.update_layout(template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',)
        
    return fig1, fig2, fig3, fig4, fig5



 # access dashboard at: http://127.0.0.1:8044/

if __name__ == '__main__':
    app.run_server(host="127.0.0.1", debug=True, port=8044)