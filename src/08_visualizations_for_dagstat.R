library(tidyverse)

evaluation_llm_performance_per_document <- read.csv("C:/Users/LENOVO/Desktop/DSSGx/land_sealing_post_dssg/bavaria-building-plans-digitalization/data/final/tables/annotations/evaluation_llm_performance_per_document.csv")

labels <- c("eg_fok_unit" = "EG FOK Unit", "eg_fok_value" = "EG FOK Value", 
            "fok_unit" = "FOK Unit", "fok_value" = "FOK Value",
            "gok_unit" = "GOK Unit", "gok_value"= "GOK Value",
            "gfz_value"  = "GFZ", "grz_value" = "GRZ", 
            "grundwasser_value" = "Grundwasser","hw10_value" = "HW10",
            "hw100_value" = "HW100")  

p1 <- evaluation_llm_performance_per_document %>%
  ggplot(aes(x = metric, y = count, fill = correct_result)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = ifelse(count == 0, "", count)), 
            position = position_stack(vjust = 0.5), 
            size = 3, color = "white") +  # Hide labels for 0 values
  scale_x_discrete(labels = labels) +
  coord_flip() +
  scale_y_discrete(labels = labels) + 
  labs(title = "",
       y = "N of Documents",
       x = "",
       fill = "Extraction evaluation")  +
  theme(legend.position = "bottom") +  # Move legend to bottom
  guides(fill = guide_legend(nrow = 2))  # Arrange legend in one row

file_path <- "C:/Users/LENOVO/Desktop/DSSGx/land_sealing_post_dssg/bavaria-building-plans-digitalization/img/evaluation_llm_performance_per_document.png"
ggsave(file_path, p1, width = 12, height = 6, dpi = 300)  


evaluation_llm_performance_per_row <- read.csv("C:/Users/LENOVO/Desktop/DSSGx/land_sealing_post_dssg/bavaria-building-plans-digitalization/data/final/tables/annotations/evaluation_results_per_row.csv")

ggplot(evaluation_llm_performance_per_row, aes(x = metric, y = count, fill = correct_result)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = ifelse(count == 0, "", count)), 
            position = position_stack(vjust = 0.5), 
            size = 3, color = "white") +  # Hide labels for 0 values  scale_x_discrete(labels = labels) +  
  scale_y_continuous(labels = scales::percent_format()) +  # Show percentages
  coord_flip() +  # Flip axes for better readability
  labs(title = "Performance of extraction",
       y = "Proportion",
       x = "",
       fill = "Extraction evaluation") +
  theme_minimal()
