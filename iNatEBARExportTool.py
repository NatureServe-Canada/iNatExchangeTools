# encoding: utf-8

# Project: iNatExchangeTools
# Credits: Randal Greene, Allison Siemens-Worsley
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: iNatEBARExportTool.py
# ArcGIS Python tool for exporting iNaturalist.ca records into CSVs for EBAR import

# import Python packages
import arcpy
import iNatExchangeUtils
import datetime
import os


class iNatEBARExportTool:
    """Export iNaturalist.ca records into CSVs for EBAR import"""
    def __init__(self):
        pass

    def runiNatEBARExportTool(self, parameters, messages):
        # print start time
        start_time = datetime.datetime.now()
        iNatExchangeUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # make variables for parms
        iNatExchangeUtils.displayMessage(messages, 'Processing parameters')
        tools_path = os.path.dirname(__file__)
        iNatExchangeUtils.project_path = parameters[0].valueAsText
        iNatExchangeUtils.output_path = iNatExchangeUtils.project_path + '/' + iNatExchangeUtils.output_folder
        iNatExchangeUtils.input_label = parameters[1].valueAsText
        observations = iNatExchangeUtils.output_path + '/' + iNatExchangeUtils.input_label + '.gdb/observations'
        # # limit to pre-extracted HBJBL obs
        # observations = iNatExchangeUtils.output_path + '/' + iNatExchangeUtils.input_label + '.gdb/observations_hbjbl'

        # export unobscured observations
        iNatExchangeUtils.displayMessage(messages, 'Exporting observations')
        arcpy.management.MakeFeatureLayer(tools_path + '/iNatExchangeTools.gdb/JurisdictionBufferWGS84',
                                          'jurisdictions')
        # limit to Canada (for iNat Ingestor only)
        arcpy.management.SelectLayerByAttribute('jurisdictions', 'NEW_SELECTION', 'JurisdictionID NOT IN (14, 15)')
        arcpy.management.MakeFeatureLayer(observations, 'observations')
        arcpy.management.SelectLayerByLocation('observations', 'INTERSECT', 'jurisdictions')
        # # limit to EBAR species of interest
        # arcpy.management.SelectLayerByAttribute('observations', 'SUBSET_SELECTION',
        #                                         'scientific_name IN (SELECT NATIONAL_SCIENTIFIC_NAME FROM NSN)')
        arcpy.management.SelectLayerByAttribute('observations', 'SUBSET_SELECTION',
                                                'private_latitude IS NULL ' +
                                                "AND (geoprivacy IS NULL OR geoprivacy <> 'private')")
        if arcpy.Exists(iNatExchangeUtils.output_path + '/unobscured_for_ebar_import.csv'):
            arcpy.Delete_management(iNatExchangeUtils.output_path + '/unobscured_for_ebar_import.csv')
        arcpy.conversion.TableToTable('observations', iNatExchangeUtils.output_path, 'unobscured_for_ebar_import.csv')
        iNatExchangeUtils.displayMessage(messages, 'Created ' + iNatExchangeUtils.output_path +
                                         '/unobscured_for_ebar_import.csv')

        # export obscured observations
        arcpy.management.SelectLayerByLocation('observations', 'INTERSECT', 'jurisdictions')
        # # limit to EBAR species of interest
        # arcpy.management.SelectLayerByAttribute('observations', 'SUBSET_SELECTION',
        #                                         'scientific_name IN (SELECT NATIONAL_SCIENTIFIC_NAME FROM NSN)')
        arcpy.management.SelectLayerByAttribute('observations', 'SUBSET_SELECTION', 'private_latitude IS NOT NULL ' +
                                                "AND (geoprivacy IS NULL OR geoprivacy <> 'private')")
        if arcpy.Exists(iNatExchangeUtils.output_path + '/obscured_for_ebar_import.csv'):
            arcpy.Delete_management(iNatExchangeUtils.output_path + '/obscured_for_ebar_import.csv')
        arcpy.conversion.TableToTable('observations', iNatExchangeUtils.output_path, 'obscured_for_ebar_import.csv')
        iNatExchangeUtils.displayMessage(messages, 'Created ' + iNatExchangeUtils.output_path +
                                         '/obscured_for_ebar_import.csv')

        # finish time
        finish_time = datetime.datetime.now()
        iNatExchangeUtils.displayMessage(messages, 'Finish time: ' + str(finish_time))


# controlling process
if __name__ == '__main__':
    inee = iNatEBARExportTool()
    # hard code parameters for debugging
    param_project_path = arcpy.Parameter()
    param_project_path.value = 'D:/GIS/iNatExchange'
    param_input_label = arcpy.Parameter()
    param_input_label.value = 'inaturalist-canada-5'
    parameters = [param_project_path, param_input_label]
    inee.runiNatEBARExportTool(parameters, None)
