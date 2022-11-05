"""
The main user controls
"""

import streamlit as st
from wrappers import sessionize
import core

session = st.session_state

@sessionize(label = "datafile")
def upload(container):
    """
    Upload a file.
    """
    file = container.file_uploader( "Upload a collection here", help = "This must be a pickle file exported from `eco_helper`." )    
    return file


@sessionize
def inspect_summary(container):
    """
    Inspect the summary of the collection.
    """
    current = core.get( "inspect_summary" )
    contender = core.get( "explore_gene_sets" )
    button = container.button( "Inspect EcoType Summary", help = "View the composition of Ecotypes in a broad summary" )
    return button or (current and not contender )


@sessionize
def explore_gene_sets(container):
    """
    Explore the gene sets of the collection.
    """
    current = core.get( "explore_gene_sets" )
    contender = core.get( "inspect_summary" )
    button = container.button( "Explore Gene sets", help = "Explore the gene sets of specific cell-types in specific Ecotypes" )
    return button or (current and not contender )

