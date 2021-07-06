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
import iNatProvinceExportTool
import iNatExchangeUtils


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'iNat Exchange Tools'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [iNatImport, iNatEBARExport, iNatProvinceExport]


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

        # Date Label
        param_date_label = arcpy.Parameter(
            displayName='Input Label',
            name='input_label',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_date_label.value = '3June2021'

        params = [param_project_path, param_input_label, param_date_label]
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
        ini = iNatImportTool()
        ini.runiNatImportTool(parameters, messages)
        return


