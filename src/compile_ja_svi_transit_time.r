suppressPackageStartupMessages(library(tidyverse))

load_job_accessibility <- function(dir_processed, dir_raw) {
  # Read through all job accessibility files
  dir_ja <- str_glue("{dir_processed}/job_accessibility")
  df <- tibble(segment = dir(dir_ja))  # Get job segments
  df <- df %>%
    mutate(speed = map(segment, 
                        function(seg) str_glue("{dir_ja}/{seg}")) %>%
             map(dir)) %>% 
    unnest(cols = c(speed)) %>% 
    mutate(speed = as.integer(speed))
  df <- df %>%
    mutate(mode = map2(segment, speed,
                        function(seg, speed)
                          str_glue("{dir_ja}/{seg}/{speed}")) %>%
             map(dir)) %>% 
  unnest(cols = c(mode))
  df <- df %>%
    mutate(threshold = pmap(list(segment, speed, mode),
                             function(seg, speed, mode)
                               str_glue("{dir_ja}/{seg}/{speed}/{mode}")) %>%
             map(dir)) %>%  
    unnest(cols = c(threshold)) %>% 
    mutate(threshold = str_remove_all(threshold, ".csv") %>% as.integer())
  
  # Actually load the job accessibility files
  load_ja <- function(dir_ja, segment, speed, mode, threshold) {
    # This will load a list of job accessibilities from the directory specified
    # by arguments
    read_csv(str_glue("{dir_ja}/{segment}/{speed}/{mode}/{threshold}.csv"), 
             show_col_types = FALSE) %>%
      transmute(FIPS = tract_id, gravity_sum = gravity)
  }
  df <- df %>% 
    mutate(data = pmap(list(segment, speed, mode, threshold),
                       ~ load_ja(dir_ja, ..1, ..2, ..3, ..4))) %>% 
    unnest(cols = c(data)) %>% 
    mutate(mode = factor(mode, levels = c("transit_current", "red_line"), 
                         labels = c("transit", "red_line")))
  # Compute difference and percent difference
  df <- df %>%
    pivot_wider(names_from = mode, values_from = gravity_sum) %>%
    mutate(difference = red_line - transit,
           pct_difference = difference / transit) %>%
    pivot_longer(c("transit", "red_line", "difference", "pct_difference"),
               names_to = "mode", values_to = "gravity_sum") %>% 
    mutate(mode = factor(mode, levels = c("transit",
                                          "red_line",
                                          "difference",
                                          "pct_difference")))
}

tag_service_area <- function(df, dir_raw) {
  # Tag FIPS in df with boolean for red line service area
  service_area <- readLines(str_glue("{dir_raw}/service_area.csv"))
  df <- df %>% mutate(service_area = FIPS %in% service_area)
}

load_svi <- function(dir_processed, svi_file) {
  # Load SVI socioeconomic summary data and compute a statistic stating whether
  # a tract is below the mean
  df <- read_csv(str_glue("{dir_processed}/{svi_file}"), 
                  col_types = cols_only(FIPS = "d", 
                                        svi_socioecon_summary = "d")) %>% 
    mutate(disadvantaged = svi_socioecon_summary < 0,
           svi_pct_rank = rank(svi_socioecon_summary) /
             length(svi_socioecon_summary))
}

average_commute_time <- function(segment, speed, dir_processed, weight = TRUE) {
  # Load the time it takes to commute from each census tract to each other
  # census tract using transit and the red line. Then, if weight is TRUE, use 
  # job flow data to compute a weighted average commute time for each tract.
  # Otherwise, just average over all tracts.
  df <- read_csv(
    str_glue("{dir_processed}/transit_time_data_speed_{speed}_period_8.csv"),
    show_col_types = FALSE)
  job_flows <- read_csv(
    str_glue("{dir_processed}/job_flow_tract_{segment}.csv"), 
    show_col_types = FALSE)
  # Join the job flows
  df <- df %>%
    left_join(job_flows, 
              by = c("origin" = "h_geocode", 
                     "dest" = "w_geocode")) %>% 
    mutate(job_totals = replace_na(job_totals, 0))
  
  # Compute (weighted) average commute time
  df <- df %>% 
    group_by(origin) %>% 
    mutate(
      flow_proportion = job_totals / sum(job_totals))
  if (weight) {
    df <- df %>% 
      summarize(
        transit = sum(transit_time_current * flow_proportion),
        red_line = sum(transit_time_with_red_line * flow_proportion))
  } else {
    df <- df %>% 
      summarize(
        transit = mean(transit_time_current),
        red_line = mean(transit_time_with_red_line)
      )
  }
  df <- df %>% 
    mutate(difference = red_line - transit,
           pct_difference = difference / transit) %>% 
    pivot_longer(c("transit", "red_line", "difference", "pct_difference"),
                 names_to = "mode", 
                 values_to = "average_commute_time") %>%
    transmute(origin, mode = factor(mode, levels = c("transit",
                                                     "red_line",
                                                     "difference",
                                                     "pct_difference")),
              average_commute_time)
}

load_all_data <- function(dir_processed, dir_raw, weight = TRUE) {
  # weight determines whether average commute times are weighted by job flow
  df <- load_job_accessibility(dir_processed, dir_raw)
  df <- df %>%
    group_by(segment) %>%
    summarize(speed = unique(speed), .groups = "drop") %>% 
    mutate(average_commute_time = 
             map2(segment, speed, 
                  ~average_commute_time(..1, ..2, dir_processed, weight))) %>% 
    unnest(cols = average_commute_time) %>% 
    rename(FIPS = origin) %>% 
    left_join(df, by = c("FIPS", "segment", "speed", "mode"))
  df <- load_svi(dir_processed,
                 "SVI_EP_2020_Standard_Scaled_Summary_Index.csv") %>% 
    inner_join(df, by = "FIPS")
  df <- df %>% tag_service_area(dir_raw)
}

