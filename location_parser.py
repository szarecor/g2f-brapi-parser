import csv
import json


def generate_location_additional_info_data():
    locations = []

    with open('raw_data/Carolyn_Lawrence_Dill_G2F_Mar_2017/z._2015_supplemental_info/g2f_2015_field_metadata.csv', 'r') as field_metadata_handle:

        reader = csv.DictReader(field_metadata_handle)

        for row in reader:

            # TODO: probably find a better location ID than the Experiment ID:
            id = row.get('Experiment')

            locations.append({
                'locationDbId': id,
                'weatherStationLatitude': row.get('WS Lat'),
                'weatherStationLongitude': row.get('WS Lon'),
            })

    return locations



def generate_location_additional_info_fixture():

    in_data = generate_location_additional_info_data()
    out_data = []

    ''' DB Columns are:
    cropDbId, locationDbId, key, value 
    '''

    for row in in_data:

        v = row.get('weatherStationLatitude') or None

        if v:
            out_data.append({
                'model': 'jsonapi.LocationAdditionalInfo',
                'fields': {
                    'cropDbId': 'maize',
                    'locationDbId': row.get('locationDbId'),
                    'key': 'weatherStationLatitude',
                    'value': row.get('weatherStationLatitude'),
                }
            })

        v = row.get('weatherStationLongitude') or None

        if v:
            out_data.append({
                'model': 'jsonapi.LocationAdditionalInfo',
                'fields': {
                    'cropDbId': 'maize',
                    'locationDbId': row.get('locationDbId'),
                    'key': 'weatherStationLongitude',
                    'value': row.get('weatherStationLongitude'),
                }
            })

    return out_data



def generate_primary_location_data():
    ''' Creates a file of LOCATIONS (fields) to be imported into python-brapi DB via the admin UI '''

    # python-brapi expects these fields:
    # cropDbId, locationDbId, type, name, abbreviation, countryCode, countryName, latitude, longitude, altitude, instituteName, instituteAddress
    # According to https://brapi.docs.apiary.io/#reference/locations, the first three fields are required and the remaining are optional


    # The csv data looks like this:
    # Experiment	Type	Treatment	City	WS_SN	WS Lat	WS Lon	DateIn	DateOut	Previous Crop	Tillage	PlotLen	AlleyLen	RowSp	PlanterType	KernelsPerPlot	Moisture Meter	LBS for  test	corner1 lat	corner1 lon	corner 2lat	corner2 lon	corner3 lat	corner3 lon	corner4 lat	corner4 lon	Cardinal	date of soil sampling	preplant herb	postplant herb	total N	total P	total K	fert dates 1	fert dates 2	fert dates 3	fert dates 4	fert dates 5	fert dates 6	fert dates 7	fert dates 8	Type of Fert	Insecticide
    # AZI1	Inbred	Irrigated	Willcox	8639	32.034726	-109.692471	6/28/15	10/7/15	Corn	Disk	15	24	30	air planter	20			32.034293	-109.69252	32.03438	-109.692344	32.034864	-109.692338	32.034793	-109.692518			Makaze, Glyphosate (isopropylamine salt); Medal II EC, S-metolachlor; Eptam, S-ethyl dipropylthiocarbamate; Trifluralin HF, Trifluralin; Atrazine 4L, Atrazine	Cadet; Fluthiacet-methyl	118	0	0	6/12/15	6/13/15	6/18/15	6/19/15	6/22/15	6/25/15	6/28/15	7/7/15	UAN; 32-0-0	Coragen; Chlorantraniliprole


    locations = []

    LOCATION_TYPE = 'Field Trial'
    CROP_ID = 'maize'


    with open('raw_data/Carolyn_Lawrence_Dill_G2F_Mar_2017/z._2015_supplemental_info/g2f_2015_field_metadata.csv', 'r') as field_metadata_handle:

        reader = csv.DictReader(field_metadata_handle)
        #experiments = set([row['Experiment'] for row in reader])

        field_metadata_handle.seek(0)

        for row in reader:
            # The lat/lon columns are as follows (notice the inconsistentcy for 'corner 2lat':
            # corner1 lat
            # corner1 lon
            # corner 2lat
            # corner2 lon
            # corner3 lat
            # corner3 lon
            # corner4 lat
            # corner4 lon

            lats = (float(row.get('corner1 lat') or 0), float(row.get('corner 2lat') or 0), float(row.get('corner3 lat') or 0), float(row.get('corner4 lat') or 0))

            avg_lat = sum(lats)/4

            lons = (float(row.get('corner1 lon') or 0), float(row.get('corner2 lon') or 0), float(row.get('corner3 lon') or 0), float(row.get('corner4 lon') or 0))

            avg_lon = sum(lons)/4


            # The CSV apparently doesn't containt a field for state, so we need to extract that from the Experiment column:
            state_or_province = row['Experiment'][:2]

            if state_or_province == 'ON':
                country_name = 'Canada'
                country_code = 'CAN'
            else:
                country_name = 'United States'
                country_code = 'USA'

            # TODO: probably find a better location ID than the Experiment ID:
            id = row.get('Experiment')
            #lat = row.get('WS Lat')
            #lon = row.get('WS Lon')
            city = row.get('City').rstrip(", Texas") or "?"

            if city.endswith(state_or_province):
                city_and_state = city
                city = city.rstrip(" , " + state_or_province)
            else:
                city_and_state = ", ".join((city, state_or_province))

            loc = {
                'cropDbId': CROP_ID,
                'locationDbId': id,
                'type': LOCATION_TYPE,
                'name': city_and_state,
                'abbreviation': city,
                'countryCode': country_code,
                'countryName': country_name,
                'latitude': avg_lat,
                'longitude': avg_lon,
            }

            locations.append(loc)

        return locations




def generate_primary_location_fixture():

    in_data = generate_primary_location_data()
    out_data = []

    for item in in_data:
        loc = {
            'model': 'jsonapi.Location',
            'fields': item,
        }

        out_data.append(loc)

    return out_data




if __name__ == '__main__':


    #fixture_str = json.dumps(generate_primary_location_fixture(), indent=3)
    #print(fixture_str)


    fixture_data = generate_location_additional_info_fixture()
    print(json.dumps(d, indent=3))
