"""
Controls for the celltype/state gene set explore page.
"""

import streamlit as st
from wrappers import sessionize
import core
import eco_helper.enrich.visualise as visualise
import json

session = st.session_state

session["highlight_subsets"] = {}

@sessionize(label = "which_subsets" )
def show_subset_figures(container = st):
    """
    Controls for showing which plots to show.
    """
    show_scatter = container.checkbox( "Show scatterplot", value = True, help = "Show the term scatterplot." )
    show_counts = False # container.checkbox( "Show counts", value = False, help = "Show the counts of terms associated with subsets." )
    show_topmost = container.checkbox( "Show topmost", value = True, help = "Show the topmost enriched terms (either global or per subset)." )
    show_topmost_table = container.checkbox( "Show topmost table", value = False, help = "Show the topmost enriched terms (either global or per subset) in a table." )
    return dict( scatter = show_scatter, counts = show_counts, topmost = show_topmost, topmost_table = show_topmost_table )


@sessionize(label = "gene_set")
def select_dataset(container = st):
    """
    Select a dataset.
    """
    collection = core.get( "collection" )
    if not collection:
        return 
    ecotypes = list( collection.keys() )
    ecotype = container.selectbox( "EcoType", options = ecotypes )

    datasets = list( collection[ecotype]["CellType"].unique() )
    dataset = container.selectbox( "Celltype/state", options = datasets )
    
    dataset = collection[ecotype].query( f"CellType == '{dataset}'" )

    # dataset["Genes"] = dataset["Genes"].apply( lambda x: x[:50]+"..." )
    return dataset

@sessionize(label = "gene_set_settings")
def figure_settings(container = st):

    container.markdown("----")

    col1, col2 = container.columns(2)

    dataset = core.get( "gene_set" )
    datacols = dataset.columns
    
    rcols = list(datacols)
    rcols.remove( "Term" )
    rcols.insert(0, "Term")
    ref_col = container.selectbox( "Reference column", options = rcols, help = "The column to reference patterns in." )

    xcols = list(datacols)
    xcols.remove( "log2_score" )
    xcols.insert( 0, "log2_score" )
    x = col1.selectbox( "x-column", options = xcols, help = "The column to use for the x-axis" )

    ycols = list(datacols)
    ycols.remove( "log10_qval" )
    ycols.insert( 0, "log10_qval" )
    y = col2.selectbox( "y-column", options = ycols, help = "The column to use for the y-axis" )
    
    stylecols = list(datacols)
    stylecols.insert(0, None)
    style = col2.selectbox( "Style", options = stylecols, help = "The column to use for the marker-style" )
    
    size = col1.selectbox( "Size", options = stylecols, help = "The column to use for the marker-size" )
    return dict( x = x, y = y, style = style, size = size, ref = ref_col )

def subsets_textfield(container = st):
    container.text_area( "Highlighted subsets", value = str( json.dumps( session.get( "highlight_subsets", {} ), indent = 4 ) ), help = "The currently highlighted term-subsets. Note, this is only for display purposes. Editing in this field will have no effect." )

def edit_subsets(container = st):
    """
    Edit the highlighted subsets.
    """

    subsets = core.get( "highlight_subsets" ) 
    if not subsets:
        session["highlight_subsets"] = {}
        subsets = session["highlight_subsets"]
    labels = list( subsets.keys() )
    if "None" in labels:
        labels.remove( "None" )
    labels.insert( 0, "None" )
    
    upload_subsets( st.sidebar )

    label = container.selectbox( "Subset", options = labels, help = "The subset to edit." )
    
    terms = container.text_area( "Patterns to highlight", value = subsets.get(label, ""), help = "Either a single or multiple of `python`-style `regex` patterns to match. This field is interpreted as `python-code`, hence each pattern should be encapsulated by single or double ticks. If multiple patterns are provided, they must be in a `list` or `tuple`. " )
    # multiple_terms = container.checkbox( "contains multiple patterns", help = "If `True`, the terms will be interpreted as a `list` or `tuple` of patterns. If `False`, the terms will be interpreted as a single pattern." )
    try:
        terms = eval( terms.strip() ) #if multiple_terms else [terms.strip()]
    except:
        terms = [terms.strip()]
        if terms == [""]:
            terms = None


    new_label = container.text_input( "New subset label", value = label, placeholder = "New subset", help = "The label of the new subset. This may include spaces and special characters." )
    add_new = container.button( "Save subset", help = "Save the subset to the current selection" )
    drop_subset = container.button( "Drop subset", help = "Drop the subset from the current selection" )
    if add_new:
        subsets[new_label] = terms
        if not new_label == "None":
            subsets.pop( "None", None )
    elif drop_subset:
        subsets.pop( label, None )
    elif terms:
        subsets[label] = terms
    else:
        subsets.pop( "None", None )

    session["highlight_subsets"] = subsets

