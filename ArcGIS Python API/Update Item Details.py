from arcgis.gis import GIS

Username = "Username"
Password = "Password"

# Create connection
gis = GIS("https://www.arcgis.com", Username, Password)

# Search and create a list of content
fc = gis.content.search(query="contentstatus: org_authoritative AND type: Feature Service",sort_field="title",sort_order="asc", max_items=100 )

# Loop through item list
for item in fc:
  # title = item.title
  # id = item.id
  # des = item.description
  # type = item.type
  # typeKeywords = item.typeKeywords
  # tags = item.tags
  # credits = item.accessInformation
  # oldterms = item.licenseInfo
  item.update(item_properties={'licenseInfo':"Copyright 2018. Texas Department of Transportation. "
                                             "This data was produced for internal use within the Texas"
                                             " Department of Transportation and is made available to "
                                             "the public for informational purposes only. Accuracy is limited "
                                             "to the validity of available data as of date published."})
