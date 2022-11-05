"""
Core functions for the viewer
"""

import pickle
import streamlit as st
from wrappers import sessionize

session = st.session_state

def check( value ):
    """
    Checks if a value exists in the session
    """
    return value in session

def get( value ):
    """
    Get a value from the session, returns None if it does not exist.
    """
    return session.get( value, None )


@sessionize( label = "collection" )
def load( filename ):
    """
    Load a pickle file.
    """
    data = pickle.loads( filename.read() )
    return data

def to_pickle( obj ):
    """
    Convert an object to a pickle file.
    """
    return pickle.dumps( obj )
