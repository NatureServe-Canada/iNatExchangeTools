# encoding: utf-8

# Project: iNatExchangeTools
# Credits: Randal Greene, Allison Siemens-Worsley
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: iNatImportTool.py
# ArcGIS Python tool for importing iNaturalist.ca CSVs into working gdb

# import Python packages
import arcpy
import iNatExchangeUtils


class iNatImportTool:
    """Import iNaturalist.ca CSVs into working gdb"""
    def __init__(self):
        pass

    def runiNatImportTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        iNatExchangeUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # make variables for parms
        iNatExchangeUtils.displayMessage(messages, 'Processing parameters')
        #param_geodatabase = parameters[0].valueAsText
        project_path = 'C:/GIS/iNatExchange'
        input_folder = 'Input'
        input_label = 'inaturalist-ca-5-20210603-1622752843'
        input_path = project_path + '/' + input_folder + '/' + input_label
        input_prefix = input_label + '-'
        output_folder = 'Output'
        output_path = project_path + '/' + output_folder
        if not arcpy.Exists(output_path):
            arcpy.management.CreateFolder(project_path, output_folder)
        if not arcpy.Exists(output_path + '/' + input_label + '.gdb'):
            arcpy.management.CreateFileGDB(output_path, input_label + '.gdb')
        arcpy.env.workspace = output_path + '/' + input_label + '.gdb'
        #prov_abbr = 'YT'
        #prov_folder = output_folder + '/' + prov_abbr
        #prov_gdb = prov_folder + '/' + prov_abbr + '.gdb'
        ## comma-separated list of quoted values
        #prov_name = "'Yukon'"

        # import observations, giving preference to private coordinates where available
        iNatExchangeUtils.displayMessage(messages, 'Importing observations')
        arcpy.conversion.TableToTable(input_path + '/' + input_prefix + 'observations.csv', arcpy.env.workspace,
                                      'obs_temp')
        iNatExchangeUtils.displayMessage(messages,
                                         'Plotting observations, preferring private coordinates where available')
        arcpy.management.AddField('obs_temp', 'lon', 'DOUBLE')
        arcpy.management.AddField('obs_temp', 'lat', 'DOUBLE')
        expr = '''
def get_coord(coord, private_coord):
    if private_coord:
        return private_coord
    else:
        return coord'''
        arcpy.management.CalculateField('obs_temp', 'lon', 'get_coord(!longitude!, !private_longitude!)', 'PYTHON3',
                                        expr)
        arcpy.management.CalculateField('obs_temp', 'lat', 'get_coord(!latitude!, !private_latitude!)', 'PYTHON3',
                                        expr)
        arcpy.management.XYTableToPoint('obs_temp', 'observations', 'lon', 'lat')
#        arcpy.management.Delete('obs_temp')


# controlling process
if __name__ == '__main__':
    ini = iNatImportTool()
    # hard code parameters for debugging
    #param_geodatabase = arcpy.Parameter()
    #param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    #parameters = [param_geodatabase]
    parameters = []
    ini.runiNatImportTool(parameters, None)
