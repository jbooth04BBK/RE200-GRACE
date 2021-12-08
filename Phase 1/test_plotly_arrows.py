import plotly.offline as py
import plotly.graph_objs as go

trace = go.Scatter(
    x=[1, 2, 2, 1],
    y=[3, 4, 3, 4],
    mode='markers',
    marker=dict(size=[100, 100, 100, 100])
)

# Edges
x0 = [1, 2]
y0 = [3, 3]
x1 = [2, 1]
y1 = [4, 4]

head_fraction = 0.51
tail_fraction = 0.49

fig = go.Figure(
    data=[trace],
    layout=go.Layout(
        annotations = [

            # dict(ax=(x0[i] + x1[i])/2, ay=(y0[i]+y1[i])/2, axref='x', ayref='y', # tail of arrow
            #      x=((x1[i]*3) + x0[i]) / 4, y=((y1[i]*3) + y0[i])/4, xref='x', yref='y', # head of arrow
            #      showarrow=True,
            #      arrowhead=1,
            #      arrowsize=2,
            #      arrowwidth=1,
            #      opacity=1
            #      ) for i in range(0, len(x0))

            dict(ax=(x0[i] + ((x1[i] - x0[i]) * tail_fraction)), ay=(y0[i] + ((y1[i] - y0[i]) * tail_fraction)), axref='x', ayref='y',  # tail of arrow
                 x=(x0[i] + ((x1[i] - x0[i]) * head_fraction)), y=(y0[i] + ((y1[i] - y0[i]) * head_fraction)), xref='x', yref='y',  # head of arrow
                 showarrow=True,
                 arrowhead=1,
                 arrowsize=2,
                 arrowwidth=1,
                 opacity=1
                 )
            for i in range(0, len(x0))

                    ]
                )
            )
py.plot(fig)