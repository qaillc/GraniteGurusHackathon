import streamlit as st
import os
import numpy as np
import matplotlib.pyplot as plt
from ibm_watsonx_ai.foundation_models import Model
from matplotlib.colors import ListedColormap

st.set_page_config(page_title="Granite Gurus Many Eyes", layout="wide")

# Set up the tabs
tab1, tab2, tab3 = st.tabs(["Project Intro", "Granite Search", "Notes"])

# Tab 1: Project Intro
with tab1:
    st.header("Project Introduction")
    st.write("""
    Welcome to the Granite Gurus Many Eyes Hackathon project. 
    This project is an extension of the previous Hackathons: Build Your AI Startup, Codestral, and Edge Runners.
    
    In this project, we focus on introducing two powerful principles: 
    1. **Uniqueness**
    2. **Many Eyes**

    These principles are demonstrated through a search engine that sits on top of IBM Granite.
    """)

    
    # Embed a YouTube video
    video_url = "https://www.youtube.com/watch?v=Zk1V_V9GoHQ"
    st.video(video_url)

# Tab 2: Granite Search
with tab2:
    


    # Function to get credentials from user input
    def get_credentials():
        url = "https://us-south.ml.cloud.ibm.com"
        apikey = os.getenv("IBM_TOKEN")
        if apikey:
            return {"url": url, "apikey": apikey}
        return None
    
    # Function to modify the generated number according to the rules
    def modify_number(number):
        modified_number = ''
        for digit in number:
            if digit not in '01':  # Change any digit that is not 0 or 1 to 1
                modified_number += '1'
            else:
                modified_number += digit
        return modified_number
    
    # Function to create the grid based on the boolean string
    def create_grid(boolean_string):
        if len(boolean_string) != 16:
            st.error("The generated string is not 16 digits long.")
            return None
        
        # Convert string to a list of integers
        grid = np.array([int(bit) for bit in boolean_string]).reshape(4, 4)
        
        # Create a colormap for the grid
        cmap = ListedColormap(['white', 'black'])
        
        # Plot the grid
        fig, ax = plt.subplots(figsize=(2, 2))  # Shrink the graph size
        ax.matshow(grid, cmap=cmap)
        
        # Add grid lines and remove ticks
        ax.set_xticks(np.arange(-0.5, 4, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 4, 1), minor=True)
        ax.grid(which='minor', color='gray', linestyle='-', linewidth=2)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        
        return fig

    # Function to interpolate between start and end values
    def interpolate_value(start_value, end_value, position, max_position):
        difference = end_value - start_value
        interpolated_value = start_value + (difference * (position / max_position))
        interpolated_value_int = int(interpolated_value)
        binary_representation = bin(interpolated_value_int)[2:].zfill(16)
        
        return binary_representation
    
    # Streamlit app
    def main():
        st.title("Granite Star Search with IBM")
        
        # Get credentials from the user
        credentials = get_credentials()
        if not credentials:
            st.error("Please enter your API key.")
            return
        
        # Model and parameters
        model_id = "ibm/granite-13b-chat-v2"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1.05
        }
        project_id = os.getenv("PROJECT_ID")
        
        # Initialize the model
        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=credentials,
            project_id=project_id
        )
        
        # Sliders for selecting the start value and positionx
        start_value = st.slider("Start Value", 0, 65535, 32768)
        max_slider_value = 256
        position = st.slider("Radial Out", 0, max_slider_value, 0)
        
        # Define the distinct end values for each of the four numbers
        end_values = [0, 65280, 65534, 255]
    
        # Interpolate each value based on the slider position
        interpolated_values = [
            interpolate_value(start_value, end_values[0], position, max_slider_value),  # Number 1
            interpolate_value(start_value, end_values[1], position, max_slider_value),  # Number 2
            interpolate_value(start_value, end_values[2], position, max_slider_value),  # Number 3
            interpolate_value(start_value, end_values[3], position, max_slider_value)   # Number 4
        ]
        
        # Display the interpolated boolean strings horizontally
        st.write("Interpolated Boolean Strings:")
        cols = st.columns(len(interpolated_values))  # Create a column for each boolean string
    
        for i, boolean_string in enumerate(interpolated_values):
            with cols[i]:  # Place each boolean string in its respective column
                st.write(f"Number {i+1}: {boolean_string}")
        
        # Manual input for the 5th grid
        manual_input = st.text_input("Enter a 16-digit boolean number (e.g., 1010101010101010):", "0000000000000000")
        
        # Validate and modify the input if necessary
        manual_input = modify_number(manual_input)
        
        # Display the grids in a row, including the manual input
        cols = st.columns(5)  # Change the number of columns to 5
        for i, boolean_string in enumerate(interpolated_values):
            with cols[i]:
                st.write(f"Grid Number {i+1}:")
                fig = create_grid(boolean_string)
                if fig:
                    st.pyplot(fig)
    
        # Add the 5th grid for the manual input
        with cols[4]:  # Use the 5th column for the manual input grid
            st.write("Predicted Pattern:")
            if len(manual_input) != 16:
                st.error("The input is not 16 digits long.")
            else:
                fig = create_grid(manual_input)
                if fig:
                    st.pyplot(fig)
        
        # Prepare the prompt for the model
        prompt_input = """
        Analyze the four 16 digit boolean numbers, identify the underlying pattern in the sequence, and use this underlying pattern to predict the next 16 digit boolean number. Return only the predicted boolean number 16 digits long. If it is not 15 digit add leadding zeros to make it 16 digits.
        """
        formatted_question = " ".join(interpolated_values)
        prompt = f"{prompt_input}\n{formatted_question}"
        
        if st.button("Predict Next Pattern"):
            generated_response = model.generate_text(prompt=prompt, guardrails=False)
            st.write(f"**Predicted Next Boolean Number:** {generated_response}")

    if __name__ == "__main__":
        main()


# Tab 3: Notes
with tab3:
    st.header("Notes")
    st.write("Seting up your IBM Account.")
    mynotes = """
    Steps to get the API Key
1. Go to the main website. https://cloud.ibm.com/
2. Then click on “manage” on the top bar. In the drop down menu click “Access(IAM)”. It will take you to this link: https://cloud.ibm.com/iam
3. Now, In the left side bar click on “API Keys”. It will take you to this link: https://cloud.ibm.com/iam/apikeys
4. Then just create a key. You can also download the key value.

In the code we also need Project_ID. I have set it up as hugging face secrets. here are the steps too create a project and get its ID.  Steps to get the project ID:
1. Go this link: https://dataplatform.cloud.ibm.com/wx/home?context=wx
2. Go to the end of the page to the “Projects section” and click on “+”. Enter any name for the project. 
3. Then open the project. You will see a tab “Manage”. Click on it and you will see the project ID. You can refer to the attached screenshot to get an idea too.
4. Also for testing prompt lab you have to associate a Watson instance with it. Just click on “Services & integrations” then click on “Associate” service and select “Watsonx Challenge-XML”. 
    
    
    """
    st.write(mynotes)
    