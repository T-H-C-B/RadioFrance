from dataclasses import dataclass
from typing import List, Optional
from bs4 import BeautifulSoup
import requests
import time

@dataclass
class Data:
    uuid: str
    path: Optional[str]
    published_date: str
    updated_date: str
    name: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[str]
    isOrganisation: bool
    body: Optional[str]
    gender: Optional[str]
    url: Optional[str]
    station_id: List[int]
    alternateNames: Optional[str]
    relationships: Optional[str]
    connections: Optional[str]
    country: Optional[str] = None

# For CSV Parsing
import csv

def parse_csv(filename: str) -> List[Data]:
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)

        data_objects = []
        for row in reader:
            data = Data(
                uuid=row[0],
                path=row[1] if row[1] else None,
                published_date=row[2],
                updated_date=row[3],
                name=row[4],
                first_name=row[5] if row[5] else None,
                last_name=row[6] if row[6] else None,
                role=row[7] if row[7] else None,
                isOrganisation=(row[8].lower() == 'true'),
                body=row[9] if row[9] else None,
                gender=row[10] if row[10] else None,
                url=row[11] if row[11] else None,
                station_id=[int(x) for x in row[12][1:-1].split(',')] if row[12] else [],
                alternateNames=row[13] if row[13] else None,
                relationships=row[14] if row[14] else None,
                connections=row[15] if row[15] else None
            )
            data_objects.append(data)

    return data_objects

def find_most_country_occurence(data_list: List[Data]) -> str:
    countries = {}
    for data in data_list:
        if data.country:
            if data.country in countries:
                countries[data.country] += 1
            else:
                countries[data.country] = 1
    return max(countries, key=countries.get)


def export_to_new_csv(newcsvPath: str, data_list: List[Data]):
    with open(newcsvPath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(["uuid", "path", "published_date", "updated_date", "name", "first_name", "last_name",
                         "role", "isOrganisation", "body", "gender", "url", "station_id", "alternateNames",
                         "relationships", "connections", "country"])

        for data in data_list:
            writer.writerow([
                data.uuid,
                data.path,
                data.published_date,
                data.updated_date,
                data.name,
                data.first_name,
                data.last_name,
                data.role,
                data.isOrganisation,
                data.body,
                data.gender,
                data.url,
                ",".join(map(str, data.station_id)),
                data.alternateNames,
                data.relationships,
                data.connections,
                data.country
            ])

def initialize_csv(newcsvPath: str):
    """Initialize the CSV with headers."""
    with open(newcsvPath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["uuid", "path", "published_date", "updated_date", "name", "first_name", "last_name",
                         "role", "isOrganisation", "body", "gender", "url", "station_id", "alternateNames",
                         "relationships", "connections", "country"])

def append_to_csv(newcsvPath: str, data: Data):
    """Append the data to the CSV."""
    with open(newcsvPath, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            data.uuid,
            data.path,
            data.published_date,
            data.updated_date,
            data.name,
            data.first_name,
            data.last_name,
            data.role,
            data.isOrganisation,
            data.body,
            data.gender,
            data.url,
            ",".join(map(str, data.station_id)),
            data.alternateNames,
            data.relationships,
            data.connections,
            data.country
        ])

data_list = parse_csv('personnality.csv')

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

headers = {'User-Agent': USER_AGENT}

data_list = parse_csv('personnality.csv')

initialize_csv('personnality_with_country.csv')

for data in data_list:
    try:
        r = requests.get('https://forebears.io/fr/surnames?q=' + data.last_name, headers=headers)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            search_result = soup.find(class_='search-result')
            if search_result:
                details = search_result.find_all(class_='detail-value')
                if details and len(details) > 2:
                    if details[2].has_attr('title'):
                        country = details[2]['title']
                        print(f"Last Name: {data.last_name}, Country: {country}")
                        data.country = country
                    else:
                        print(f"Unable to find country title for {data.last_name}")
                else:
                    print(f"Insufficient details for {data.last_name}")
            else:
                print('No search result for ' + data.last_name)
        else:
            print(f"Error {r.status_code} for {data.last_name}")

        append_to_csv('personnality_with_country.csv', data)
    except Exception as e:
        print(f"Exception occurred while processing {data.last_name}. Error: {e}")

export_to_new_csv('personnality_with_country.csv', data_list)


