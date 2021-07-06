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
        iNatExchangeUtils.project_path = parameters[0].valueAsText
        iNatExchangeUtils.output_path = iNatExchangeUtils.project_path + '/' + iNatExchangeUtils.output_folder
        if not arcpy.Exists(iNatExchangeUtils.output_path):
            arcpy.management.CreateFolder(iNatExchangeUtils.project_path, iNatExchangeUtils.output_folder)
        iNatExchangeUtils.input_label = parameters[1].valueAsText
        iNatExchangeUtils.input_path = iNatExchangeUtils.project_path + '/' + iNatExchangeUtils.input_folder + '/' + \
            iNatExchangeUtils.input_label
        iNatExchangeUtils.input_prefix = iNatExchangeUtils.input_label + '-'
        if not arcpy.Exists(iNatExchangeUtils.output_path + '/' + iNatExchangeUtils.input_label + '.gdb'):
            arcpy.management.CreateFileGDB(iNatExchangeUtils.output_path, iNatExchangeUtils.input_label + '.gdb')
        arcpy.env.workspace = iNatExchangeUtils.output_path + '/' + iNatExchangeUtils.input_label + '.gdb'

        # import observations, giving preference to private coordinates where available
        iNatExchangeUtils.displayMessage(messages, 'Importing observations')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'observations.csv', arcpy.env.workspace, 'obs_temp')
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
        arcpy.management.Delete('obs_temp')

        # import other tables
        iNatExchangeUtils.displayMessage(messages, 'Importing annotations')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'annotations.csv', arcpy.env.workspace, 'annotations')
        iNatExchangeUtils.displayMessage(messages, 'Importing comments')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'comments.csv', arcpy.env.workspace, 'comments')
        iNatExchangeUtils.displayMessage(messages, 'Importing conservation_statuses')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'conservation_statuses.csv', arcpy.env.workspace, 'conservation_statuses')
        iNatExchangeUtils.displayMessage(messages, 'Importing identifications')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'identifications.csv', arcpy.env.workspace, 'identifications')
        iNatExchangeUtils.displayMessage(messages, 'Importing observation_field_values')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'observation_field_values.csv', arcpy.env.workspace, 'observation_field_values')
        iNatExchangeUtils.displayMessage(messages, 'Importing observation_fields')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'observation_fields.csv', arcpy.env.workspace, 'observation_fields')
        iNatExchangeUtils.displayMessage(messages, 'Importing quality_metrics')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'quality_metrics.csv', arcpy.env.workspace, 'quality_metrics')
        iNatExchangeUtils.displayMessage(messages, 'Importing taxa')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'taxa.csv', arcpy.env.workspace, 'taxa')
        iNatExchangeUtils.displayMessage(messages, 'Importing users')
        arcpy.conversion.TableToTable(iNatExchangeUtils.input_path + '/' + iNatExchangeUtils.input_prefix +
                                      'users.csv', arcpy.env.workspace, 'users')

        # add indexes
        iNatExchangeUtils.displayMessage(messages, 'Indexing query and join fields')
        arcpy.management.AddIndex('observations', ['id'], 'id_idx')
        arcpy.management.AddIndex('observations', ['place_admin1_name'], 'place_admin1_name_idx')
        arcpy.management.AddIndex('observations', ['geoprivacy'], 'geoprivacy_idx')
        arcpy.management.AddIndex('observations', ['taxon_geoprivacy'], 'taxon_geoprivacy_idx')
        arcpy.management.AddIndex('observations', ['private_latitude'], 'private_latitude_idx')
        arcpy.management.AddIndex('annotations', ['resource_id'], 'resource_id_idx')
        arcpy.management.AddIndex('comments', ['parent_id'], 'parent_id_idx')
        arcpy.management.AddIndex('identifications', ['observation_id'], 'observation_id_idx')
        arcpy.management.AddIndex('observation_field_values', ['observation_id'], 'observation_id_idx')
        arcpy.management.AddIndex('quality_metrics', ['observation_id'], 'observation_id_idx')
        arcpy.management.AddIndex('taxa', ['id'], 'id_idx')
        arcpy.management.AddIndex('conservation_statuses', ['taxon_id'], 'taxon_id_idx')


# controlling process
if __name__ == '__main__':
    ini = iNatImportTool()
    # hard code parameters for debugging
    param_project_path = arcpy.Parameter()
    param_project_path.value = 'C:/GIS/iNatExchange'
    param_input_label = arcpy.Parameter()
    param_input_label.value = 'inaturalist-ca-5-20210603-1622752843'
    parameters = [param_project_path, param_input_label]
    ini.runiNatImportTool(parameters, None)
