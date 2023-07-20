import re
from main.models import City, Lookup

import xml.etree.ElementTree as ET


def price_converter(am):

    digits_in_lakh = 100000
    digits_in_crore = 10000000
    digits = re.findall('\d*\.?\d+', am)
    output = 0

    if 'Lakh' in am:
        output = float(digits[0]) * digits_in_lakh
        output = int(round(output, -3))
    if 'Crore' in am:
        output = float(digits[0]) * digits_in_crore
        output = int(round(output, -3))
    return output


#
def get_type(_type):
    # type = LookupCategory.objects.get(parent_id=1).id
    if _type == "Plot Form":
        _type = "Plot File"
    a = Lookup.objects.get(name=_type,lookup_category_id__in=[2,3,4,9.18]).id
    return a


def get_area_unit(_area_unit):
    return Lookup.objects.get(name=_area_unit).id


def get_area_unit_by_id(unit_id):
    return Lookup.objects.get(id=unit_id).name.lower()


def get_type_by_id(type_id):
    _type = Lookup.objects.get(id=type_id).name.lower()
    # Building
    # Factory
    # Office
    # Other
    # Shop
    # Commercial Plot
    # Farmhouse Plot
    # Plot File
    # Residential Plot
    # Farm house
    # Flat
    # House
    # Warehouse
    # Industrial Land
    # Agricultural Land

    # coding for SEO purpseo
    if _type == 'house' or _type == 'flat' or _type == 'appartment' or _type == 'farm house' or _type == 'pent house' or _type == 'portion':
        return 'residential'
    elif _type == 'plaza' or _type == 'shop' or _type == 'building' or _type == 'office' or _type == 'ware house' or _type == 'factory' or _type == 'other':
        return 'commercial'
    elif _type == 'agricultural land' or _type == 'industrial land' or _type == 'residential plot' or _type == 'commercial plot' or _type == 'plot file':
        return 'plots'


def get_city_by_id(city_id):
    city = City.objects.get(id=city_id).name
    return city


def get_purpose(_pupose):
    purpose = _pupose

    if "Rent" in purpose:
        purpose = 22
    elif "Sale" in purpose:
        purpose = 23
    return purpose


def get_purpose_by_id(_id):
    return Lookup.objects.get(id=_id).name



# def get_purpose(_type):
#     return Lookup.objects.get(name=_type).id


def get_city(_city):
    _city = _city.strip()
    return City.objects.get(name=_city)


def validate_property(array):
    print(array)
    errors = ''
    is_valid = True
    if not array[2]:
        errors += "Property Type Not Available"
        is_valid = False
        return [errors, is_valid]
    if not array[8]:
        errors += "Property Purpose Not Available"
        is_valid = False
        return [errors, is_valid]

    if not array[0]:
        errors += "Property Title Not Available"
        is_valid = False
        return [errors, is_valid]
    if not array[1]:
        errors += "Property Description Not Available"
        is_valid = False
        return [errors, is_valid]
    if not array[6]:
        errors += "Property Land Area Not Available"
        is_valid = False
        return [errors, is_valid]
    if not array[3]:
        errors += "Property Price Not Specified"
        is_valid = False
        return [errors, is_valid]
    if not array[4]:
        errors += "Property Area Not Available"
        is_valid = False
        return [errors, is_valid]
    if not array[5]:
        errors += "Property City Not Available"
        is_valid = False
        return [errors, is_valid]
    if not array[7]:
        errors += "Property Area Unit Not Available"
        is_valid = False
        return [errors, is_valid]

    return [errors, is_valid]


def parse_xml(xmlfile, state):
    # create element tree object
    tree = ET.parse(xmlfile)

    # get root element
    root = tree.getroot()

    # create empty list for news items
    links = []

    if state == 'property':
        for child in root:
            for item in child:
                if 'dealer' not in item.text and 'static' not in item.text:
                    links.append(item.text)
    else:
        for child in root:
            for item in child:
                if 'dealer' in item.text or 'static' in item.text:
                    links.append(item.text)


    return links


