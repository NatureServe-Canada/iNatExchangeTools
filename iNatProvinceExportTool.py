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
        prov_gdb = prov_folder + '/iNat_' + param_province + '_' + iNatExchangeUtils.date_label + '.gdb'
        if not arcpy.Exists(prov_gdb):
            arcpy.management.CreateFileGDB(prov_folder, param_province + '.gdb')

        # export observations - those named as being in province, or intersecting 32km terrestrial buffer or 200nm
        # Canadian EEZ marine buffer
        iNatExchangeUtils.displayMessage(messages, 'Exporting observations')
        arcpy.management.MakeFeatureLayer('observations', 'obs_lyr')
        arcpy.management.SelectLayerByAttribute('obs_lyr', 'NEW_SELECTION', "place_admin1_name = '" + prov_name + "'")
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
        # split into multiple buckets... most efficient way to do queries??? boolean parms???
        arcpy.management.CopyFeatures('obs_lyr', prov_gdb + '/observations')
        arcpy.management.AddIndex(prov_gdb + '/observations', ['id'], 'observations_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/observations', ['taxon_id'], 'observations_taxon_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/observations', ['user_id'], 'observations_user_id_idx')
        arcpy.conversion.TableToTable('obs_lyr', prov_folder,
                                      'iNat_observations_' + iNatExchaneUtils.date_label + '.csv')

        # annotations - assume all are resource_type='Observation'
        iNatExchangeUtils.displayMessage(messages, 'Exporting annotations')
        arcpy.management.MakeFeatureLayer('annotations', 'annotations_lyr')
        arcpy.management.AddJoin('annotations_lyr', 'resource_id', prov_gdb + '/observations', 'id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('annotations_lyr')
        arcpy.management.RemoveJoin('annotations_lyr', 'observations')
        arcpy.conversion.TableToTable('annotations_lyr', prov_gdb, 'annotations')
        arcpy.management.AddIndex(prov_gdb + '/annotations', ['id'], 'annotations_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/annotations', ['resource_id'], 'annotations_resource_id_idx')
        arcpy.conversion.TableToTable('annotations', prov_folder, 'annotations.csv')

        # comments - assume all are parent_type='Observation'
        iNatExchangeUtils.displayMessage(messages, 'Exporting comments')
        arcpy.management.MakeFeatureLayer('comments', 'comments_lyr')
        arcpy.management.AddJoin('comments_lyr', 'parent_id', prov_gdb + '/observations', 'id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('comments_lyr')
        arcpy.management.RemoveJoin('comments_lyr', 'observations')
        arcpy.conversion.TableToTable('comments_lyr', prov_gdb, 'comments')
        arcpy.management.AddIndex(prov_gdb + '/comments', ['id'], 'comments_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/comments', ['parent_id'], 'comments_parent_id_idx')
        arcpy.conversion.TableToTable('comments', prov_folder, 'comments.csv')

        # identifications
        iNatExchangeUtils.displayMessage(messages, 'Exporting identifications')
        arcpy.management.MakeFeatureLayer('identifications', 'identifications_lyr')
        arcpy.management.AddJoin('identifications_lyr', 'observation_id', prov_gdb + '/observations', 'id',
                                 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('identifications_lyr')
        arcpy.management.RemoveJoin('identifications_lyr', 'observations')
        arcpy.conversion.TableToTable('identifications_lyr', prov_gdb, 'identifications')
        arcpy.management.AddIndex(prov_gdb + '/identifications', ['id'], 'identifications_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/identifications', ['observation_id'],
                                  'identifications_observation_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/identifications', ['taxon_id'], 'identifications_taxon_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/identifications', ['user_id'], 'identifications_user_id_idx')
        arcpy.conversion.TableToTable('identifications', prov_folder, 'identifications.csv')

        # observation_field_values
        iNatExchangeUtils.displayMessage(messages, 'Exporting observation_field_values')
        arcpy.management.MakeFeatureLayer('observation_field_values', 'observation_field_values_lyr')
        arcpy.management.AddJoin('observation_field_values_lyr', 'observation_id', prov_gdb + '/observations', 'id',
                                 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('observation_field_values_lyr')
        arcpy.management.RemoveJoin('observation_field_values_lyr', 'observations')
        arcpy.conversion.TableToTable('observation_field_values_lyr', prov_gdb, 'observation_field_values')
        arcpy.management.AddIndex(prov_gdb + '/observation_field_values', ['id'], 'ofvs_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/observation_field_values', ['observation_id'],
                                  'ofvs_observation_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/observation_field_values', ['observation_field_id'],
                                  'ofvs_observation_field_id_idx')
        arcpy.conversion.TableToTable('observation_field_values', prov_folder, 'observation_field_values.csv')

        # observation_fields (all records, no subsetting)
        iNatExchangeUtils.displayMessage(messages, 'Exporting observation_fields')
        arcpy.conversion.TableToTable('observation_fields', prov_gdb, 'observation_fields')
        arcpy.management.AddIndex(prov_gdb + '/observation_fields', ['id'], 'observation_fields_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/observation_fields', ['user_id'], 'observation_fields_user_id_idx')
        arcpy.conversion.TableToTable('observation_fields', prov_folder, 'observation_fields.csv')

        # quality_metrics
        iNatExchangeUtils.displayMessage(messages, 'Exporting quality_metrics')
        arcpy.management.MakeFeatureLayer('quality_metrics', 'quality_metrics_lyr')
        arcpy.management.AddJoin('quality_metrics_lyr', 'observation_id', prov_gdb + '/observations', 'id',
                                 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('quality_metrics_lyr')
        arcpy.management.RemoveJoin('quality_metrics_lyr', 'observations')
        arcpy.conversion.TableToTable('quality_metrics_lyr', prov_gdb, 'quality_metrics')
        arcpy.management.AddIndex(prov_gdb + '/quality_metrics', ['id'], 'quality_metrics_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/quality_metrics', ['observation_id'],
                                  'quality_metrics_observation_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/quality_metrics', ['user_id'], 'quality_metrics_user_id_idx')
        arcpy.conversion.TableToTable('quality_metrics', prov_folder, 'quality_metrics.csv')

        # taxa
        iNatExchangeUtils.displayMessage(messages, 'Exporting taxa')
        arcpy.management.MakeFeatureLayer('taxa', 'taxa_lyr')
        arcpy.management.AddJoin('taxa_lyr', 'id', prov_gdb + '/observations', 'taxon_id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('taxa_lyr')
        arcpy.management.RemoveJoin('taxa_lyr', 'observations')
        arcpy.management.AddJoin('taxa_lyr', 'id', prov_gdb + '/identifications', 'taxon_id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('taxa_lyr', 'ADD_TO_SELECTION')
        arcpy.management.RemoveJoin('taxa_lyr', 'identifications')
        arcpy.conversion.TableToTable('taxa_lyr', prov_gdb, 'taxa')
        arcpy.management.AddIndex(prov_gdb + '/taxa', ['id'], 'taxa_id_idx')
        arcpy.conversion.TableToTable('taxa', prov_folder, 'taxa.csv')

        # conservation_statuses
        iNatExchangeUtils.displayMessage(messages, 'Exporting conservation_statuses')
        arcpy.management.MakeFeatureLayer('conservation_statuses', 'conservation_statuses_lyr')
        arcpy.management.AddJoin('conservation_statuses_lyr', 'taxon_id', prov_gdb + '/taxa', 'id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('conservation_statuses_lyr')
        arcpy.management.RemoveJoin('conservation_statuses_lyr', 'taxa')
        arcpy.conversion.TableToTable('conservation_statuses_lyr', prov_gdb, 'conservation_statuses')
        arcpy.management.AddIndex(prov_gdb + '/conservation_statuses', ['id'], 'cs_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/conservation_statuses', ['taxon_id'], 'cs_taxon_id_idx')
        arcpy.management.AddIndex(prov_gdb + '/conservation_statuses', ['user_id'], 'cs_user_id_idx')
        arcpy.conversion.TableToTable('conservation_statuses', prov_folder, 'conservation_statuses.csv')

        # users (all records, no subsetting)
        iNatExchangeUtils.displayMessage(messages, 'Exporting users')
        arcpy.conversion.TableToTable('users', prov_gdb, 'users')
        arcpy.management.AddIndex(prov_gdb + '/users', ['id'], 'users_id_idx')
        arcpy.conversion.TableToTable('users', prov_folder, 'users.csv')

        # add relationships to output gdb
        iNatExchangeUtils.displayMessage(messages, 'Adding relationships to output gdb')
        arcpy.env.workspace = prov_gdb
        arcpy.management.CreateRelationshipClass(prov_gdb + '/observations', prov_gdb + '/annotations',
                                                 'observations_annotations', 'SIMPLE', 'annotations', 'observations',
                                                 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'resource_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/observations', prov_gdb + '/comments',
                                                 'observations_comments', 'SIMPLE', 'comments', 'observations', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'parent_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/taxa', prov_gdb + '/conservation_statuses',
                                                 'taxa_conservation_statuses', 'SIMPLE', 'conservation_statuses',
                                                 'taxa', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'taxon_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/users', prov_gdb + '/conservation_statuses',
                                                 'users_conservation_statuses', 'SIMPLE', 'conservation_statuses',
                                                 'users', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/observations', prov_gdb + '/identifications',
                                                 'observations_identifications', 'SIMPLE', 'identifications',
                                                 'observations', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'observation_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/taxa', prov_gdb + '/identifications',
                                                 'taxa_identifications', 'SIMPLE', 'identifications', 'taxa', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'taxon_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/users', prov_gdb + '/identifications',
                                                 'users_identifications', 'SIMPLE', 'identifications', 'users', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/observations', prov_gdb + '/observation_field_values',
                                                 'observations_observation_field_values', 'SIMPLE',
                                                 'observation_field_values', 'observations', 'NONE', 'ONE_TO_MANY',
                                                 'NONE', 'id', 'observation_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/observation_fields',
                                                 prov_gdb + '/observation_field_values',
                                                 'observation_fields_observation_field_values', 'SIMPLE',
                                                 'observation_field_values', 'observation_fields', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'observation_field_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/users', prov_gdb + '/observation_field_values',
                                                 'users_observation_field_values', 'SIMPLE',
                                                 'observation_field_values', 'users', 'NONE', 'ONE_TO_MANY', 'NONE',
                                                 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/users', prov_gdb + '/observations', 'users_observations',
                                                 'SIMPLE', 'observations', 'users', 'NONE', 'ONE_TO_MANY', 'NONE',
                                                 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/users', prov_gdb + '/observation_fields',
                                                 'users_observation_fields', 'SIMPLE', 'observation_fields', 'users',
                                                 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/users', prov_gdb + '/quality_metrics',
                                                 'users_quality_metrics', 'SIMPLE', 'quality_metrics', 'users', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/observations', prov_gdb + '/quality_metrics',
                                                 'observations_quality_metrics', 'SIMPLE', 'quality_metrics',
                                                 'observations', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'observation_id')
        arcpy.management.CreateRelationshipClass(prov_gdb + '/taxa', prov_gdb + '/observations',
                                                 'taxa_observations', 'SIMPLE', 'observations',
                                                 'taxa', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'taxon_id')


# controlling process
if __name__ == '__main__':
    inpe = iNatProvinceExportTool()
    # hard code parameters for debugging
    param_province = arcpy.Parameter()
    param_province.value = 'NU'
    parameters = [param_province]
    inpe.runiNatProvinceExportTool(parameters, None)


