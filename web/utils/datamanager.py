# Singleton class
import collections
import json

from django.conf import settings


class DataManager:
    __instance = None

    permission_list = ["inbox"]

    @staticmethod
    def getInstance():
        """ Static access method. """
        if DataManager.__instance is None:
            DataManager()
        return DataManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if DataManager.__instance:
            raise Exception("This class is a singleton!")
        else:
            DataManager.__instance = self

    def __read_file(self, path):
        with open(path, "r") as json_file:
            data = json_file.read()
            json_file.close()
            return data

    def __read_json(self, path):
        return json.loads(self.__read_file(path))

    def __menu_json(self):       
        return self.__read_json('sirmaya_admin/static/resources/menu.json')

    def __parent_category(self, permission):
        if not permission:
            return None
        else:
            return permission.split('-')[1]

    def __create_permission_groups(self, permissions):
        if not permissions:
            return None
        else:
            groupdict = collections.defaultdict(list)
            for permission in permissions:
                group = self.parent_category(permission)
                groupdict[group].append(permission)

            result = list(groupdict.values())

    def build_menu_json_for_sidebar(self, permission_groups=None):
        """ Take permissions from server, look up menu json and create new json to create side bar """
        permission_groups = [
            ['add-property', 'manage-property', 'upload-property'],
            ['property-meta'],
            ['add-project', 'manage-project', 'sort-project'],
            ['add-projectmeta-meta'],
            ['manage-dealers', ],
            ['add-developers','manage-developers'],
            ['manage-ibuying-enquiries'],
            ['manage-wanted-enquiries','add-area', 'manage-area'],
            ['manage-jv-enquiries','manage-fp','manage-finance-enquiries'],
            # ['add-fp', 'manage-fp'],
            # ['manage-finance-enquiries'],
            ['add-job', 'manage-job'],
            ['add-propertycontent', 'manage-propertycontent'],
            # ['add-landing-content', 'manage-landing-content'],
            ['add-landing-content', 'manage-landing-content', 'ceo-message'],
            # ['add-seo-content', 'manage-seo-content', "Common Script"],
            ['add-seo-content'],
            ['add-city-filter-console'],
            ['manage-homepagevideo'],
            ['add-dealermeta-filter-console'],
            ['add-about-content'],
            ['add-privacy-policy-content'],
            ['add-faq', 'manage-faq'],
            ['manage-dealers2', 'charts-dealers2', 'hits-dealers2', 'user-dealers2'],
            ['send-sms', 'sms-scheduler', 'sms-logs'],
            ['New-Adds', 'Manage-Adds'],
            ['new-users', 'manage-users'],
            ['new-listings', 'user-listings'],
            ['new-users2', 'manage-users2'],
            ['manage-operations'],
        ]

        menu_json = self.__menu_json()
        new_menu_items = []

        for permission_group in permission_groups:
            new_menu_item_dict_value = {}
            subs_categories = []

            parent_category = self.__parent_category(permission_group[0])
            existing_menu_item_dict = menu_json[parent_category]
            new_menu_item_dict_value["title"] = existing_menu_item_dict["title"]
            new_menu_item_dict_value["icon_class"] = existing_menu_item_dict["icon_class"]
            new_menu_item_dict_value["is_href"] = existing_menu_item_dict.get('is_href')
            new_menu_item_dict_value["min_acl"] = existing_menu_item_dict.get('min_acl')
            new_menu_item_dict_value["href"] = f'{settings.HOST_URL}/{existing_menu_item_dict.get("href")}'

            for permission in permission_group:
                if permission in existing_menu_item_dict.keys():
                    subs_categories.append(existing_menu_item_dict[permission])
            
            new_menu_item_dict_value["subs"] = subs_categories
            new_menu_item = new_menu_item_dict_value
            new_menu_items.append(new_menu_item)
        return new_menu_items
