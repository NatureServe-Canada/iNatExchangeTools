# encoding: utf-8

# Project: iNatExchangeTools
# Credits: Randal Greene, Allison Siemens-Worsley
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: iNatEBARExportTool.py
# ArcGIS Python tool for exporting iNaturalist.ca records into CSVs for EBAR import

# import Python packages
import arcpy
import iNatExchangeUtils


class iNatEBARExportTool:
    """Export iNaturalist.ca records into CSVs for EBAR import"""
    def __init__(self):
        pass

    def runiNatEBARExportTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        iNatExchangeUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # make variables for parms
        iNatExchangeUtils.displayMessage(messages, 'Processing parameters')
        #param_geodatabase = parameters[0].valueAsText
        observations = 'C:/GIS/iNatExchange/Output/inaturalist-ca-5-20210603-1622752843.gdb/observations'
        buffer = 'C:/GIS/EBAR/EBAR.gdb/JurisdictionBufferFull'

        # convert date to text if necessary
        convert_date = False
        field_type = iNatExchangeUtils.fieldType(observations, 'observed_on')
        if not field_type:
            convert_date = True
            # add field
        elif field_type != 'Date':
            convert_date = True
        # field name decisions...

        # select observations within EBAR buffer
        arcpy.management.MakeFeatureLayer(observations, 'observations')
        arcpy.management.SelectLayerByLocation('observations', 'INTERSECT', buffer)
        ## select research grade, unobscured observations
        #arcpy.management.SelectLayerByAttribute('observations', 'SUBSET_SELECTION',
        #                                        "quality_grade = 'research' AND private_latitude IS NULL")
        # select unobscured observations
        arcpy.management.SelectLayerByAttribute('observations', 'SUBSET_SELECTION', 'private_latitude IS NULL')

        # export
        arcpy.conversion.TableToTable('observations', 'C:/GIS/iNatExchange', 'unobscured_for_ebar_import.csv')

        # repeat process for obscured


# controlling process
if __name__ == '__main__':
    inee = iNatEBARExportTool()
    # hard code parameters for debugging
    #param_geodatabase = arcpy.Parameter()
    #param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    #parameters = [param_geodatabase]
    parameters = []
    inee.runiNatEBARExportTool(parameters, None)

