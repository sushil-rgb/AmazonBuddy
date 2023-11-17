from tools.tool import TryExcept, yaml_load, userAgents, Response
from bs4 import BeautifulSoup
import re


class Amazon:
    """
    The Amazon class provides methods for scraping data from Amazon.com.

    Attributes:
        headers (dict): A dictionary containing the user agent to be used in the request headers.
        catch (TryExcept): An instance of TryExcept class, used for catchig exceptions.
        scrape (yaml_load): An instance of the yaml_load class, used for selecting page elements to be scraped.
    """

    def __init__(self, userInput):
        """
        Initializes an instance of the Amazon class.
        """
        self.userInput = userInput
        self.headers = {'User-Agent': userAgents()}
        self.catch = TryExcept()
        self.scrape = yaml_load('selector')

    async def status(self):
        response = await Response(self.base_url).response()
        return response

    async def getASIN(self):
        """
        Extracts the ASIN (Amazon Standard Identification Number) from the given URL.

        Args:
            url (str): The URL to extract the ASIN from.

        Return:
            str: The ASIN extracted from the URL.

        Raises:
            IndexError: If the ASIN cannot be extracted from the URL.
        """
        pattern = r"(?<=dp\/)[A-Za-z|0-9]+"
        try:
            asin = (re.search(pattern, self.userInput)).group(0)
        except Exception as e:
            asin = "N/A"
        return asin

    async def dataByAsin(self):
        """
        Extracts product information from the Amazon product page by ASIN (Amazon Standard Identification Number).

        Args:
            -asin (str): The ASIN of the product to extract informatio from.

        Returns:
            -dict: A dictionary containing product information, including name, price, rating, rating count, availability,
                   hyperlink, image link, store, and store link.

        Raises:
            -AttributeError: If the product information cannot be extracted from the page.
        """
        # Construct the URL using the ASIN:
        url = f"https://www.amazon.com/dp/{self.userInput}"
        # Retrieve the page content using 'static_connection' method:
        content = await Response(url).content()
        soup = BeautifulSoup(content, 'lxml')
        try:
            # Try to extract the image link using the second first selector.
            image_link = soup.select_one(self.scrape['image_link_i']).get('src')
        except Exception as e:
            image_link = soup.select_one(self.scrape['image_link_ii']).get('src')
        # finally:
        #     # If the image link cannot be extracted, return an error message:
        #     return f'Content loading error. Please try again in few minutes. Error message || {str(e)}.'
        try:
            availabilities = soup.select_one(self.scrape['availability']).text.strip()
        except AttributeError:
            availabilities = 'In stock'
        store = await self.catch.text(soup.select_one(self.scrape['store']))
        store_link = f"""https://www.amazon.com{await self.catch.attributes(soup.select_one(self.scrape['store']), 'href')}"""
        # Construct the data dictionary containing product information:
        datas = {
            'Name': await self.catch.text(soup.select_one(self.scrape['name'])),
            'ASIN': await self.getASIN(),
            'Price': await self.catch.text(soup.select_one(self.scrape['price_us'])),
            'Rating': await self.catch.text(soup.select_one(self.scrape['review'])),
            'Rating count': await self.catch.text(soup.select_one(self.scrape['rating_count'])),
            'Availability': availabilities,
            'Hyperlink': url,
            'Image': image_link,
            'Store': store,
            'Store link': store_link,

        }
        return datas

    async def product_review(self):
        """
            Extracts product reviews from the Amazon product reviews page.

            Returns:
                -dict: A dictionary containing product review information, including top positive and top critical reviews.

            Raises:
                -AttributeError: If the review information cannot be extracted from the page.
        """
        # Get ASIN asynchronously:
        asin = await self.getASIN()
        # From the URL for Amazon product reviews:
        review_url = f"https://www.amazon.com/product-reviews/{asin}"
        req = await Response(review_url).content()
        soup = BeautifulSoup(req, 'lxml')
        pos_crit_review = soup.select_one(self.scrape['pos_criti_review'])
        review_lists = soup.select_one(self.scrape['review_lists']).text.strip()
        # Check if positive and critical reviews are present
        if pos_crit_review is not None:
            profile_name = soup.select(self.scrape['profile_name'])
            review_title = soup.select(self.scrape['full_review'])
            stars = soup.select(self.scrape['stars'])
            review_title = soup.select(self.scrape['review_title'])
            full_review = soup.select(self.scrape['full_review'])
            product = soup.select_one(self.scrape['product_name']).text.strip()
            image = soup.select_one(self.scrape['image']).get('src')
            # Populate datas dictionary for positive and critical reviews
            datas = {
                'top positive review':
                    {
                        'product': product,
                        'customer': profile_name[0].text.strip(),
                        'stars': stars[0].text.strip(),
                        'title': review_title[0].text.strip(),
                        'review': full_review[0].text.strip(),
                        'image': image,
                    },
                'top critical review':
                    {
                        'product': product,
                        'customer': profile_name[-1].text.strip(),
                        'stars': stars[-1].text.strip(),
                        'title': review_title[-1].text.strip(),
                        'review': full_review[-1].text.strip(),
                        'image': image,
                    }
            }
        # Check if there are no positive and critical reviews, but there are review lists
        elif pos_crit_review is None and review_lists != "":
            profile_name = soup.select(self.scrape['profile_name'])
            review_title = soup.select(self.scrape['full_review'])
            stars = soup.select(self.scrape['stars_i'])
            review_title = soup.select(self.scrape['review_title_i'])
            full_review = soup.select(self.scrape['full_review_i'])
            product = soup.select_one(self.scrape['product_name']).text.strip()
            image = soup.select_one(self.scrape['image']).get('src')
            datas = {
                'top positive review':
                    {
                        'product': product,
                        'customer': profile_name[0].text.strip(),
                        'stars': stars[0].text.strip(),
                        'title': review_title[0].text.strip(),
                        'review': full_review[0].text.strip(),
                        'image': image,
                    },
                'top critical review':
                    {
                        'product': product,
                        'customer': profile_name[-1].text.strip(),
                        'stars': stars[-1].text.strip(),
                        'title': review_title[-1].text.strip(),
                        'review': full_review[-1].text.strip(),
                        'image': image,
                    }
            }
        # Handle the case where there are no reviews
        else:
            datas = soup.select_one(self.scrape['no_reviews']).text.strip()
        return datas

