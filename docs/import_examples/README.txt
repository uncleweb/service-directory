ver: 0.1
date: 28-01-2016

Welcome to the wonderful world of Service Directory CSV based data imports/exports!

As of this iteration, importing data into Service Directory is done in stages. Starting with base data and building towards the more complicated models.

This means that there will be multiple csv imports to do, each relying on the other.

The CSV import/export functionality can be found by accessing the Service Directory admin CMS and selecting any of the models. Then the import and export buttons should be at the top right.


Examples of the formats of these files can be found in this folder.


The import order is:
Countries
Categories
Keywords (which rely on Categories)
Country Areas (which rely on Countries)
Organisations (which rely on Countries, Country Areas)
Services (which rely on Organisations, Categories, Keywords)


Within the imports, certain models can be referred to by their Natural identifier (ie 'name') rather than a Numeric ID.

Countries, Categories, Keywords can be referred to by name

Country Areas, Organisations, Services must be referred to by numeric ID

Boolean (true/false) fields are set using 0 or 1 where 1 is true. NOT the text 'true','false','yes','no',etc...

The importer will use the appropriate identifier to both
 - Determine if the thing being imported is New or being Updated
 - Find models associated with the thing being imported and create appropriate relationships between them


When importing, after selecting the CSV file, you will see a preview of the changes that will be made by the import.


Some models accept lists of things to be associated with. These must be quoted and comma seperated in the CSV eg for importing a keyword with multiple categories:

name,categories,show_on_home_page
HIV,"Health,Education,Teenager",1

NOTE THAT THE CATEGORIES MUST ALREADY HAVE BEEN IMPORTED. This applies to all models that are referred to during the import. Eg Countries must already exist before they can be referred to by Organisations. That is why the import order is necessary for the moment.


An Organisation imported with multiple Country Areas would look like this:

id,name,about,address,telephone,email,web,country,areas,location
1,"Orphan Puppies","We're amazing","123 Place Rd","3209123","admin@test.com","http://www.google.com","South Africa","1,2","-33.891,18.505"

Notice that here we had to provide an ID for the organisation to correctly import. And that the Areas column is a comma seperated list of IDs.
Notice also the location is quoted, comma seperated, decimal, latitude and longitude.
