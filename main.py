import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_excel('asset/Mlbb_Heroes.xlsx')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Visualisasi Data Heroes MLBB Patch 1.7.20 September, 20 2022."),
    html.Label("Pilih Role Hero (Termasuk Secondary Role):"),
    dcc.Dropdown(
        id='primary-role-dropdown',
        options=[{'label': role, 'value': role}
                 for role in df['Primary_Role'].unique()],
        value=df['Primary_Role'].unique()[0],
        multi=False
    ),
    html.Div([
        dcc.Graph(id='esport-wins-graph'),
        dcc.Graph(id='winning-percentage-pie'),
    ]),
    html.Label("Pilih Nama Hero :"),
    dcc.Dropdown(
        id='hero-dropdown',
        options=[{'label': hero, 'value': hero}
                 for hero in df['Name'].unique()],
        value=df['Name'].unique()[0],
        multi=False
    ),
    html.Div(dcc.Graph(id='attribute-radar-chart'))
])


@app.callback(
    [dash.dependencies.Output('esport-wins-graph', 'figure'),
     dash.dependencies.Output('winning-percentage-pie', 'figure'),
     dash.dependencies.Output('attribute-radar-chart', 'figure')],
    [dash.dependencies.Input('primary-role-dropdown', 'value'),
     dash.dependencies.Input('hero-dropdown', 'value')]
)
def update_graph(primary_role, hero):
    data_filter = df[(df['Primary_Role'] == primary_role) |
                     (df['Secondary_Role'] == primary_role)]

    max_win = data_filter['Esport_Wins'].max()
    min_win = data_filter['Esport_Wins'].min()
    nilai_rata_win = (data_filter['Esport_Wins'] -
                      min_win) / (max_win - min_win)

    colors = px.colors.diverging.RdBu[::-1]
    colorscale = [[i, colors[int(i * (len(colors) - 1))]]
                  for i in nilai_rata_win]

    bar = px.bar(data_filter, x='Name', y='Esport_Wins',
                 color=nilai_rata_win, color_continuous_scale=colorscale,
                 labels={'Esport_Wins': 'Jumlah Kemenangan Esport'},
                 title=f"Esport Wins of {primary_role} Heroes",
                 template='plotly_white')

    bar.update_layout(coloraxis_colorbar=dict(
        title="Jumlah Kemenangan Esport"))

    role_counts = df['Primary_Role'].value_counts()
    winning_percentage = (df.groupby('Primary_Role')[
                          'Esport_Wins'].sum() / role_counts) * 100
    pie_fig = px.pie(names=winning_percentage.index, values=winning_percentage.values,
                     title='Persentase Kemenangan Esport Berdasarkan Role.',
                     labels={'names': 'Primary Role', 'values': 'Winning Percentage'})

    pie_fig.update_traces(textinfo='percent+label')

    hero_attributes = df[df['Name'] == hero][['Hp_Regen', 'Mana_Regen', 'Phy_Damage', 'Mag_Damage',
                                              'Phy_Defence', 'Mag_Defence', 'Mov_Speed']].iloc[0]

    categories = hero_attributes.index.tolist()
    values = hero_attributes.values.tolist()

    spider = go.Figure()
    spider.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=hero
    ))

    spider.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values)],
            )),

    )

    spider.update_layout(title=f'Profile Hero {hero}')

    return bar, pie_fig, spider


if __name__ == '__main__':
    app.run_server(debug=True)
