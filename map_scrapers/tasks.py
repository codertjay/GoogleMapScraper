import csv
import re
import time
from urllib.parse import urlencode

import requests
from celery import shared_task
from decouple import config

from map_scrapers.helper import supported_types
from map_scrapers.models import History, SearchInfo

api_key = config("GOOGLE_MAP_API_KEY")

#  Once the proxy is available
# Proxy server to use
proxies = {
    # 'http': 'http://username:password@proxyserver:port',
    # 'https': 'http://username:password@proxyserver:port'
}
rating_list = [
    {
        "minimum_rating": 0,
        "maximum_rating": 5,
    }, {
        "minimum_rating": 0,
        "maximum_rating": 1,
    }, {
        "minimum_rating": 1,
        "maximum_rating": 2,
    }, {
        "minimum_rating": 2,
        "maximum_rating": 3,
    }, {
        "minimum_rating": 4,
        "maximum_rating": 5,
    },
]


def get_email_from_website(url):
    try:
        """This gets an email address"""
        response = requests.get(url, timeout=5)
        # Extract all emails from the website

        emails = re.findall(r'\b(?!.*@sentry\.com)[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)

        for email in emails:
            if "sentry" not in email:
                return email
        return None
    except Exception as a:
        print("a", a)
        return None


def get_social_media_links(url):
    social_media_links = ""

    try:
        response = requests.get(url, timeout=5)
        html_content = response.text

        # Define regular expressions for each social media platform
        facebook_regex = "(?:https?:)?\/\/(?:www\.)?(?:facebook|fb)\.com\/(?P<profile>(?![A-z]+\.php)(?!marketplace|gaming|watch|me|messages|help|search|groups)[A-z0-9_\-\.]+)\/?"
        twitter_regex = "(?:https?:)?\/\/(?:[A-z]+\.)?twitter\.com\/@?(?!home|share|privacy|tos)(?P<username>[A-z0-9_]+)\/?"
        youtube_channel_regex = "(?:https?:)?\/\/(?:[A-z]+\.)?youtube.com\/channel\/(?P<id>[A-z0-9-\_]+)\/?"
        youtube_user_regex = "(?:https?:)?\/\/(?:[A-z]+\.)?youtube.com\/user\/(?P<username>[A-z0-9]+)\/?"
        linkedin_regex = "(?:https?:)?\/\/(?:[\w]+\.)?linkedin\.com\/(?P<company_type>(company)|(school))\/(?P<company_permalink>[A-z0-9-À-ÿ\.]+)\/?"
        instagram_regex = "(?:https?:)?\/\/(?:www\.)?(?:instagram\.com|instagr\.am)\/(?P<username>[A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)"

        # Find all social media links in the HTML content
        links = {
            "Facebook": list(set(re.findall(facebook_regex, html_content))),
            "Twitter": list(set(re.findall(twitter_regex, html_content))),
            "Instagram": list(set(re.findall(instagram_regex, html_content))),
            "LinkedIn": list(set(re.findall(linkedin_regex, html_content))),
            "YouTube_Channel": list(set(re.findall(youtube_channel_regex, html_content))),
            "YouTube_User": list(set(re.findall(youtube_user_regex, html_content))),
        }

        # Format the social media links as a string with the requested format
        for key, value in links.items():
            try:
                if key == "Facebook":
                    if len(value) > 0:
                        social_media_links += f"Facebook:  https://www.facebook.com/{value[-1]}/   "
                elif key == "Twitter":
                    if len(value) > 0:
                        social_media_links += f"Twitter:  https://www.Twitter.com/{value[-1]}/    "
                elif key == "Instagram":
                    if len(value) > 0:
                        social_media_links += f"Instagram:  https://www.Instagram.com/{value[-1]}/ "
                elif key == "LinkedIn":
                    if len(value) > 0:
                        social_media_links += f"LinkedIn:  https://www.LinkedIn.com/company/{value[-1][-1]}/  "
                elif key == "YouTube_Channel":
                    if len(value) > 0:
                        social_media_links += f"YouTube_Channel:  https://www.youtube.com/channel/{value[-1]}/  "
                elif key == "YouTube_User":
                    if len(value) > 0:
                        social_media_links += f"YouTube_Channel:  https://www.youtube.com/user/{value[-1]}/  "
            except Exception as a:
                print(a)
    except Exception as a:
        print("Error getting social")
    return social_media_links


def get_textsearch(query_string):
    place_ids = []
    try:
        url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={query_string}&key={api_key}'
        time.sleep(5)
        response = requests.get(url)
        # Check if there are additional pages of results
        data = response.json()

        if response.status_code == 200:
            for item in response.json().get("results"):
                place_ids.append(item.get("place_id"))
            # get the next page
            while 'next_page_token' in data:
                # Add the "pagetoken" parameter to the query string
                page_token = data['next_page_token']
                time.sleep(5)
                next_url = f'{url}&pagetoken={page_token}'
                response = requests.get(next_url)
                data = response.json()
                # Process the next page of results
                for item in data.get("results"):
                    place_ids.append(item.get("place_id"))
    except:
        pass
    return place_ids


@shared_task
def get_all_place(query, category, user_id, search_info_id):
    """
   This get all the places
    """
    place_ids = []

    search_info = SearchInfo.objects.filter(id=search_info_id).first()
    if not search_info:
        return True
    # split with the string
    query = query.strip("[]").split(",")
    for item in query:
        try:
            item = item.replace('"', "")
            query_string = f"{category} in {item}"
            # add the place ids
            place_ids += get_textsearch(query_string)
        except:
            pass
    # Use textsearch
    for rating in rating_list:
        for item in query:
            try:
                item = item.replace('"', "")
                query_string = f'{category} in {item}&minimum_rating={rating.get("minimum_rating")}&maximum_rating={rating.get("maximum_rating")}'
                # add the place ids
                place_ids += get_textsearch(query_string)
            except:
                pass

    # Get open now and close now
    for item in query:
        try:
            item = item.replace('"', "")
            query_string = f'{category} in {item}&opennow=true'
            # add the place ids
            place_ids += get_textsearch(query_string)
        except:
            pass
    # Get open now and close now
    for item in query:
        try:
            item = item.replace('"', "")
            query_string = f'{category} in {item}&opennow=false'
            # add the place ids
            place_ids += get_textsearch(query_string)
        except:
            pass
    # Get base on price
    for price in range(0, 4):
        for item in query:
            try:
                item = item.replace('"', "")
                query_string = f'{category} in {item}&minprice={price}&maxprice={price + 1}&'
                # add the place ids
                place_ids += get_textsearch(query_string)
            except:
                pass
    # Get base on type
    for item in query:
        try:

            query_string = f'{item}&type={category.lower()}&'
            # add the place ids
            place_ids += get_textsearch(query_string)
        except:
            pass
    # Get base on type and add in
    for item in query:
        try:

            query_string = f'{category} in {item}&type={category.lower()}&'
            # add the place ids
            place_ids += get_textsearch(query_string)
        except:
            pass

    # Deduplicate the place IDs
    place_ids = list(set(place_ids))
    search_info.total_places = len(place_ids)
    search_info.save()
    for place_id in place_ids:
        time.sleep(10)
        get_place_detail_and_save.delay(place_id, user_id, search_info.id)
    return True


@shared_task
def get_place_detail_and_save(place_id, user_id, search_info_id):
    """
    this get a single place with the id provided
    :param place_id:
    :return:
    """
    # Set up API parameters
    params = {
        "place_id": place_id,
        "key": api_key
    }
    # Send API request
    response = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params=params)
    if response.status_code == 200:
        data = response.json().get("result")
        #  if no data pass
        if not data:
            return False
        website = data.get("website")
        business_name = data.get("name")
        full_address = data.get("formatted_address")
        street = data.get("vicinity")
        phone_number = data.get("formatted_phone_number")
        cid = data["url"].split("=")[-1]
        opening_hours = data.get("opening_hours", {}).get("weekday_text")
        if opening_hours:
            opening_hours_formatted = []
            for hours in opening_hours:
                day, open_close_hours = hours.split(": ")
                opening_hours_formatted.append(f"{day}: [{open_close_hours}]")
            opening_hours = ", ".join(opening_hours_formatted)
        else:
            opening_hours = "Not Available"
        google_map_url = data["url"]
        latitude = data["geometry"]["location"]["lat"]
        longitude = data["geometry"]["location"]["lng"]
        reviews_url = f"https://search.google.com/local/reviews?{urlencode({'placeid': place_id, 'q': business_name + ', ' + full_address, 'authuser': 0, 'hl': 'en', 'gl': 'US'})}"
        average_rating = data.get("rating")
        review_count = data.get("user_ratings_total")
        categories = ", ".join(category for category in data.get("types", []))
        phones = data.get("international_phone_number")
        plus_code = data.get("plus_code", {}).get("global_code", "")
        municipality = "Not Available"
        if 'address_components' in data:
            city = state = zip_code = None
            for component in data.get("address_components", []):
                if 'locality' in component.get('types', []):
                    city = component['long_name']
                elif 'administrative_area_level_1' in component.get('types', []):
                    state = component.get('short_name', [])
                elif 'postal_code' in component.get('types', []):
                    zip_code = component.get('long_name', [])
                if city and state and zip_code:
                    break
            if city and state:
                municipality = f"{city}, {state} {zip_code}"

        # Get social media links
        social_media_links = "Not Available"
        if website:
            social_media_links = get_social_media_links(website)

        #  if length is greater than zero
        image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSX1mtYL8f3jCPWwGO9yCiCJlbi8LikmuJMew"
        if data.get("photos"):
            #  get the real image url
            image = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={data.get('photos')[0].get('photo_reference')}&key={api_key}"
            response = requests.head(image, allow_redirects=True)
            image = response.url

        try:
            if website:
                email = get_email_from_website(website)
            else:
                email = None

            # check if the email exist with that user before
            search_info = SearchInfo.objects.filter(id=search_info_id).first()
            if search_info:
                search_info.scraped_places += 1
                search_info.save()
                if search_info.scraped_places >= search_info.total_places:
                    search_info.completed = True
                    search_info.save()

                history = History.objects.create(
                    user_id=user_id,
                    search_info_id=search_info_id,
                    phone_number=phone_number,
                    place_id=place_id,
                    email=email,
                    business_name=business_name,
                    full_address=full_address,
                    street=street,
                    cid=cid,
                    image=image,
                    municipality=municipality,
                    plus_code=plus_code,
                    social_media_links=social_media_links,
                    opening_hours=opening_hours,
                    google_map_url=google_map_url,
                    latitude=latitude,
                    longitude=longitude,
                    reviews_url=reviews_url,
                    average_rating=average_rating,
                    review_count=review_count,
                    website=website,
                    categories=categories,
                    phones=phones,
                )
            print("History Created")
        except Exception as a:
            print("error occured crating history", a)
        return True


@shared_task
def create_item_task(decoded_file, user_id):
    """
    this is used to update the item which are updated from the csv
    :param decoded_file:
    :return:
    """
    #  read the csv in dictionary format
    for row in csv.DictReader(decoded_file):
        print("the row", row)
        try:
            query = row.get("query")
            category = row.get("category")
            print("query", query)
            print("category", category)
            get_all_place.delay(query, category, user_id)
        except Exception as a:
            print("The error was ", a)
