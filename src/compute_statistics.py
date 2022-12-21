from job_data import compute_job_flow, compute_job_totals
from transit_time import compute_transit_time
from job_accessibility import compute_job_accessibility

import argparse

parser = argparse.ArgumentParser(description='Compute Commmute Statistics for Downstram Analysis')
parser.add_argument('--year', type=int, default = 2019, help='year of lodes data')
parser.add_argument('--seg',type=str, default = 'S000', help='Segment of the workforce; S000: Total number of jobs, SE01: Number of jobs with earnings $1250/month or less')
parser.add_argument('--speed',type=float, default = 20, help='Assumed Red Line Speed')
args = parser.parse_args()

seg = args.seg
year = args.year
speed = args.speed
job_totals = compute_job_totals(seg = seg, year = year)
compute_job_flow(seg = seg, year = year)
travel_time = compute_transit_time(assumed_train_speed = speed)
compute_job_accessibility(travel_time, job_totals, seg, speed)