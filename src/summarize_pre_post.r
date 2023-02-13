#! /usr/bin/Rscript

library("argparse")
source("./compile_ja_svi_transit_time.r")

parser <- ArgumentParser(description="Summarize data")
parser$add_argument('--service_area', action='store_true',
                    help='Restrict computations to origin and destination tracts that are in the service area')
parser$add_argument('--speed', type="integer", default=20,
                    help='Red line speed to summarize')
parser$add_argument('--threshold', type="integer", default=30,
                    help='Commute threshold to use')
args <- parser$parse_args()

if (args$service_area) {
  df <- load_service_to_service_data("../processed_data/", "../raw_data/")
} else {
  df <- load_all_data("../processed_data/", "../raw_data/")
}

df_summary <- df %>%
  pivot_wider(names_from = mode, values_from = c("gravity_sum", "average_commute_time")) %>%
  filter(segment == "S000",
         speed == args$speed,
         threshold == args$threshold) %>%
  summarize(mean_ja = mean(gravity_sum_difference),
            mean_pct_ja = mean(gravity_sum_pct_difference),
            total_ja = sum(gravity_sum_difference),
            mean_commute = mean(average_commute_time_difference),
            mean_pct_commute = mean(average_commute_time_pct_difference),
            count = n())

print(df_summary)