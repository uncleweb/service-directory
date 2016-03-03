DO $$

DECLARE health_category_id integer;
DECLARE education_category_id integer;
DECLARE test_keyword_id integer;
DECLARE hiv_keyword_id integer;
DECLARE tutoring_keyword_id integer;
DECLARE sa_country_id integer;
DECLARE healthcareco_org_id integer;
DECLARE hivtest_service_id integer;

BEGIN

-- to print a variable:
-- RAISE NOTICE 'health_category_id: %', health_category_id;

--category
INSERT INTO "api_category" (name,show_on_home_page) VALUES('Health',True) RETURNING id INTO health_category_id;
INSERT INTO "api_category" (name,show_on_home_page) VALUES('Education',False) RETURNING id INTO education_category_id;

--keyword
INSERT INTO "api_keyword" (name,show_on_home_page) VALUES('test',True) RETURNING id INTO test_keyword_id;
INSERT INTO "api_keyword" (name,show_on_home_page) VALUES('HIV',True) RETURNING id INTO hiv_keyword_id;
INSERT INTO "api_keyword" (name,show_on_home_page) VALUES('tutoring',True) RETURNING id INTO tutoring_keyword_id;

--keyword_categories
INSERT INTO "api_keyword_categories" (keyword_id,category_id) VALUES(test_keyword_id,health_category_id);
INSERT INTO "api_keyword_categories" (keyword_id,category_id) VALUES(test_keyword_id,education_category_id);
INSERT INTO "api_keyword_categories" (keyword_id,category_id) VALUES(hiv_keyword_id,health_category_id);
INSERT INTO "api_keyword_categories" (keyword_id,category_id) VALUES(tutoring_keyword_id,education_category_id);

--country
INSERT INTO "api_country" (name,iso_code) VALUES('South Africa','ZA') RETURNING id INTO sa_country_id;

--organisation
INSERT INTO "api_organisation" (name,about,address,telephone,email,web,country_id,location) VALUES('Healthcare Co','Something about them','202 The Gatehouse, Century Way, Century City','0215522159','blueteam@informationlogistics.co.za','http://www.informationlogistics.co.za',sa_country_id,'SRID=4326;POINT (18.5054960000000008 -33.8919369999999986)') RETURNING id INTO healthcareco_org_id;

--service
INSERT INTO "api_service" (name,verified_as,age_range_min,age_range_max,availability_hours,organisation_id) VALUES('Free HIV Test','',NULL,NULL,'8am to 5pm',healthcareco_org_id) RETURNING id INTO hivtest_service_id;

--service_categories
INSERT INTO "api_service_categories" (service_id,category_id) VALUES(hivtest_service_id,health_category_id);
INSERT INTO "api_service_categories" (service_id,category_id) VALUES(hivtest_service_id,education_category_id);

--service_keywords
INSERT INTO "api_service_keywords" (service_id,keyword_id) VALUES(hivtest_service_id,test_keyword_id);
INSERT INTO "api_service_keywords" (service_id,keyword_id) VALUES(hivtest_service_id,hiv_keyword_id);

END $$;
