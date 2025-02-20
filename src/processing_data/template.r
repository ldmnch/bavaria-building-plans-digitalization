library(tidyverse)
library(openxlsx)

prepro_llm_data <- function(llm_extracted_data){
  
  llm_extracted_data <- llm_extracted_data %>%
    select(-contains('llm')) %>%
    group_by(id, filename) %>% 
    mutate(across(where(is.numeric), as.character)) %>% 
    pivot_longer(cols = -c(id, filename), names_to = 'met', values_to = 'value') %>% 
    ungroup()
  
  return(llm_extracted_data)
  
}

sealing_data <- read_csv('data/proc/building_plans_sample/features/info_data_extraction.csv')

floors_data <- read.csv('data/proc/building_plans_sample/features/info_data_extraction_floors.csv',
                                 fileEncoding = "latin1")

flooding_data <- read.csv('data/proc/building_plans_sample/features/info_data_extraction_flooding.csv',
                                 fileEncoding = "latin1")

template_path <- 'data/final/tables/annotation_template.xlsx'
output_path_filename <- "filled_anotation"

sealing_data <- prepro_llm_data(sealing_data)
flooding_data <- prepro_llm_data(flooding_data)
floors_data <- prepro_llm_data(floors_data)

llm_extracted_data <- rbind(sealing_data, flooding_data, floors_data) 
llm_extracted_data <- llm_extracted_data %>% 
  arrange(id, filename) 

#use doc 4781 and 1 
# Split the rows into four subsets. By the column 'id' split into 4 groups: three of 20 and one of 14

# Step 1: Get unique ids and shuffle them

unique_ids <- llm_extracted_data %>% distinct(id) %>% pull(id) %>% sample()

# Step 2: Create a grouping vector
group_labels <- rep(1:3, times = c(20, 20, 21))

# Step 3: Assign groups to ids
id_groups <- tibble(id = unique_ids, group = group_labels)

# Step 4: Merge with original dataframe
llm_extracted_data <- llm_extracted_data %>% left_join(id_groups, by = "id")
llm_extracted_data <- llm_extracted_data %>% mutate(group = case_when(
  id == 1 ~ 4, 
  id == 4781 ~ 4,
  TRUE ~ group
))

llm_extracted_data %>%
  group_by(group) %>%
  summarise(n = n_distinct(id))

for (group_name in unique(llm_extracted_data$group)) {
  
  llm_extracted_data_group <- llm_extracted_data %>% 
    filter(group == group_name)
  
  # Do something with llm_extracted_data_group

  llm_extracted_data_group <- llm_extracted_data_group %>% select(-group)
  
  wb <- loadWorkbook(template_path)
  
  writeData(wb, sheet = "Hoja 1",
            x = llm_extracted_data_group,
            startCol = 1, startRow = 4,
            colNames = TRUE, rowNames = FALSE)
  
  folder_path <- paste0("data/final/bplan_samples/annotation/filled_templates/")
      
  if (!dir.exists(folder_path)) {
    dir.create(folder_path, recursive = TRUE)
    }
  
  # Save the workbook with updates
  saveWorkbook(wb, file = paste0("data/final/bplan_samples/annotation/filled_templates/ann_",group_name, "/", output_path_filename,"_group_", group_name,".xlsx"), overwrite = TRUE)
  

}
