import os 
from urllib.request import urlretrieve
from utils import download_files
import argparse
from add_red_line import add_red_line

parser = argparse.ArgumentParser(description='Compute Commmute Statistics for Downstram Analysis')
parser.add_argument('--otp_path', type=str, default = 'otp_current', help='path of the Open Trip Planner')
parser.add_argument('--red_line', action=argparse.BooleanOptionalAction, help='Indicator of whether to resimulate red line')
parser.add_argument('--period', type = float, default = 8)
parser.add_argument('--speed', type = float, default = 20)
args = parser.parse_args()

otp_path = args.otp_path
red_line = args.red_line
period = args.period
speed = args.speed

os.chdir(f"../")

if red_line:
    otp_path = f'{otp_path}_speed_{speed}_period_{period}'
    os.makedirs(otp_path, exist_ok=True)
    os.system(f"cp -R red_line_prototype {otp_path}/gtfs_red_line_speed_{speed}_period_{period}/")
    add_red_line(otp_path, period = period, speed = speed)

os.makedirs(otp_path, exist_ok=True)
for tranit_type in ["local-bus", "light-rail", "metro", "marc", "commuter-bus"]:
    transit_gtfs_file = f"{otp_path}/mdotmta_gtfs_{tranit_type}"
    os.makedirs(transit_gtfs_file, exist_ok=True)
    if not os.path.isfile(transit_gtfs_file):
        url = f"https://feeds.mta.maryland.gov/gtfs/{tranit_type}"
        download_files(url, transit_gtfs_file)

osm_file = "maryland-latest.osm.pbf"
if not os.path.isfile(f"{otp_path}/{osm_file}"):
        url = f"https://download.geofabrik.de/north-america/us/{osm_file}"
        urlretrieve(url, f"{otp_path}/{osm_file}")

version = "2.2.0"
otp_file = f"otp-{version}-shaded.jar"
if not os.path.isfile(f"{otp_path}/{otp_file}"):
        url = f"https://repo1.maven.org/maven2/org/opentripplanner/otp/{version}/{otp_file}"
        urlretrieve(url, f"{otp_path}/{otp_file}")
os.chdir(f"{otp_path}")
os.system(f"Java -Xmx12G -jar {otp_file} --build --serve .")

