"""
The main application.
"""

import os
loc = os.path.dirname(__file__)


import streamlit as st
import window, core, controls
import gene_set_explorer as explorer

session = st.session_state

def main():
    
    st.set_page_config(
            page_title = "eco_helper",
            page_icon = "resources/eco_helper.svg",
            layout = "wide",
            initial_sidebar_state = "expanded"
        )
    
        
    st.sidebar.image(f"{loc}/resources/eco_helper.png")

    window.side_controls()

    if not core.get( "datafile" ):
         window.welcome()

    if core.get( "datafile" ) and not core.get( "collection" ):
        core.load( session["datafile"] )
    
    if core.get( "collection" ):

        if core.get( "inspect_summary" ) or (not core.get( "explore_gene_sets" ) and not core.get( "inspect_summary" )):
            window.ecotype_summary_page()

        if core.get( "explore_gene_sets" ):
            window.gene_set_explorer()
            

    # st.write(session)

if __name__ == "__main__":
    main()