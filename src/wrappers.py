"""
Wrapper functions to make it easier to use the session.
"""

import functools
import streamlit as st

session = st.session_state


# def containerize( func ):
#     """
#     Add implicit container support to functions.
#     This will allow them to use a specific container or just `st` by default.
#     """

#     @functools.wraps( func )
#     def wrapper( *args, **kwargs ):
#         """
#         Add implicit container support to functions.
#         """

#         if len( args ) == 1:
#             return func( *args, **kwargs )
#         elif "container" in kwargs:
#             return func( *args, **kwargs )
#         else:
#             return func( st, *args, **kwargs )
            
#     return wrapper

def sessionize( func=None, label = None ):
    """
    Add a value to the session.

    This will allow the function to automatically add the return value to the session state under some specified label.
    If the label is not specified, the function name will be used. If `remember` is set to True, then the value will only once be set to the session state.
    
    This can also `containerize` the function if the `container` argument is set to `True`.
    """

    if func and label is None:
        label = func.__name__
        
    def _wrapper( func ):

        @functools.wraps( func )
        def wrapper( *args, **kwargs ):
            session[label] = func( *args, **kwargs )
            return session[label]

        return wrapper
    
    if func:
        return _wrapper( func )
    return _wrapper
