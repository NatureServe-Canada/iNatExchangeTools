# Project: iNatExchangeTools
# Credits: Randal Greene, Allison Siemens-Worsley
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: iNat Exchange Tools.py
# ArcGIS Python toolbox for importing and exporting iNaturalist data extracts

# Notes:
# - following 120 maximum line length "convention"
# - tested with ArcGIS Pro 2.8.1


# import python packages
import arcpy
import iNatImportTool
import iNatEBARExportTool
import iNatJurisdictionExportTool
import iNatExchangeUtils


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'iNat Exchange Tools'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [iNatImport, iNatEBARExport, iNatJurisdictionExport]


class iNatImport(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'iNat Import'
        self.description = 'Import iNaturalist.ca CSVs into working gdb'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Project Path
        param_project_path = arcpy.Parameter(
            displayName='Project Path',
            name='project_path',
            datatype='DEFolder',
            parameterType='Required',
            direction='Input')
        param_project_path.value = 'C:/GIS/iNatExchange'

        # Input Label
        param_input_label = arcpy.Parameter(
            displayName='Input Label',
            name='input_label',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_input_label.value = 'inaturalist-ca-5-20210603-1622752843'

        ## Date Label
        #param_date_label = arcpy.Parameter(
        #    displayName='Input Label',
        #    name='input_label',
        #    datatype='GPString',
        #    parameterType='Required',
        #    direction='Input')
        #param_date_label.value = '3June2021'

        params = [param_project_path, param_input_label]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ini = iNatImportTool.iNatImportTool()
        ini.runiNatImportTool(parameters, messages)
        return


class iNatEBARExport(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'iNat EBAR Export'
        self.description = 'Export iNaturalist.ca records into CSVs for EBAR import'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Project Path
        param_project_path = arcpy.Parameter(
            displayName='Project Path',
            name='project_path',
            datatype='DEFolder',
            parameterType='Required',
            direction='Input')
        param_project_path.value = 'C:/GIS/iNatExchange'

        # Input Label
        param_input_label = arcpy.Parameter(
            displayName='Input Label',
            name='input_label',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_input_label.value = 'inaturalist-ca-5-20210603-1622752843'

        params = [param_project_path, param_input_label]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        inee = iNatEBARExportTool.iNatEBARExportTool()
        inee.runiNatEBARExportTool(parameters, messages)
        return


class iNatJurisdictionExport(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'iNat Province Export'
        self.description = 'Export iNaturalist.ca records into GDB and CSVs for transfer to Provinces'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Project Path
        param_project_path = arcpy.Parameter(
            displayName='Project Path',
            name='project_path',
            datatype='DEFolder',
            parameterType='Required',
            direction='Input')
        param_project_path.value = 'C:/GIS/iNatExchange'

        # Input Label
        param_input_label = arcpy.Parameter(
            displayName='Input Label',
            name='input_label',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_input_label.value = 'inaturalist-ca-5-20210603-1622752843'

        # Date Label
        param_date_label = arcpy.Parameter(
            displayName='Date Label',
            name='date_label',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_date_label.value = '3June2021'

        # Province
        param_province = arcpy.Parameter(
            displayName='Province',
            name='province',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')
        param_province.filter.type = 'ValueList'
        # filter list gets overridden in updateParameters below
        param_province.filter.list = ['YT', 'NU', 'NT']
        param_province.value = 'NU'

        # Custom Jurisdiction Label
        param_custom_label = arcpy.Parameter(
            displayName='Custom Jurisdiction Label',
            name='custom_label',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        # Custom Jurisdiction Polygon
        param_custom_polygon = arcpy.Parameter(
            displayName='Custom Jurisdiction Polygon',
            name='custom_polygon',
            datatype='GPFeatureLayer',
            parameterType='Optional',
            direction='Input')

        # Include iNaturalist.ca Geoprivacy=Private
        param_include_ca_geo_private = arcpy.Parameter(
            displayName='Include iNaturalist.ca Geoprivacy=Private',
            name='include_ca_geo_private',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_include_ca_geo_private.value = 'true'

        # Include iNaturalist.ca Geoprivacy=Obscured
        param_include_ca_geo_obscured = arcpy.Parameter(
            displayName='Include iNaturalist.ca Geoprivacy=Obscured',
            name='include_ca_geo_obscured',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_include_ca_geo_obscured.value = 'true'

        # Include iNaturalist.ca Taxon Geoprivacy=Private
        param_include_ca_taxon_private = arcpy.Parameter(
            displayName='Include iNaturalist.ca Taxon Geoprivacy=Private',
            name='include_ca_taxon_private',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_include_ca_taxon_private.value = 'true'

        # Include iNaturalist.ca Taxon Geoprivacy=Obscured
        param_include_ca_taxon_obscured = arcpy.Parameter(
            displayName='Include iNaturalist.ca Taxon Geoprivacy=Obscured',
            name='include_ca_taxon_obscured',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_include_ca_taxon_obscured.value = 'true'

        # Include iNaturalist.org Private and Obscured
        param_include_org_private_obscured = arcpy.Parameter(
            displayName='Include iNaturalist.org Private and Obscured',
            name='include_org_private_obscured',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_include_org_private_obscured.value = 'true'

        # Include Unobscured
        param_include_unobscured = arcpy.Parameter(
            displayName='Include Unobscured',
            name='include_unobscured',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_include_unobscured.value = 'true'

        params = [param_project_path, param_input_label, param_date_label, param_province, param_custom_label,
                  param_custom_polygon, param_include_ca_geo_private, param_include_ca_geo_obscured,
                  param_include_ca_taxon_private, param_include_ca_taxon_obscured, param_include_org_private_obscured,
                  param_include_unobscured]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        param_province = parameters[3]
        param_province.filter.list = list(iNatExchangeUtils.prov_dict.keys())
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        inje = iNatJurisdictionExportTool.iNatJurisdictionExportTool()
        inje.runiNatJurisdictionExportTool(parameters, messages)
        return
