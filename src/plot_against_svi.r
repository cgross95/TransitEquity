#! /usr/bin/Rscript

library("argparse")
source("./compile_ja_svi_transit_time.r")

svi_facet_formula <- function(segment, threshold, speed, mode) {
  left <-  ""
  right <-  ""
  # segment + speed + mode ~ threshold
  if(segment) {
    left <- str_glue("{left} + segment")
  } 
  if(speed) {
    left <- str_glue("{left} + speed")
  } 
  if(mode) {
    left <- str_glue("{left} + mode")
  }
  if(threshold) {
    right <- str_glue("{right} + threshold")
  }
  begins_with_plus = "\\s\\+\\s"
  if(left == "") {
    left <-  "."
  } else if(str_starts(left, begins_with_plus)) {
    left <- str_replace(left, begins_with_plus, "")
  }
  if(right =="") {
    right <- "."
  } else if(str_starts(right, begins_with_plus)) {
    right <- str_replace(right, begins_with_plus, "")
  }
  as.formula(str_glue("{left} ~ {right}"))
}

svi_title <- function(seg, threshold, speed, mode) {
  title = ""
  if (length(seg) == 1) {
    title <- str_glue("{title} Segment: {seg}")
  }
  if (length(threshold) == 1) {
    title <- str_glue("{title} Threshold: {threshold}")
  }
  if (length(speed) == 1) {
    title <- str_glue("{title} Speed: {speed}")
  }
  if (length(mode) == 1) {
    title <- str_glue("{title} Mode: {mode}")
  }
  title
}

vs_svi_fname <- function(df, var, seg_choice,
                         threshold_choice,
                         speed_choice,
                         mode_choice,
                         histogram = FALSE) {
  seg_str <- seg_choice %>% as.character() %>% str_flatten(collapse = "_")
  threshold_str <- threshold_choice %>% as.character() %>%
    str_flatten(collapse = "_")
  speed_str <- speed_choice %>% as.character() %>% str_flatten(collapse = "_")
  mode_str <- mode_choice %>% as.character() %>% str_flatten(collapse = "_")
  dir <- str_glue("../results/vs_svi/{seg_str}/{speed_str}/{threshold_str}/{mode_str}")
  dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  var_name <- df %>% select({{ var }}) %>% colnames()
  if (histogram) {
    fname <- str_glue("{dir}/{var_name}_hist.png")
  } else {
    fname <- str_glue("{dir}/{var_name}.png")
  }
}

vs_svi <- function(df,
                   var,
                   ...,
                   seg_choice = unique(df$segment),
                   threshold_choice = unique(df$threshold),
                   speed_choice = unique(df$speed),
                   mode_choice = c("transit", "red_line")) {
  # var is either gravity_sum or average_commute_time
  # all additional arguments are filters for df
  filtered_df <- df %>%
    filter(
      segment %in% seg_choice,
      threshold %in% threshold_choice,
      speed %in% speed_choice,
      mode %in% mode_choice,
      ...)
  svi_facet_formula <- svi_facet_formula(length(seg_choice) > 1,
                                         length(threshold_choice) > 1,
                                         length(speed_choice) > 1,
                                         length(mode_choice) > 1)
  svi_title <- svi_title(seg_choice,
                         threshold_choice,
                         speed_choice,
                         mode_choice,
                         ...)
  ggplot(data = filtered_df, mapping = aes(svi_socioecon_summary, {{ var }})) +
    geom_point(alpha = 0.4) +
    geom_smooth(method = "lm", formula = "y ~ x") +
    facet_grid(svi_facet_formula) +
    labs(title = svi_title)
  fname <- vs_svi_fname(df, {{ var }}, seg_choice, threshold_choice,
                        speed_choice, mode_choice)
  ggsave(fname, width = 10, height = 10)
}

var_histogram <- function(df,
                   var,
                   ...,
                   seg_choice = unique(df$segment),
                   threshold_choice = unique(df$threshold),
                   speed_choice = unique(df$speed),
                   mode_choice = c("transit", "red_line")) {
  # var is either gravity_sum or average_commute_time
  # all additional arguments are filters for df
  filtered_df <- df %>%
    filter(
      segment %in% seg_choice,
      threshold %in% threshold_choice,
      speed %in% speed_choice,
      mode %in% mode_choice,
      ...)
  svi_facet_formula <- svi_facet_formula(length(seg_choice) > 1,
                                         length(threshold_choice) > 1,
                                         length(speed_choice) > 1,
                                         length(mode_choice) > 1)
  svi_title <- svi_title(seg_choice,
                         threshold_choice,
                         speed_choice,
                         mode_choice,
                         ...)
  ggplot(data = filtered_df, mapping = aes({{ var }})) +
    geom_histogram() +
    facet_grid(svi_facet_formula) +
    labs(title = svi_title)
  fname <- vs_svi_fname(df, {{ var }}, seg_choice, threshold_choice,
                        speed_choice, mode_choice, histogram = TRUE)
  ggsave(fname, width = 10, height = 10)
}

parser <- ArgumentParser(description="Plot job accessibility and average commute times versus SVI summary")
parser$add_argument('--thresh_min', type="integer", default=15,
                    help='Lowest commute threshold to consider')
parser$add_argument('--thresh_max', type="integer", default=90,
                    help='Largest commute threshold to consider')
parser$add_argument('--thresh_step', type="integer", default=15,
                    help='Step between commute thresholds')
parser$add_argument('--service_area', action='store_true',
                    help='Restrict computations to origin and destination tracts that are in the service area')
args <- parser$parse_args()

thresh <- seq(args$thresh_min, args$thresh_max, args$thresh_step)

if (args$service_area) {
  df <- load_service_to_service_data("../processed_data/", "../raw_data/")
} else {
  df <- load_all_data("../processed_data/", "../raw_data/")
}

pwalk(df %>% select(segment) %>% unique(),
      ~vs_svi(df, gravity_sum, seg_choice = ..1, threshold_choice = thresh))

pwalk(df %>% select(segment) %>% unique(),
      ~vs_svi(df, gravity_sum, seg_choice = ..1, threshold_choice = thresh,
              mode_choice = "pct_difference"))

pwalk(df %>% select(segment) %>% unique(),
      ~var_histogram(df, gravity_sum, seg_choice = ..1, threshold_choice = thresh))

pwalk(df %>% select(segment) %>% unique(),
      ~var_histogram(df, gravity_sum, seg_choice = ..1, threshold_choice = thresh,
              mode_choice = "pct_difference"))

# Threshold doesn't matter for commute time, we just pick one
pwalk(df %>% select(segment) %>% unique(),
      ~vs_svi(df, average_commute_time, threshold_choice = df$threshold[1],
              seg_choice = ..1))

pwalk(df %>% select(segment) %>% unique(),
      ~vs_svi(df, average_commute_time, threshold_choice = df$threshold[1],
              seg_choice = ..1, mode_choice = "pct_difference"))

pwalk(df %>% select(segment) %>% unique(),
      ~var_histogram(df, average_commute_time, threshold_choice = df$threshold[1],
              seg_choice = ..1))

pwalk(df %>% select(segment) %>% unique(),
  ~var_histogram(df, average_commute_time, threshold_choice = df$threshold[1],
              seg_choice = ..1, mode_choice = "pct_difference"))