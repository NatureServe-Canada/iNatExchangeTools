# encoding: utf-8

# Project: iNatExchangeTools
# Credits: Randal Greene, Allison Siemens-Worsley
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: iNatExchangeUtils.py
# Code shared by ArcGIS Python tools in the iNatExchange Tools Python Toolbox


import arcpy


prov_dict = {'AC': 'Atlantic Canada',
             'NL': 'Newfoundland and Labrador',
             'NS': 'Nova Scotia',
             'NB': 'New Brunswick',
             'PE': 'Prince Edward Island',
             'QC': 'Quebec',
             'ON': 'Ontario',
             'MB': 'Manitoba',
             'SK': 'Saskatchewan',
             'AB': 'Alberta',
             'BC': 'British Columbia',
             'YT': 'Yukon',
             'NT': 'Northwest Territories',
             'NU': 'Nunavut'}
# can be overridden in tools via parameters
project_path = 'C:/GIS/iNatExchange'
input_folder = 'Input'
input_label = 'inaturalist-ca-5-20210603-1622752843'
input_path = project_path + '/' + input_folder + '/' + input_label
input_prefix = input_label + '-'
output_folder = 'Output'
output_path = project_path + '/' + output_folder
date_label = '3June2021'
## assume gdb is in same folder as tools? how to get it?
#jur_buffer = 'C:/GIS/iNatExchangeTools/iNatExchangeTools.gdb/JurisdictionBufferWGS84'
#marine_eez = 'C:/GIS/iNatExchangeTools/iNatExchangeTools.gdb/MarineBufferWGS84'


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


def checkField(table, field_name):
    desc = arcpy.Describe(table)
    for field in desc.fields:
        if field.name == field_name:
            return True
    return False


def fieldType(table, field_name):
    desc = arcpy.Describe(table)
    for field in desc.fields:
        if field.name == field_name:
            return field.type
    return None
