#! /usr/bin/Rscript

source("./compile_ja_svi_transit_time.r")


df <- load_all_data("../processed_data/", "../raw_data/")

df_summary <- df %>%
  filter(mode %in% c("difference", "pct_difference"), service_area == TRUE) %>%
  group_by(segment, speed, threshold, mode) %>%
  summarize(mean_ja = mean(gravity_sum),
            total_ja = sum(gravity_sum),
            mean_commute = mean(average_commute_time),
            total_commute_time = sum(average_commute_time),
            count = n())

print(df_summary)