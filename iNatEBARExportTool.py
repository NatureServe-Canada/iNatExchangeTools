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
        iNatExchangeUtils.project_path = parameters[0].valueAsText
        iNatExchangeUtils.output_path = iNatExchangeUtils.project_path + '/' + iNatExchangeUtils.output_folder
        iNatExchangeUtils.input_label = parameters[1].valueAsText
        observations = iNatExchangeUtils.output_path + '/' + iNatExchangeUtils.input_label + '.gdb/observations'

        # convert date to text if necessary
        convert_date = False
        field_type = iNatExchangeUtils.fieldType(observations, 'observed_on')
        if not field_type:
            convert_date = True
            # add field
        elif field_type != 'Date':
            convert_date = True

        # export unobscured observations
        iNatExchangeUtils.displayMessage(messages, 'Exporting observations')
        arcpy.management.MakeFeatureLayer(observations, 'observations')
        arcpy.management.SelectLayerByLocation('observations', 'INTERSECT', iNatExchangeUtils.jur_buffer)
        arcpy.management.SelectLayerByAttribute('observations', 'SUBSET_SELECTION', 'private_latitude IS NULL')
        if arcpy.Exists(iNatExchangeUtils.project_path + '/unobscured_for_ebar_import.csv'):
            arcpy.Delete_management(iNatExchangeUtils.project_path + '/unobscured_for_ebar_import.csv')
        arcpy.conversion.TableToTable('observations', iNatExchangeUtils.project_path, 'unobscured_for_ebar_import.csv')
        iNatExchangeUtils.displayMessage(messages, 'Created ' + iNatExchangeUtils.project_path +
                                         '/unobscured_for_ebar_import.csv')

        # export obscured observations
        arcpy.management.SelectLayerByLocation('observations', 'INTERSECT', iNatExchangeUtils.jur_buffer)
        arcpy.management.SelectLayerByAttribute('observations', 'SUBSET_SELECTION', 'private_latitude IS NOT NULL')
        if arcpy.Exists(iNatExchangeUtils.project_path + '/obscured_for_ebar_import.csv'):
            arcpy.Delete_management(iNatExchangeUtils.project_path + '/obscured_for_ebar_import.csv')
        arcpy.conversion.TableToTable('observations', iNatExchangeUtils.project_path, 'obscured_for_ebar_import.csv')
        iNatExchangeUtils.displayMessage(messages, 'Created ' + iNatExchangeUtils.project_path +
                                         '/obscured_for_ebar_import.csv')


# controlling process
if __name__ == '__main__':
    inee = iNatEBARExportTool()
    # hard code parameters for debugging
    param_project_path = arcpy.Parameter()
    param_project_path.value = 'C:/GIS/iNatExchange'
    param_input_label = arcpy.Parameter()
    param_input_label.value = 'inaturalist-ca-5-20210603-1622752843'
    parameters = [param_project_path, param_input_label]
    inee.runiNatEBARExportTool(parameters, None)
