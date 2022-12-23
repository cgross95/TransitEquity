from job_data import compute_job_flow, compute_job_totals
from transit_time import *
from job_accessibility import compute_job_accessibility
import preprocess_svi_ep
from svi_summary_index import compute_svi_summaries
from map_outliers import map_outliers
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Compute Commmute Statistics for Downstram Analysis')
parser.add_argument('--year', type=int, default = 2019, help='year of lodes data')
parser.add_argument('--seg', type=str, default = 'S000', help='Segment of the workforce; S000: Total number of jobs, SE01: Number of jobs with earnings $1250/month or less')
parser.add_argument('--recompute_current_transit_time', action=argparse.BooleanOptionalAction)
parser.add_argument('--resimulate_red_line', action=argparse.BooleanOptionalAction)
parser.add_argument('--speed', type=float, default = 20, help='Speed of the Assumed Red Line; default is 20 mph')
parser.add_argument('--period', type=float, default = 8, help='Service frequency; Default is 8 minutes')
parser.add_argument('--svi2020', action='store_true', help='Use 2020 census data (otherwise 2018)')
parser.add_argument('--thresh_min', type=int, default=15, help='Lowest commute threshold to consider')
parser.add_argument('--thresh_max', type=int, default=90, help='Largest commute threshold to consider')
parser.add_argument('--thresh_step', type=int, default=15, help='Step between commute thresholds')
args = parser.parse_args()

seg = args.seg
year = args.year
speed = args.speed
period = args.period
recompute_current_transit_time = args.recompute_current_transit_time
resimulate_red_line = args.resimulate_red_line
min_thresh = args.thresh_min
max_thresh = args.thresh_max
thresh_step = args.thresh_step

job_totals = compute_job_totals(seg = seg, year = year)
job_flow = compute_job_flow(seg = seg, year = year)

if recompute_current_transit_time == True:
    # If this is set true, run 'python activate_otp.py --otp_path otp_current' in another terminal window
    # And wait till "Grizzly server running." shows up 
    get_all_pair_transit_time("gtfs_current.csv", job_flow, tract_file = "2020_Gaz_tracts_24.txt", 
        date = '11/01/2022', time = '08:00AM')

if resimulate_red_line == True:
    # If this is set true, run 'python activate_otp.py --otp_path otp_red_line --red_line --speed {speed} --period {period}' in another terminal window
    # And wait till "Grizzly server running." shows up 
    get_all_pair_transit_time(f"gtfs_red_line_speed_{int(speed)}_period_{int(period)}.csv", job_flow,
        tract_file = "2020_Gaz_tracts_24.txt", date = '11/01/2022', time = '08:00AM')


transit_time = compute_transit_time("gtfs_current.csv", f"gtfs_red_line_speed_{int(speed)}_period_{int(period)}.csv", 
    speed = speed, period = period)
compute_job_accessibility(transit_time, job_totals, seg, speed, min_thresh=min_thresh, max_thresh=max_thresh, thresh_step=thresh_step)

svi2020 = args.svi2020
preprocess_svi_ep.preprocessing(svi2020)
compute_svi_summaries(svi2020)
subprocess.call("./compute_outliers.r")
map_outliers(seg, speed, min_thresh, max_thresh, thresh_step)
