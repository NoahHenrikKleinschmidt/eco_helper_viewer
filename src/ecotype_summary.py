"""
Controls for the ecotype summary page.
"""

import streamlit as st
from wrappers import sessionize
from core import check, get, to_pickle
import controls 
import eco_helper.enrich.visualise as visualise

session = st.session_state

@sessionize(label = "ecotype_summary_settings")
def figure_settings(container = st):

    container.markdown("----")

    col1, col2 = container.columns(2)

    collection = get("collection")
    datacols = list( collection["E1"].columns )

    xcols = list(datacols)
    xcols.remove( "log2_score" )
    xcols.insert( 0, "log2_score" )
    x = col1.selectbox( "x-column", options = xcols, help = "The column to use for the x-axis" )

    ycols = list(datacols)
    ycols.remove( "log10_qval" )
    ycols.insert( 0, "log10_qval" )
    y = col2.selectbox( "y-column", options = ycols, help = "The column to use for the y-axis" )
    
    
    huecols = list(datacols)
    huecols.remove( "CellType" )
    huecols.insert( 0, "CellType" )
    hue = col1.selectbox( "Hue", options = huecols, help = "The column to use for the hue" )
    
    stylecols = list(datacols)
    stylecols.insert(0, None)
    style = col2.selectbox( "Style", options = stylecols, help = "The column to use for the marker-style" )
    
    size = col1.selectbox( "Size", options = stylecols, help = "The column to use for the marker-size" )

   
    return dict( x = x, y = y, hue = hue, style = style, size = size )

# @sessionize(label = "raw_figure" )
def view_scatterplots(container = st):
    """
    View the summary of the collection.
    """
    collection = get( "collection" )
    if not collection:
        return 
    
    settings = dict( get( "figure_settings" ) ) 
    settings.update( get( "ecotype_summary_settings" ) ) 

    visualise.backend = settings.pop( "backend" )

    if visualise.backend == "plotly":
        settings.pop("padding")
        fig = visualise.collection_scatterplot( collection, **settings )
        container.plotly_chart( fig, use_container_width = True )
    else:
        padding = settings.pop( "padding" )
        despine = settings.pop( "despine" )
        fig = visualise.collection_scatterplot( collection, **settings )
        fig.tight_layout( pad = padding )
        if despine:
            visualise.sns.despine()

        container.pyplot( fig, dpi = 500 )
    return fig


def view_gene_sets(container = st):
    """
    View topmost enriched gene sets for each cell type in each ecotype
    """
    collection = get( "collection" )
    if not collection:
        return 

    settings = dict( get( "figure_settings" ) ) 
    settings.update( get( "ecotype_summary_settings" ) )

    visualise.backend = settings.pop( "backend", "plotly" )

    col1, col2, col3 = container.columns((1, 2, 6))
    ecotype = col1.selectbox( "Ecotype", options = list(collection.keys()) )
    view_n_topmost( col2 )

    if visualise.backend == "plotly":
        fig = _plotly_gene_sets_of_ecotype( ecotype, collection[ecotype] )
        container.plotly_chart( fig, use_container_width = True )

    if visualise.backend == "matplotlib":
        fig = _matplotlib_gene_sets_of_ecotype( ecotype, collection[ecotype] )
        container.pyplot( fig, dpi = 500 )
    
    return fig

@sessionize
def view_n_topmost(container = st):
    return container.number_input( "Topmost", min_value = 1, max_value = 50, value = 5, help = "The number of topmost enriched gene sets to show for each cell-type/state in each ecotype" )


def _matplotlib_gene_sets_of_ecotype( ecotype, df ):
    """
    Plot the topmost enriched gene sets for each cell type in the given ecotype
    """
    settings = dict( get( "figure_settings" ) )
    settings.update( get( "ecotype_summary_settings" ) )

    plt = visualise.plt
    sns = visualise.sns
    pd = visualise.pd

    n = get( "view_n_topmost" )
    x, y = settings.get("x"), settings.get("y")
    despine = settings.pop( "despine" )

    fig, ax = plt.subplots( figsize = settings.pop("figsize", None) )
    groups = df.groupby( settings.get("hue") )
    df = []
    for celltype, group in groups:
        group = group.sort_values( by = x, ascending = False )
        group = group.sort_values( by = y, ascending = False )
        group = group.head( int(n) )
        df.append( group )
    df = pd.concat( df )

    sns.scatterplot(    data = df, 
                        x = x, y = "Term", 
                        hue = "CellType", 
                        size = y, 
                        legend = True,
                        sizes = (100, 300),
                        ax = ax )
    ax.set( xlabel = settings.get("xlabel", x), ylabel = "" )
    ax.grid( axis = "both" )
    ax.legend( bbox_to_anchor = (1.01, 1), loc = 2, frameon = False )

    if despine:
        for spine in ax.spines.values():
            spine.set_linewidth(0.3)

    return fig

def _plotly_gene_sets_of_ecotype( ecotype, df ):
    """
    Plot the topmost enriched gene sets for each cell type in the given ecotype
    """
    import plotly.graph_objs as go

    settings = get( "figure_settings" )
    settings.update( get( "ecotype_summary_settings" ) ) 
    n = get( "view_n_topmost" )

    x, y = settings.get("x"), settings.get("y")

    fig = go.Figure()
    groups = df.groupby( settings.get("hue") )
    for celltype, group in groups:
        group = group.sort_values( by = x, ascending = False )
        group = group.sort_values( by = y, ascending = False )
        group = group.head( int(n) )
        
        fig.add_trace( go.Scatter( 
                                    x = group[x], y = group["Term"], 
                                    name = celltype,
                                    mode='markers',
                                    marker=dict(
                                        size=group[y],
                                        sizemode='area',
                                        sizeref=2.*max(group[y])/(20.**2),
                                        sizemin=2,
                                    ),
                                    text = group["Term"],
                                        hoverinfo = "name+text+z+x",
                                    ) )
    fig.update_layout(
        title = f"Topmost enriched gene sets for each cell type in {ecotype}",
        xaxis_title = settings.get("xlabel", x),
    )   

    return fig
