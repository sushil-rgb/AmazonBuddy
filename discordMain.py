from discordsFunctionalities.runBot import run_discord_bot
from scrapers.scraper import Amazon
import asyncio



if __name__ == '__main__':
    url = "https://www.amazon.co.jp/COGIT-Make-Hips-Bagel-Cushion/dp/B005CIY2QS/ref=lp_8436174051_1_2?sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D"
    print(asyncio.run(Amazon(url).dataByLink()))
    # run_discord_bot()

