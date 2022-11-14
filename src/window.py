"""
The main window
"""


import os
import darkdetect
import streamlit as st
import user_input
import controls
import ecotype_summary
import gene_set_explorer as explorer
import core


session = st.session_state


loc = os.path.dirname(__file__)
suffix = "_light" if darkdetect.isDark() else "_dark"
viewer_logo = f"{loc}/resources/viewer{suffix}.png"


def welcome():

    st.image(viewer_logo, use_column_width = True)

    st.markdown( """

    # Welcome to the _eco_helper_ Results Viewer
    
    This web application offers an interactive data explorer for the gene set enrichment results of 
    an [EcoTyper](https://github.com/digitalcytometry/ecotyper) analysis, performed by the 
    [eco_helper](https://github.com/NoahHenrikKleinschmidt/eco_helper) package.

    It allows for easy visualization of enriched terms, placing them into categories and exporting figures.

    To use the viewer, be sure to export an enrichment collection as a pickle-file via `eco_helper` and upload it here.
    """, unsafe_allow_html = True )

def side_controls():

    user_input.upload(st.sidebar)
    user_input.inspect_summary(st.sidebar)
    user_input.explore_gene_sets(st.sidebar)

def ecotype_summary_page():

    figure_panel, controls_panel = st.container(), st.container()
    figure_control_panel = controls_panel.expander( "Figure Settings", False )

    controls.scatter_figure_controls(figure_control_panel)
    ecotype_summary.figure_settings(figure_control_panel)

    scatter_fig = ecotype_summary.view_scatterplots(figure_panel)
    controls.download_figure( scatter_fig, "ecotypes_summary", figure_panel )

    gene_sets_fig = ecotype_summary.view_gene_sets(figure_panel)
    controls.download_figure( gene_sets_fig, "ecotype_topmost_gene_sets", figure_panel )

def gene_set_explorer():

    upper, middle_upper, middle_lower, lower = st.container(), st.container(), st.container(), st.container()
    ucol1, ucol2 = upper.columns( (1, 3) ) 
    mcol1, mcol2 = middle_upper.columns( (1, 2.5) )

    figure_control_panel = lower.expander( "Figure Settings", False )

    explorer.select_dataset(ucol1)
    explorer.subsets_textfield(ucol2)
    upper.markdown("---")

    controls.scatter_figure_controls(figure_control_panel)
    explorer.figure_settings(figure_control_panel)

    explorer.show_subset_figures(mcol1)
    explorer.edit_subsets(mcol1)
    explorer.auto_drop_subsets(mcol1)
    explorer.topmost_thresholds(middle_lower)

    if core.get( "which_subsets" ).get( "scatter" ):
        subsets_fig = explorer.view_subsets(mcol2)
        
        controls.download_figure( subsets_fig, suffix = "subsets", container = mcol2 )
    
        gene_set_view_container = middle_upper
    else:
        gene_set_view_container = mcol2

    if core.get( "which_subsets" ).get( "counts" ):
        counts_fig = explorer.view_histogram(mcol2)
        controls.download_figure( counts_fig, suffix = "fractions", container = mcol2 )

    if core.get( "which_subsets" ).get( "topmost" ):
        topmost_fig = explorer.view_gene_sets(gene_set_view_container)
        controls.download_figure( topmost_fig, suffix = "topmost", container = gene_set_view_container )

    middle_lower.markdown("---")