# encoding: utf-8

# Project: iNatExchangeTools
# Credits: Randal Greene, Allison Siemens-Worsley
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: iNatExchangeUtils.py
# Code shared by ArcGIS Python tools in the iNatExchange Tools Python Toolbox


import arcpy


def displayMessage(messages, msg):
    """Output message to arcpy message object or to Python standard output."""
    if messages:
        upper_msg = msg.upper()
        if 'WARNING' in upper_msg:
            messages.addWarningMessage(msg)
        elif 'ERROR' in upper_msg or 'EXCEPTION' in upper_msg:
            messages.addErrorMessage(msg)
        else:
            messages.addMessage(msg)
    else:
        print(msg)
    return

