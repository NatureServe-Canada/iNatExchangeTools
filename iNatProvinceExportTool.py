# encoding: utf-8

# Project: iNatExchangeTools
# Project: iNatExchangeTools
# Credits: Randal Greene, Allison Siemens-Worsley
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: iNatProvinceExportTool.py
# ArcGIS Python tool for exporting iNaturalist.ca records into GDB and CSVs for transfer to Provinces

# import Python packages
import arcpy
import iNatExchangeUtils


class iNatProvinceExportTool:
    """Export iNaturalist.ca records into GDB and CSVs for transfer to Provinces"""
    def __init__(self):
        pass

    def runiNatProvinceExportTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        iNatExchangeUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # make variables for parms
        iNatExchangeUtils.displayMessage(messages, 'Processing parameters')
        param_province = parameters[0].valueAsText
        prov_name = iNatExchangeUtils.prov_dict[param_province]
        work_gdb = iNatExchangeUtils.output_path + '/' + iNatExchangeUtils.input_label + '.gdb'
        arcpy.env.workspace = work_gdb

        # make folder and gdb for province
        prov_folder = iNatExchangeUtils.output_path + '/' + param_province
        if not arcpy.Exists(prov_folder):
            arcpy.management.CreateFolder(iNatExchangeUtils.output_path, param_province)
        prov_gdb = prov_folder + '/' + param_province + '.gdb'
        if not arcpy.Exists(prov_gdb):
            arcpy.management.CreateFileGDB(prov_folder, param_province + '.gdb')

        # export observations - those named as being in province, or intersecting 32km terrestrial buffer or 200nm
        # Canadian EEZ marine buffer
        iNatExchangeUtils.displayMessage(messages, 'Exporting observations')
        arcpy.management.MakeFeatureLayer('observations', 'obs_lyr')
        arcpy.management.SelectLayerByAttribute('obs_lyr', 'NEW_SELECTION',
                                                "place_admin1_name = '" + prov_name + "'")
        arcpy.management.MakeFeatureLayer(iNatExchangeUtils.jur_buffer, 'JurisdictionBuffer')
        arcpy.management.SelectLayerByAttribute('JurisdictionBuffer', 'NEW_SELECTION',
                                                "JurisdictionAbbreviation = '" + param_province + "'")
        arcpy.management.SelectLayerByLocation('obs_lyr', 'INTERSECT', 'JurisdictionBuffer',
                                               selection_type='ADD_TO_SELECTION')
        if param_province not in('SK', 'AB'):
            arcpy.management.MakeFeatureLayer(iNatExchangeUtils.marine_eez, 'MarineBuffer')
            arcpy.management.SelectLayerByAttribute('MarineBuffer', 'NEW_SELECTION',
                                                    "JurisdictionAbbreviation = '" + param_province + "'")
            arcpy.management.SelectLayerByLocation('obs_lyr', 'INTERSECT', 'MarineBuffer',
                                                   selection_type='ADD_TO_SELECTION')
        arcpy.management.CopyFeatures('obs_lyr', prov_gdb + '/observations')


# controlling process
if __name__ == '__main__':
    inpe = iNatProvinceExportTool()
    # hard code parameters for debugging
    param_province = arcpy.Parameter()
    param_province.value = 'NU'
    parameters = [param_province]
    inpe.runiNatProvinceExportTool(parameters, None)


