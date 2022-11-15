"""
General controls
"""

import streamlit as st
from wrappers import sessionize
from core import to_pickle, get
import eco_helper.enrich.visualise as visualise 

session = st.session_state

@sessionize(label = "figure_settings" )
def scatter_figure_controls(container = st):
    """
    Controls for the figure.

    Returns
    -------
    dict    
        A dictionary of figure settings.
    """
    col1, col2 = container.columns(2)

    backend = col1.selectbox( "Backend", [ "plotly", "matplotlib" ], help = "The backend to use for plotting." )
    xlabel = col1.text_input( "x-Label", value = "log2(score)", help = "The label for the x-axis" )
    ylabel = col1.text_input( "y-Label", value = "-log10(qval)", help = "The label for the y-axis" )
    padding = col2.slider( "Width padding", min_value = 0.0, max_value = 10.0, value = 3.0, step = 0.1, help = "The padding between the figure and the edge of the page" )

    settings = dict(  backend = backend, xlabel = xlabel, ylabel = ylabel, padding = padding )

    if backend == "matplotlib":
        x_size = col2.slider( "Figure width", min_value = 5, max_value = 30, value = 10, help = "The width of the figure" )
        y_size = col2.slider( "Figure height", min_value = 2, max_value = 30, value = 4, help = "The height of the figure" )
        despine = col2.checkbox( "Despine", value = True, help = "Remove the top and right spines" )
        palette = col1.text_input( "Palette", value = "colorblind", help = "The palette to use for the plot" )
        settings.update( dict( figsize = (x_size, y_size), despine = despine, palette = palette ) )
    
    return settings

def download_figure( fig, filename = None, suffix = None, container = st):
    """
    Download summary figure.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure or plotly.graph_objects.Figure
        The figure to download.
    filename : str
        The filename to save the figure as. If none is provided, the filename is assembled from the currently loaded dataset.
    suffix : str
        A suffix to append to the filename.
    container : streamlit.container
        The container to use for the controls.
    """
    if filename is None:
        dataset = get( "gene_set" )
        ecotype = dataset._ecotype
        celltype = dataset._celltype
        filename = f"{ecotype}_{celltype}"

    if suffix is not None:
        filename = f"{filename}.{suffix}"
        
    if not fig:
        return
    if visualise.backend == "plotly":
        container.download_button( "Download Figure (html)", fig.to_html(), mime="text/html", file_name = f"{filename}.html" )
        picklefig = to_pickle( fig )

    else:
    #     download = container.button( "Download Figure (png)", key = filename )
    #     if download:
    #         fig.savefig( f"{filename}.png", dpi = 500 )
        picklefig = to_pickle( fig )

    container.download_button( "Download Figure (pickle)", picklefig, mime="bytes", file_name = f"{filename}.{visualise.backend}.p" )