library(tidyverse)
library(openxlsx)

llm_extracted_data <- read_csv('data/proc/building_plans_sample/features/test_images_info_data_extraction.csv')
template_data <- read.xlsx('data/final/bplan_samples/annotation/annotation_template.xlsx', sheet = 'Hoja 1')
template_path <- 'data/final/bplan_samples/annotation/annotation_template.xlsx'

llm_extracted_data <- llm_extracted_data %>% 
    select(-contains('llm')) %>%
    group_by(id, filename) %>%
    pivot_longer(cols = -c(id, filename), names_to = 'met', values_to = 'value') 

wb <- loadWorkbook(template_path)

writeData(wb, sheet = "Hoja 1",
        x = llm_extracted_data,
        startCol = 1, startRow = 1,
        colNames = TRUE, rowNames = FALSE)
            
folder_path <- paste0("data/final/bplan_samples/annotation/filled_company_templates/")
      
if (!dir.exists(folder_path)) {
    dir.create(folder_path, recursive = TRUE)
    }


      # Save the workbook with updates
saveWorkbook(wb, file = paste0("data/final/bplan_samples/annotation/filled_company_templates/", "test_filled_annotation",".xlsx"), overwrite = TRUE)


