#! /usr/bin/Rscript

library("argparse")
source("./compile_ja_svi_transit_time.r")

save_outlier_tracts <- function(var, segment_choice, speed_choice,
                                threshold_choice,
                                mode_choice = "pct_difference") {
  filtered_df <- df %>%
    filter(
      segment == segment_choice,
      threshold == threshold_choice,
      speed == speed_choice,
      mode %in% c("pct_difference", "difference")) %>% 
    pivot_wider(names_from = mode, values_from = c("average_commute_time", "gravity_sum"))
  dir <- str_glue("../results/outliers/{segment_choice}/{speed_choice}/{threshold_choice}/{mode_choice}")
  dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  filename <- str_glue("{dir}/{var}.csv")
  if (var == "average_commute_time") {
    filtered_df <- filtered_df %>% 
      filter(average_commute_time_pct_difference
             <  boxplot.stats(average_commute_time_pct_difference)$stats[1])
  } else if (var == "gravity_sum") {
    filtered_df <- filtered_df %>% 
      filter(gravity_sum_pct_difference >  boxplot.stats(gravity_sum_pct_difference)$stats[5])
  }
  filtered_df %>%
    select(FIPS, svi_pct_rank, .data[[str_glue("{var}_pct_difference")]],
           .data[[str_glue("{var}_difference")]]) %>%
    unique() %>% 
    write_csv(filename)
}


parser <- ArgumentParser(description="Compute outliers for commute time and job accessibility")
parser$add_argument('--service_area', action='store_true',
                    help='Restrict computations to origin and destination tracts that are in the service area')
args <- parser$parse_args()

if (args$service_area) {
  df <- load_service_to_service_data("../processed_data/", "../raw_data/")
} else {
  df <- load_all_data("../processed_data/", "../raw_data/")
}

pwalk(df %>% select(segment, speed, threshold) %>% unique(),
      ~save_outlier_tracts("gravity_sum", ..1, ..2, ..3))
pwalk(df %>% select(segment, speed, threshold) %>% unique(),
      ~save_outlier_tracts("average_commute_time", ..1, ..2, ..3))
