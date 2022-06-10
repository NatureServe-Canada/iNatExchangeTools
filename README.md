# iNatExchangeTools
Tools for preparing iNaturalist data for jurisdictions and EBAR<br>
Credits: Randal Greene, Allison Siemens-Worsley<br>
� NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)<br>
Tested in ArcGIS Pro 2.8.1, but likely compatible with ArcMap 10.x and ArcGIS Pro 2.x<br>
<br>
Use:
- Copy/download iNatExhangeTools, including iNatExchangeTools.gdb, to local drive
- The Project Path can be the iNatExhangeTools folder or a new folder
- Obtain an iNaturalist extract and copy to an "Input" subfolder of the Project Path (authorized users can get it from https://www.inaturalist.org/sites/5; please contact carrie@inaturalist.org to request access)
- Run the iNat Import Tool first to copy/georeference the CSV data to a local geodatabase in the "Output" subfolder of the Project Path
- Then run the iNat EBAR Export and iNat Jurisdiction Export Tools to create output subsets
- Data transferred to Jurisdictions should include the readme.txt file provided here