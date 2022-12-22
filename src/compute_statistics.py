from job_data import compute_job_flow, compute_job_totals
from transit_time import *
from job_accessibility import compute_job_accessibility
import argparse

parser = argparse.ArgumentParser(description='Compute Commmute Statistics for Downstram Analysis')
parser.add_argument('--year', type=int, default = 2019, help='year of lodes data')
parser.add_argument('--seg',type=str, default = 'S000', help='Segment of the workforce; S000: Total number of jobs, SE01: Number of jobs with earnings $1250/month or less')
parser.add_argument('--recompute_current_transit_time', action=argparse.BooleanOptionalAction)
parser.add_argument('--resimulate_red_line', action=argparse.BooleanOptionalAction)
args = parser.parse_args()

seg = args.seg
year = args.year
speed = args.speed
period = 8
recompute_current_transit_time = parser.recompute_current_transit_time
resimulate_red_line = parser.resimulate_red_line

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
    get_all_pair_transit_time(f"gtfs_red_line_speed_{speed}_period_{period}.csv", job_flow,
        tract_file = "2020_Gaz_tracts_24.txt", date = '11/01/2022', time = '08:00AM')


transit_time = compute_transit_time("gtfs_current.csv", f"gtfs_red_line_speed_{speed}_period_{period}.csv", 
    speed = speed, period = period)
compute_job_accessibility(transit_time, job_totals, seg, speed)