def upload_subsets(container = st):
    """
    Upload a subset file.
    """
    file = container.file_uploader( "Upload a subset file", help = "Upload a file of subsets to highlight. This must be a python `dictionary` as a blank text file (i.e. a `json` file), containing subset labels as keys and lists of python-`regex` patterns as values (lists of strings). **Note**: Once you have uploaded the file, make sure to remove it using the little `x` symbol next to your uploaded file, otherwise the file will be re-uploaded and any modifications you make to the dictionary (such as adding new terms) will be overwritten each time the app recomputes!" )
    contents = file.read().decode("utf-8") if file else None
    if contents:
        contents = eval( contents )
        session["highlight_subsets"].update( contents ) 

@sessionize
def topmost_thresholds(container = st):
    """
    Set the topmost thresholds.
    """
    container.markdown("----")
    col1, col2, col3 = container.columns(3)
    
    dataset = core.get( "gene_set" )
    x = core.get( "gene_set_settings" )["x"]
    y = core.get( "gene_set_settings" )["y"]
    minx, maxx = float(dataset[x].min()), float(dataset[x].max())
    miny, maxy = float(dataset[y].min()), float(dataset[y].max())
    topx = col1.slider( "x-threshold", min_value = minx, max_value = maxx, value = 0.65 * maxx, step = 0.01, help = "The topmost threshold for the `x` column." )
    topy = col2.slider( "y-threshold", min_value = miny, max_value = maxy, value = 0.65 * maxy, step = 0.01, help = "The topmost threshold for the `y` column." )
    
    n_per_subset = col3.number_input( "Show n per subset", min_value = 0, value = 0, max_value = 50, help = "Use this to show the `n` top-most gene sets in each subset instead of global numeric thresholding. If set to `0` this input is ignored." )

    return topx, topy, n_per_subset

# @sessionize(label = "raw_figure")
def view_subsets(container = st):
    """
    View the current subsets.
    """

    dataset = core.get( "gene_set" )
    subsets = session["highlight_subsets"]
    

    settings = core.get( "gene_set_settings" )
    settings.update( core.get( "figure_settings" ) )

    title = dataset["CellType"].unique()[0]
    ref_col = settings.get("ref")

    despine = settings.pop("despine", False)
    padding = settings.pop("padding", None)
    palette = settings.pop("palette", None)

    visualise.backend = settings.pop("backend")

    plotter = visualise.StateScatterplot(   df = dataset, 
                                            x = settings.get("x"), 
                                            y = settings.get("y"), 
                                            hue = settings.get("hue"), 
                                            style = settings.get("style") )
    
    if visualise.backend == "plotly":
        fig = plotter.highlight( 
                                    ref_col = ref_col,
                                    title = title,
                                    subsets = subsets, 
                                    hover_data = {"Combined Score" : "Combined Score", "Term" : "Term", },
                                    xlabel = settings.get("xlabel", None),
                                    ylabel = settings.get("ylabel", None),
                                )
        container.plotly_chart( fig, use_container_width = True )
    else:
        fig = plotter.highlight( 
                                    ref_col = ref_col,
                                    title = title,
                                    subsets = subsets, 
                                    figsize = settings.get("figsize"),
                                    palette = palette,
                                    xlabel = settings.get("xlabel", None),
                                    ylabel = settings.get("ylabel", None),
                                )
        if despine:
            visualise.sns.despine()
        visualise.plt.tight_layout()
        container.pyplot( fig )

    return fig 

