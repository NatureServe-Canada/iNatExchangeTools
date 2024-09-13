# encoding: utf-8

# Project: iNatExchangeTools
# Credits: Randal Greene, Allison Siemens-Worsley
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: iNatJurisdictionExportTool.py
# ArcGIS Python tool for exporting iNaturalist.ca records into GDB and CSVs for transfer to Provinces or custom
# jurisdictions (e.g., Parks Canada Agency)

# import Python packages
import arcpy
import arcpy.management
import arcpy.conversion
import iNatExchangeUtils
import os
import datetime


class iNatJurisdictionExportTool:
    """Export iNaturalist.ca records into GDB and CSVs for transfer to Provinces or custom jurisdictions (e.g., Parks
    Canada Agency)"""
    def __init__(self):
        pass

    def runiNatJurisdictionExportTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        iNatExchangeUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # make variables for parms
        iNatExchangeUtils.displayMessage(messages, 'Processing parameters')
        tools_path = os.path.dirname(__file__)
        iNatExchangeUtils.project_path = parameters[0].valueAsText
        iNatExchangeUtils.output_path = iNatExchangeUtils.project_path + '/' + iNatExchangeUtils.output_folder
        iNatExchangeUtils.input_label = parameters[1].valueAsText
        work_gdb = iNatExchangeUtils.output_path + '/' + iNatExchangeUtils.input_label + '.gdb'
        arcpy.env.workspace = work_gdb
        iNatExchangeUtils.date_label = parameters[2].valueAsText
        # need either province parm or both custom parms or species parm
        param_province = parameters[3].valueAsText
        param_custom_label = parameters[4].valueAsText
        param_custom_polygon = parameters[5].valueAsText
        param_species = parameters[6].valueAsText
        jur_param_ok = True
        if param_province:
            prov_name = iNatExchangeUtils.prov_dict[param_province]
            if param_custom_label or param_custom_polygon:
                jur_param_ok = False
        else:
            if not param_custom_label or not param_custom_polygon:
                jur_param_ok = False
            elif param_custom_label in list(iNatExchangeUtils.prov_dict.keys()):
                iNatExchangeUtils.displayMessage(messages, 'ERROR: the Custom Jurisdiction Label cannot be a Province')
                # terminate with error
                return
        if not jur_param_ok:
            if not param_species:
                iNatExchangeUtils.displayMessage(messages, 'ERROR: you must select either a Province, or provide a ' +
                                                 'Custom Jurisdiction Label and Polygon, but not both, or provide a ' +
                                                 'Species')
                # terminate with error
                return
        # need at least one set of records
        #param_include_ca_geo_private = parameters[7].valueAsText
        param_include_ca_geo_obscured = parameters[7].valueAsText
        #param_include_ca_taxon_private = parameters[8].valueAsText
        param_include_ca_taxon_obscured = parameters[8].valueAsText
        param_include_org_obscured = parameters[9].valueAsText
        param_include_unobscured = parameters[10].valueAsText
        if (param_include_ca_geo_obscured == 'false' and
            param_include_ca_taxon_obscured == 'false' and
            param_include_org_obscured == 'false' and
            param_include_unobscured == 'false'):
            iNatExchangeUtils.displayMessage(messages, 'ERROR: you must include at least one set of records')
            # terminate with error
            return
        arcpy.gp.overwriteOutput = True

        # make folder and gdb for jurisdiction
        if param_province:
            jur_label = param_province
            # Atlantic Canada consistes of four provinces
            if param_province == 'AC':
                param_province = "'NL', 'NS', 'NB', 'PE'"
            else:
                param_province = "'" + param_province + "'"
        elif param_custom_label:
            jur_label = param_custom_label
        else:
            jur_label = param_species
        jur_folder = iNatExchangeUtils.output_path + '/' + jur_label
        if not arcpy.Exists(jur_folder):
            arcpy.management.CreateFolder(iNatExchangeUtils.output_path, jur_label)
        jur_gdb = jur_folder + '/iNat_' + jur_label + '_' + iNatExchangeUtils.date_label + '.gdb'
        if not arcpy.Exists(jur_gdb):
            arcpy.management.CreateFileGDB(jur_folder, '/iNat_' + jur_label + '_' +
                                           iNatExchangeUtils.date_label + '.gdb')

        # export observations
        # for province, those named as being in province, or intersecting 32km terrestrial buffer or 200nm Canadian
        # EEZ marine buffer
        # for custom jurisdiction, those intersecting custom polygon
        iNatExchangeUtils.displayMessage(messages, 'Exporting observations')
        arcpy.management.MakeFeatureLayer('observations', 'obs_lyr')
        if param_province:
            arcpy.management.SelectLayerByAttribute('obs_lyr', 'NEW_SELECTION', "place_admin1_name = '" + prov_name +
                                                    "'")
            arcpy.management.MakeFeatureLayer(tools_path + '/iNatExchangeTools.gdb/JurisdictionBufferWGS84',
                                              'JurisdictionBuffer')
            arcpy.management.SelectLayerByAttribute('JurisdictionBuffer', 'NEW_SELECTION',
                                                "JurisdictionAbbreviation IN (" + param_province + ")")
            arcpy.management.SelectLayerByLocation('obs_lyr', 'INTERSECT', 'JurisdictionBuffer',
                                                   selection_type='ADD_TO_SELECTION')
            if param_province not in('SK', 'AB', 'YT'):
                arcpy.management.MakeFeatureLayer(tools_path + '/iNatExchangeTools.gdb/MarineBufferWGS84',
                                                  'MarineBuffer')
                arcpy.management.SelectLayerByAttribute('MarineBuffer', 'NEW_SELECTION',
                                                        "JurisdictionAbbreviation IN (" + param_province + ")")
                arcpy.management.SelectLayerByLocation('obs_lyr', 'INTERSECT', 'MarineBuffer',
                                                       selection_type='ADD_TO_SELECTION')
        elif param_custom_polygon:
            arcpy.management.SelectLayerByLocation('obs_lyr', 'INTERSECT', param_custom_polygon)

        # species param used for scientific_name like query
        if param_species:
            filter = ''
            param_species = param_species.replace("'", '')
            param_species = param_species.split(';')
            for species in param_species:
                if len(filter) > 0:
                    filter += ' OR '
                filter += "scientific_name LIKE '" + species + "%'"
            arcpy.management.SelectLayerByAttribute('obs_lyr', 'SUBSET_SELECTION', filter)

        # # optional hard-coded handling for taxonomic groups
        # # filter = 'taxon_id IN (SELECT id FROM taxa WHERE iconic_taxon_id IN (26036, 20978, 49995, 630955))'
        # filter = "iconic_taxon_name IN ('Insecta', 'Reptilia', 'Amphibia')"
        # arcpy.management.SelectLayerByAttribute('obs_lyr', 'SUBSET_SELECTION', filter)

        # split into multiple buckets based on parameters
        # also merge into a temp for joining to related tables
        merge_list = []
        #if param_include_ca_geo_private == 'true':
        #    merge_list.append(self.saveBucket('obs_lyr', 'ca_geo_private',
        #                                      "geoprivacy = 'private' AND private_latitude IS NOT NULL",
        #                                      jur_gdb, jur_folder))
        if param_include_ca_geo_obscured == 'true':
            merge_list.append(self.saveBucket('obs_lyr', 'ca_geo_obscured',
                                              "geoprivacy = 'obscured' AND private_latitude IS NOT NULL",
                                              jur_gdb, jur_folder))
        #if param_include_ca_taxon_private == 'true':
        #    merge_list.append(self.saveBucket('obs_lyr', 'ca_taxon_private',
        #                                      "(geoprivacy = 'open' OR geoprivacy IS NULL) AND taxon_geoprivacy = " +
        #                                      "'private' AND private_latitude IS NOT NULL", jur_gdb, jur_folder))
        if param_include_ca_taxon_obscured == 'true':
            merge_list.append(self.saveBucket('obs_lyr', 'ca_taxon_obscured', "(geoprivacy = 'open' OR geoprivacy " +
                                              "IS NULL) AND taxon_geoprivacy IN ('obscured', 'private') AND " +
                                              "private_latitude IS NOT NULL", jur_gdb, jur_folder))
        if param_include_org_obscured == 'true':
            merge_list.append(self.saveBucket('obs_lyr', 'org_obscured',
                                              "(geoprivacy IN ('obscured') OR taxon_geoprivacy IN " +
                                              "('obscured', 'private')) AND private_latitude IS NULL", jur_gdb,
                                              jur_folder))
        if param_include_unobscured == 'true':
            merge_list.append(self.saveBucket('obs_lyr', 'unobscured',
                                              "(geoprivacy = 'open' OR geoprivacy IS NULL) AND (taxon_geoprivacy = " +
                                              "'open' OR taxon_geoprivacy IS NULL) AND private_latitude IS NULL",
                                              jur_gdb, jur_folder))
        arcpy.management.Merge(merge_list, jur_gdb + '/observations_all')
        arcpy.management.AddIndex(jur_gdb + '/observations_all', ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/observations_all', ['taxon_id'], 'taxon_id_idx')
        arcpy.management.AddIndex(jur_gdb + '/observations_all', ['user_id'], 'user_id_idx')
        if arcpy.Exists(jur_folder + '/iNat_observations_all_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_observations_all_' + iNatExchangeUtils.date_label + '.csv')
        arcpy.conversion.TableToTable(jur_gdb + '/observations_all', jur_folder,
                                      'iNat_observations_all_' + iNatExchangeUtils.date_label + '.csv')

        # annotations - assume all are resource_type='Observation'
        iNatExchangeUtils.displayMessage(messages, 'Exporting annotations')
        arcpy.management.MakeTableView('annotations', 'annotations_vw')
        arcpy.management.AddJoin('annotations_vw', 'resource_id', jur_gdb + '/observations_all', 'id',
                                 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('annotations_vw')
        arcpy.management.RemoveJoin('annotations_vw', 'observations_all')
        arcpy.conversion.TableToTable('annotations_vw', jur_gdb, 'annotations')
        arcpy.management.AddIndex(jur_gdb + '/annotations', ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/annotations', ['resource_id'], 'resource_id_idx')
        if arcpy.Exists(jur_folder + '/iNat_annotations_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_annotations_' + iNatExchangeUtils.date_label + '.csv')
        arcpy.conversion.TableToTable('annotations_vw', jur_folder, 'iNat_annotations_' +
                                      iNatExchangeUtils.date_label + '.csv')

        # comments - assume all are parent_type='Observation'
        iNatExchangeUtils.displayMessage(messages, 'Exporting comments')
        arcpy.management.MakeTableView('comments', 'comments_vw')
        arcpy.management.AddJoin('comments_vw', 'parent_id', jur_gdb + '/observations_all', 'id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('comments_vw')
        arcpy.management.RemoveJoin('comments_vw', 'observations_all')
        arcpy.conversion.TableToTable('comments_vw', jur_gdb, 'comments')
        arcpy.management.AddIndex(jur_gdb + '/comments', ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/comments', ['parent_id'], 'parent_id_idx')
        if arcpy.Exists(jur_folder + '/iNat_comments_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_comments_' + iNatExchangeUtils.date_label + '.csv')
        arcpy.conversion.TableToTable('comments_vw', jur_folder, 'iNat_comments_' + iNatExchangeUtils.date_label +
                                      '.csv')

        # identifications
        iNatExchangeUtils.displayMessage(messages, 'Exporting identifications')
        arcpy.management.MakeTableView('identifications', 'identifications_vw')
        arcpy.management.AddJoin('identifications_vw', 'observation_id', jur_gdb + '/observations_all', 'id',
                                 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('identifications_vw')
        arcpy.management.RemoveJoin('identifications_vw', 'observations_all')
        arcpy.conversion.TableToTable('identifications_vw', jur_gdb, 'identifications')
        arcpy.management.AddIndex(jur_gdb + '/identifications', ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/identifications', ['observation_id'], 'observation_id_idx')
        arcpy.management.AddIndex(jur_gdb + '/identifications', ['taxon_id'], 'taxon_id_idx')
        arcpy.management.AddIndex(jur_gdb + '/identifications', ['user_id'], 'user_id_idx')
        if arcpy.Exists(jur_folder + '/iNat_identifications_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_identifications_' + iNatExchangeUtils.date_label + '.csv')
        arcpy.conversion.TableToTable('identifications_vw', jur_folder, 'iNat_identifications_' +
                                      iNatExchangeUtils.date_label + '.csv')

        # observation_field_values
        iNatExchangeUtils.displayMessage(messages, 'Exporting observation_field_values')
        arcpy.management.MakeTableView('observation_field_values', 'observation_field_values_vw')
        arcpy.management.AddJoin('observation_field_values_vw', 'observation_id', jur_gdb + '/observations_all',
                                 'id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('observation_field_values_vw')
        arcpy.management.RemoveJoin('observation_field_values_vw', 'observations_all')
        arcpy.conversion.TableToTable('observation_field_values_vw', jur_gdb, 'observation_field_values')
        arcpy.management.AddIndex(jur_gdb + '/observation_field_values', ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/observation_field_values', ['observation_id'], 'observation_id_idx')
        arcpy.management.AddIndex(jur_gdb + '/observation_field_values', ['observation_field_id'],
                                  'observation_field_id_idx')
        if arcpy.Exists(jur_folder + '/iNat_observation_field_values_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_observation_field_values_' +iNatExchangeUtils.date_label +
                                    '.csv')
        arcpy.conversion.TableToTable('observation_field_values_vw', jur_folder, 'iNat_observation_field_values_' +
                                      iNatExchangeUtils.date_label + '.csv')

        # observation_fields (all records, no subsetting)
        iNatExchangeUtils.displayMessage(messages, 'Exporting observation_fields')
        arcpy.conversion.TableToTable('observation_fields', jur_gdb, 'observation_fields')
        arcpy.management.AddIndex(jur_gdb + '/observation_fields', ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/observation_fields', ['user_id'], 'user_id_idx')
        if arcpy.Exists(jur_folder + '/iNat_observation_fields_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_observation_fields_' +iNatExchangeUtils.date_label +
                                    '.csv')
        arcpy.conversion.TableToTable('observation_fields', jur_folder, 'iNat_observation_fields_' +
                                      iNatExchangeUtils.date_label + '.csv')

        # quality_metrics
        iNatExchangeUtils.displayMessage(messages, 'Exporting quality_metrics')
        arcpy.management.MakeTableView('quality_metrics', 'quality_metrics_vw')
        arcpy.management.AddJoin('quality_metrics_vw', 'observation_id', jur_gdb + '/observations_all', 'id',
                                 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('quality_metrics_vw')
        arcpy.management.RemoveJoin('quality_metrics_vw', 'observations_all')
        arcpy.conversion.TableToTable('quality_metrics_vw', jur_gdb, 'quality_metrics')
        arcpy.management.AddIndex(jur_gdb + '/quality_metrics', ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/quality_metrics', ['observation_id'], 'observation_id_idx')
        arcpy.management.AddIndex(jur_gdb + '/quality_metrics', ['user_id'], 'user_id_idx')
        if arcpy.Exists(jur_folder + '/iNat_quality_metrics_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_quality_metrics_' + iNatExchangeUtils.date_label + '.csv')
        arcpy.conversion.TableToTable('quality_metrics_vw', jur_folder, 'iNat_quality_metrics_' +
                                      iNatExchangeUtils.date_label + '.csv')

        # taxa
        iNatExchangeUtils.displayMessage(messages, 'Exporting taxa')
        arcpy.management.MakeTableView('taxa', 'taxa_vw')
        arcpy.management.AddJoin('taxa_vw', 'id', jur_gdb + '/observations_all', 'taxon_id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('taxa_vw')
        arcpy.management.RemoveJoin('taxa_vw', 'observations_all')
        arcpy.management.AddJoin('taxa_vw', 'id', jur_gdb + '/identifications', 'taxon_id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('taxa_vw', 'ADD_TO_SELECTION')
        arcpy.management.RemoveJoin('taxa_vw', 'identifications')
        arcpy.conversion.TableToTable('taxa_vw', jur_gdb, 'taxa')
        arcpy.management.AddIndex(jur_gdb + '/taxa', ['id'], 'id_idx')
        if arcpy.Exists(jur_folder + '/iNat_taxa_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_taxa_' + iNatExchangeUtils.date_label + '.csv')
        arcpy.conversion.TableToTable('taxa_vw', jur_folder, 'iNat_taxa_' + iNatExchangeUtils.date_label + '.csv')

        # conservation_statuses
        iNatExchangeUtils.displayMessage(messages, 'Exporting conservation_statuses')
        arcpy.management.MakeTableView('conservation_statuses', 'conservation_statuses_vw')
        arcpy.management.AddJoin('conservation_statuses_vw', 'taxon_id', jur_gdb + '/taxa', 'id', 'KEEP_COMMON')
        arcpy.management.SelectLayerByAttribute('conservation_statuses_vw')
        arcpy.management.RemoveJoin('conservation_statuses_vw', 'taxa')
        arcpy.conversion.TableToTable('conservation_statuses_vw', jur_gdb, 'conservation_statuses')
        arcpy.management.AddIndex(jur_gdb + '/conservation_statuses', ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/conservation_statuses', ['taxon_id'], 'taxon_id_idx')
        arcpy.management.AddIndex(jur_gdb + '/conservation_statuses', ['user_id'], 'user_id_idx')
        if arcpy.Exists(jur_folder + '/iNat_conservation_statuses_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_conservation_statuses_' + iNatExchangeUtils.date_label +
                                    '.csv')
        arcpy.conversion.TableToTable('conservation_statuses_vw', jur_folder, 'iNat_conservation_statuses_' +
                                      iNatExchangeUtils.date_label + '.csv')

        # users (all records, no subsetting)
        iNatExchangeUtils.displayMessage(messages, 'Exporting users')
        arcpy.conversion.TableToTable('users', jur_gdb, 'users')
        arcpy.management.AddIndex(jur_gdb + '/users', ['id'], 'id_idx')
        if arcpy.Exists(jur_folder + '/iNat_users_' + iNatExchangeUtils.date_label + '.csv'):
            arcpy.management.Delete(jur_folder + '/iNat_users_' +iNatExchangeUtils.date_label +
                                    '.csv')
        arcpy.conversion.TableToTable('users', jur_folder, 'iNat_users_' +iNatExchangeUtils.date_label + '.csv')

        # add relationships to output gdb
        iNatExchangeUtils.displayMessage(messages, 'Adding relationships to output gdb')
        arcpy.env.workspace = jur_gdb
        arcpy.management.CreateRelationshipClass(jur_gdb + '/taxa', jur_gdb + '/conservation_statuses',
                                                 'taxa_conservation_statuses', 'SIMPLE', 'conservation_statuses',
                                                 'taxa', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'taxon_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/users', jur_gdb + '/conservation_statuses',
                                                 'users_conservation_statuses', 'SIMPLE', 'conservation_statuses',
                                                 'users', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/taxa', jur_gdb + '/identifications',
                                                 'taxa_identifications', 'SIMPLE', 'identifications', 'taxa', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'taxon_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/users', jur_gdb + '/identifications',
                                                 'users_identifications', 'SIMPLE', 'identifications', 'users', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/observation_fields',
                                                 jur_gdb + '/observation_field_values',
                                                 'observation_fields_observation_field_values', 'SIMPLE',
                                                 'observation_field_values', 'observation_fields', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'observation_field_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/users', jur_gdb + '/observation_field_values',
                                                 'users_observation_field_values', 'SIMPLE',
                                                 'observation_field_values', 'users', 'NONE', 'ONE_TO_MANY', 'NONE',
                                                 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/users', jur_gdb + '/observation_fields',
                                                 'users_observation_fields', 'SIMPLE', 'observation_fields', 'users',
                                                 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/users', jur_gdb + '/quality_metrics',
                                                 'users_quality_metrics', 'SIMPLE', 'quality_metrics', 'users', 'NONE',
                                                 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        self.createBucketRelationships('all', jur_gdb)
        #if param_include_ca_geo_private == 'true':
        #    self.createBucketRelationships('ca_geo_private', jur_gdb)
        if param_include_ca_geo_obscured == 'true':
            self.createBucketRelationships('ca_geo_obscured', jur_gdb)
        #if param_include_ca_taxon_private == 'true':
        #    self.createBucketRelationships('ca_taxon_private', jur_gdb)
        if param_include_ca_taxon_obscured == 'true':
            self.createBucketRelationships('ca_taxon_obscured', jur_gdb)
        if param_include_org_obscured == 'true':
            self.createBucketRelationships('org_obscured', jur_gdb)
        if param_include_unobscured == 'true':
            self.createBucketRelationships('unobscured', jur_gdb)

        # finish time
        finish_time = datetime.datetime.now()
        iNatExchangeUtils.displayMessage(messages, 'Finish time: ' + str(finish_time))

    def saveBucket(this, all_obs_lyr, bucket_name, bucket_condition, jur_gdb, jur_folder):
        """subset the observations into a bucket and save"""
        arcpy.management.MakeFeatureLayer(all_obs_lyr, bucket_name + '_lyr', bucket_condition)
        # save to gdb
        arcpy.management.CopyFeatures(bucket_name + '_lyr', jur_gdb + '/observations_' + bucket_name)
        arcpy.management.AddIndex(jur_gdb + '/observations_' + bucket_name, ['id'], 'id_idx')
        arcpy.management.AddIndex(jur_gdb + '/observations_' + bucket_name, ['taxon_id'], 'taxon_id_idx')
        arcpy.management.AddIndex(jur_gdb + '/observations_' + bucket_name, ['user_id'], 'observations_user_id_idx')
        # save to csv
        csv_name = 'iNat_observations_' + bucket_name + '_' + iNatExchangeUtils.date_label + '.csv'
        if arcpy.Exists(jur_folder + '/' + csv_name):
            arcpy.management.Delete(jur_folder + '/' + csv_name)
        arcpy.conversion.TableToTable(bucket_name + '_lyr', jur_folder, csv_name)
        # return feature class
        return jur_gdb + '/observations_' + bucket_name

    def createBucketRelationships(this, bucket_name, jur_gdb):
        """create relationship classes for an observations feature class"""
        arcpy.management.CreateRelationshipClass(jur_gdb + '/observations_' + bucket_name, jur_gdb + '/annotations',
                                                 'observations_' + bucket_name + '_annotations', 'SIMPLE',
                                                 'annotations', 'observations_' + bucket_name, 'NONE', 'ONE_TO_MANY',
                                                 'NONE', 'id', 'resource_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/observations_' + bucket_name, jur_gdb + '/comments',
                                                 'observations_' + bucket_name + '_comments', 'SIMPLE', 'comments',
                                                 'observations_' + bucket_name, 'NONE', 'ONE_TO_MANY', 'NONE', 'id',
                                                 'parent_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/observations_' + bucket_name, jur_gdb +
                                                 '/identifications', 'observations_' + bucket_name +
                                                 '_identifications', 'SIMPLE', 'identifications', 'observations_' +
                                                 bucket_name, 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'observation_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/observations_' + bucket_name, jur_gdb +
                                                 '/observation_field_values', 'observations_' + bucket_name +
                                                 '_observation_field_values', 'SIMPLE', 'observation_field_values',
                                                 'observations_' + bucket_name, 'NONE', 'ONE_TO_MANY', 'NONE', 'id',
                                                 'observation_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/users', jur_gdb + '/observations_' + bucket_name,
                                                 'users_observations_' + bucket_name, 'SIMPLE', 'observations_' +
                                                 bucket_name, 'users', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'user_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/taxa', jur_gdb + '/observations_' + bucket_name,
                                                 'taxa_observations_' + bucket_name, 'SIMPLE', 'observations_' +
                                                 bucket_name, 'taxa', 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'taxon_id')
        arcpy.management.CreateRelationshipClass(jur_gdb + '/observations_' + bucket_name, jur_gdb +
                                                 '/quality_metrics', 'observations_' + bucket_name +
                                                 '_quality_metrics', 'SIMPLE', 'quality_metrics', 'observations_' +
                                                 bucket_name, 'NONE', 'ONE_TO_MANY', 'NONE', 'id', 'observation_id')


# controlling process
if __name__ == '__main__':
    inje = iNatJurisdictionExportTool()
    # hard code parameters for debugging
    param_project_path = arcpy.Parameter()
    param_project_path.value = 'D:/GIS/iNatExchange'
    param_input_label = arcpy.Parameter()
    param_input_label.value = 'inaturalist-canada-5'
    param_date_label = arcpy.Parameter()
    param_date_label.value = '4Jun2024'
    param_province = arcpy.Parameter()
    param_province.value = None
    param_custom_label = arcpy.Parameter()
    param_custom_label.value = 'HBJBL'
    param_custom_polygon = arcpy.Parameter()
    param_custom_polygon.value = 'D:/GIS/EBAR/HudsonBay.gdb/HBJBL10' # 'C:/GIS/iNatExchange/iNatExchange.gdb/PCA_all' #'C:/GIS/EBAR/KBASites.gdb/KBASite'
    param_species = arcpy.Parameter()
    param_species.value = None # "'Emydoidea blandingii';'Graptemys geographica';'Sternotherus odoratus'"
    #param_include_ca_geo_private = arcpy.Parameter()
    #param_include_ca_geo_private.value = 'true'
    param_include_ca_geo_obscured = arcpy.Parameter()
    param_include_ca_geo_obscured.value = 'true'
    param_include_ca_taxon_private = arcpy.Parameter()
    param_include_ca_taxon_private.value = 'true'
    param_include_ca_taxon_obscured = arcpy.Parameter()
    param_include_ca_taxon_obscured.value = 'true'
    param_include_org_obscured = arcpy.Parameter()
    param_include_org_obscured.value = 'true'
    param_include_unobscured = arcpy.Parameter()
    param_include_unobscured.value = 'true'
    # for prov in ['AC', 'QC', 'ON', 'MB', 'SK', 'AB', 'BC', 'YT', 'NT', 'NU']:
    #     param_province.value = prov
    #     parameters = [param_project_path, param_input_label, param_date_label, param_province, param_custom_label,
    #                   param_custom_polygon, param_species, param_include_ca_geo_obscured,
    #                   param_include_ca_taxon_obscured, param_include_org_obscured, param_include_unobscured]
    #     inje.runiNatJurisdictionExportTool(parameters, None)
    parameters = [param_project_path, param_input_label, param_date_label, param_province, param_custom_label,
                  param_custom_polygon, param_species, param_include_ca_geo_obscured,
                  param_include_ca_taxon_obscured, param_include_org_obscured, param_include_unobscured]
    inje.runiNatJurisdictionExportTool(parameters, None)
