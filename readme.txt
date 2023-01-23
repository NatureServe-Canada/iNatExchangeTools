Export for CDCs from iNaturalist.ca

Data are provided in both file geodatabase (including relationship classes) and comma-separated value formats. The following iNaturalist tables are provided:
- observations_all, a merging of one or more of:
    - observations_ca_geo_obscured (iNaturalist.ca records with geoprivacy = obscured, with unobscured coordinates)
    - observations_ca_taxon_obscured (iNaturalist.ca records with taxon_geoprivacy = obscured, with unobscured coordinates)
    - observations_org_obscured (obscured iNaturalist.org records, with obscured coordinates)
	- observations_unobscured (records without geoprivacy or taxon_privacy)
- annotations
- comments
- conservation_statuses
- identifications
- observation_field_values
- observation_fields
- quality_metrics
- taxa
- users

Notes:
- A data model depicting table relationships is available at https://dbdiagram.io/d/6008af0480d742080a3734b9.
- If you are using ArcGIS Pro, you can use the Related Data feature on the "burger" menu on the attribute table to navigate among geodatabase observations and related records in other tables.
- The subset created for each jurisdiction includes observations named as being in the jurisdiction, or intersecting its 32km terrestrial buffer (this is the approximate maximum inacurracy introduced by iNaturalist obscuring) or 200nm marine buffer (but not outside Canada's Exclusive Economic Zone).
- Other tables above include only records related to the jurisdictional subset (except observation_fields and users, which include all records).
- See https://www.inaturalist.org/pages/help#geoprivacy for additional details on true locations of obscured records.
