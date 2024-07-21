import gradio as gr
import pandas as pd
import numpy as np
import os


def load_excel_files(file_objects):
    dfs = []
    for file in file_objects:
        df = pd.read_excel(file.name)
        df['Sheet Name'] = os.path.basename(file.name)
        dfs.append(df[['Description', 'Price', 'Sheet Name']])
    combined_df = pd.concat(dfs, ignore_index=True)
    total_price = combined_df['Price'].sum()
    return combined_df, combined_df, f"Total Price: ${total_price:.2f}"


def search_data(dataframe, search_term):
    if dataframe is None or dataframe.empty:
        return pd.DataFrame(), "Please upload Excel files first."
    
    filtered_df = dataframe[dataframe['Description'].str.contains(search_term, case=False, na=False)]
    total = filtered_df['Price'].sum()
    
    summary = f"Total: ${total:.2f}"
    
    return filtered_df, summary
    

def add_label(dataframe, search_results, label):
    if dataframe is None or dataframe.empty or search_results is None or search_results.empty:
        return dataframe, "No data to label."
    
    # Update the label for matching rows
    for _, row in search_results.iterrows():
        mask = (dataframe['Description'] == row['Description']) & \
               (dataframe['Price'] == row['Price']) & \
               (dataframe['Sheet Name'] == row['Sheet Name'])
        dataframe.loc[mask, 'Label'] = label
    
    return dataframe, f"Added label '{label}' to {len(search_results)} items."


def create_summary(dataframe):
    if dataframe is None or dataframe.empty:
        return "No data available."
    
    summary = ""
    for label in dataframe['Label'].unique():
        if label:  # Skip empty labels
            label_data = dataframe[dataframe['Label'] == label]
            summary += f"\n\nLabel: {label}\n"
            summary += label_data[['Description', 'Price', 'Sheet Name']].to_string(index=False)
            summary += f"\nTotal for {label}: ${label_data['Price'].sum():.2f}\n"
    
    return summary


def gradio_app():
    with gr.Blocks() as app:
        gr.Markdown("# Excel Search App")
        
        dataframe = gr.State(None)
        
        with gr.Row():
            file_input = gr.File(
                file_count="multiple", 
                label="Upload Excel Files",
                value=[
                    './dummy_data/expenses_feb.xlsx',
                    './dummy_data/expenses_jan.xlsx',
                    './dummy_data/expenses_mar.xlsx',
                ]
            )

        with gr.Tab("Search using keywords"):
            search_input = gr.Textbox(label="Search Term")
            result_table = gr.DataFrame(
                label="Search Results", 
                interactive=False
            )
            total_output = gr.Textbox(label="Total")
            label_dropdown = gr.Dropdown(
                choices=[
                    'grocery', 
                    'subscriptions', 
                    'transportation', 
                    'outing'
                ], 
                label="Select Label"
            )
            add_button = gr.Button("Add Label")
            label_status = gr.Textbox(label="Labeling Status")
        
        with gr.Tab("Summary"):
            summary_output = gr.Textbox(label="Summary", lines=20)

        file_input.change(
            load_excel_files,
            inputs=[
                file_input
            ],
            outputs=[
                dataframe, 
                result_table,
                total_output
            ]
        )
        
        search_input.change(
            search_data,
            inputs=[
                dataframe, 
                search_input
            ],
            outputs=[
                result_table, 
                total_output
            ]
        )

        add_button.click(
            add_label,
            inputs=[dataframe, result_table, label_dropdown],
            outputs=[dataframe, label_status]
        ).then(
            create_summary,
            inputs=[dataframe],
            outputs=[summary_output]
        )
    
    return app

iface = gradio_app()
iface.launch(server_port=7860, debug=True)