def view_histogram(container = st):

    dataset = core.get( "gene_set" )
    subsets = session["highlight_subsets"]
    

    settings = core.get( "gene_set_settings" )
    settings.update( core.get( "figure_settings" ) )
    thresholds = core.get( "topmost_thresholds" )

    title = "Term Counts per Subset" #dataset["CellType"].unique()[0]
    ref_col = settings.get("ref")

    despine = settings.pop("despine", False)
    padding = settings.pop("padding", None)
    palette = settings.pop("palette", None)

    visualise.backend = settings.pop("backend")

    plotter = visualise.StateScatterplot(   df = dataset, 
                                            x = settings.get("x"), 
                                            y = settings.get("y"), 
                                            hue = settings.get("hue"), 
                                            style = settings.get("style") )
    
    xthreshold = thresholds[0] / dataset[settings.get("x")].max() 
    fig = plotter.count_highlights( 
                                ref_col = ref_col,
                                title = title,
                                subsets = subsets, 
                                topmost = xthreshold,
                                absolute = True
                                
                            )
    if visualise.backend == "plotly":
        container.plotly_chart( fig, use_container_width = True )
    else:
        visualise.sns.set_palette( palette )
        fig.set_size_inches( settings.get("figsize"), forward=True )
        if despine:
            visualise.sns.despine()
        visualise.plt.tight_layout()
        container.pyplot( fig )

    return fig 


def auto_drop_subsets(container = st):
    """
    Drop automatically any subsets that do not have any terms in the topmost.
    """

    n_required = container.number_input( "Drop subsets with less than n terms", min_value = 0, value = 0, max_value = 50, help = "Use this to drop any subsets that do not have at least `n` terms in the topmost enriched terms. The `x_threshold` and `y_threshold` inputs are used to define topmost enriched terms." )

    if n_required == 0:
        return

    dataset = core.get( "gene_set" )
    settings = core.get( "gene_set_settings" )
    subsets = core.get("highlight_subsets" )

    thresholds = core.get( "topmost_thresholds" )

    cropped = dataset.query( f"`{settings.get('x')}` > {thresholds[0]} and `{settings.get('y')}` > {thresholds[1]}" )

    plotter = visualise.StateScatterplot(   df = cropped, 
                                            x = settings.get("x"), 
                                            y = settings.get("y"), 
                                            hue = settings.get("hue"), 
                                            style = settings.get("style") )
    
    plotter._highlight( settings.get("ref"), subsets )
    cropped = plotter.df
    # st.write( cropped )

    counts = cropped.value_counts( "__hue__" )
    to_drop = counts[counts < n_required].index.tolist()
    to_drop += [ i for i in subsets if i not in counts.index.tolist() ]
    # st.write( subsets.keys(), to_drop )

    for i in to_drop:
        subsets.pop(i)
    
    # st.write( subsets )
    session["highlight_subsets"] = subsets

    
# @sessionize(label="topmost_terms")
def view_gene_sets(container = st):

    dataset = core.get( "gene_set" )
    subsets = session["highlight_subsets"]

    settings = core.get( "gene_set_settings" )
    settings.update( core.get( "figure_settings" ) )

    title = "Topmost enriched Terms"
    ref_col = settings.get("ref")

    topx, topy, n_topmost = core.get( "topmost_thresholds" )
    n_topmost = int(n_topmost) if n_topmost > 0 else None 

    visualise.backend = settings.get("backend")

    plotter = visualise.StateScatterplot(   df = dataset, x = settings.get("x"), y = settings.get("y"), hue = settings.get("hue"), style = settings.get("style") )
    fig = plotter.top_gene_sets( subsets = subsets, ref_col = ref_col, n = n_topmost, x_threshold = topx, y_threshold = topy, title = title, xlabel = settings.get("xlabel") )
    
    if visualise.backend == "plotly":
        container.plotly_chart( fig, use_container_width = True )
    else:
        fig.set_size_inches( settings.get("figsize"), forward=True )
        visualise.plt.tight_layout()
        if settings.get("despine"):
            for axis in ['top','bottom','left','right']:
                fig.get_axes()[0].spines[axis].set_linewidth(0.3)

        container.pyplot( fig )


    if core.get( "which_subsets" ).get( "topmost_table" ):
        table_ext = container.expander( "Gene set table", expanded = False )
        table_ext.table(plotter.df)

    return fig