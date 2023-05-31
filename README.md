# YouTube-Data-Harvesting-using-API
YouTube Data Scraper is a Python application that uses the YouTube Data API to retrieve channel, video, and playlist information. Utilise SQLite and MongoDB to store data. Ideal for researchers, marketers, and data analysts.

# Introduction
Using the YouTube Data API, the YouTube Data Scraper is a Python programme that enables you to retrieve data from YouTube channels, videos, and playlists. With this programme, you can quickly and conveniently execute numerous data analysis activities while collecting useful data from YouTube. The YouTube Data Scraper has you covered if you need to retrieve channel information, fetch video details, analyse comments, or generate reports.

## OverView
You may extract and analyse data from YouTube with the help of a number of capabilities provided by the YouTube Data Scraper. Among the essential characteristics are: 

`Channel Information Retrieval:`
Obtain detailed information about a specific YouTube channel using its channel ID. The scraper retrieves essential details such as the channel name, subscriber count, view count, description, country, video count, playlist ID, channel type, and channel status. These insights facilitate analyzing a channel's popularity and engagement.

`Video Information Extraction:` Retrieve comprehensive details about a specific video, including the video title, description, tags, published date, view count, like count, favorite count, comment count, and thumbnails. This information aids in analyzing video performance, identifying trends, and understanding audience engagement.

`Playlist Information Fetching:` Access playlist information such as the playlist title, description, published date, and item count. This feature proves particularly useful for analyzing playlists and their contents.

`Comment Retrieval:`Gather comments for a specific video, enabling user feedback analysis, sentiment analysis, and deeper audience insights.

`Bulk Data Retrieval for Channels and Videos:`In addition to fetching data for individual channels and videos, the YouTube Data Scraper supports bulk data retrieval. By specifying multiple YouTube channel IDs or video IDs (separated by commas), you can fetch information for multiple channels or videos simultaneously. This feature proves extremely valuable when working with large datasets and conducting comparative analyses.

`Data Analysis and Reports:`The YouTube Data Scraper offers various data analysis capabilities to make sense of the fetched data. Utilizing the Plotly library, it generates interactive and dynamic charts, enabling the creation of insightful visualizations and reports based on the retrieved information. This feature facilitates exploring the data and drawing meaningful conclusions.

## Requirememt python package to run code
To install the required packages for your code. Open `requirements.txt` file and list the package names along with their versions. 
```
pip install -r requirements.txt
```
Make sure you run this command in your Python environment to install the necessary packages for your code to run successfully.
` Code Summary`

This repository contains a Python script that performs various tasks using different libraries and modules. The script's functionality is summarized as follows:

### 1. Importing Modules

The script begins by importing the necessary modules, including:
- `pymongo`: for establishing a connection to a MongoDB database.
- `streamlit`: for creating a Streamlit application.
- `googleapiclient`: for interacting with Google APIs.
- `datetime`: for working with date and time data.
- `pandas`: for data manipulation in tabular format.
- `json`: for working with JSON data.
- `re`: for performing regular expression operations.
- `sqlite3`: for working with SQLite databases.
- `sqlalchemy`: for creating a database engine.
- `plotly.graph_objects`: for creating interactive plots.
- `streamlit_scrollable_textbox`: for adding a scrollable textbox widget to the Streamlit application.

### 2. Connection to MongoDB

The script establishes a connection to a MongoDB database using the `MongoClient` class from the `pymongo` module.

### 3. Streamlit Application

The `streamlit` module is used to create a Streamlit application. Streamlit is a framework for building interactive web applications for data science and machine learning.

### 4. Google API Integration

The `googleapiclient` module is used to interact with Google APIs. The `build` function is used to create a service object for a specific API, and the `HttpError` class is imported to handle any HTTP errors that may occur during API requests.

### 5. Date and Time Handling

The `datetime` module is imported to work with date and time data.

### 6. Data Manipulation

The `pandas` module is imported to work with data in tabular format. It provides high-performance data structures and data analysis tools. The `json` module is used for working with JSON data. The `re` module is used for performing regular expression operations.

### 7. SQLite Database

The `sqlite3` module is imported to work with SQLite databases. SQLite is a lightweight and self-contained database engine. The `create_engine` function from the `sqlalchemy` module is used to create a database engine.

### 8. Plotly Visualization

The `plotly.graph_objects` module is imported to create interactive and customizable plots using the Plotly library.

### 9. Scrollable Textbox

The `streamlit_scrollable_textbox` module is imported to add a scrollable textbox widget to the Streamlit application.

Please note that the code provided is a combination of various functionalities, and the full implementation or context is not available. Refer to the actual code files for more details.



## Obtain YouTube API login information: 

> Go to the 'Google Cloud Console'. 

> Choose an existing project or start a new one. 

> For your project, enable the "YouTube Data API v3." 

> Create YouTube API v3 credentials. 

### Run the application: 
```
streamlit run YoutubeAPI.py 
```
## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
The project development was made possible with the assistance and support of various websites and friends. Their contributions in the form of insights, guidance, and resources greatly enhanced the project.

## Contact
For any inquiries or suggestions regarding this project, please contact Mouli Raja at [baimouli@gmail.com].


## Conclusion 

Data from YouTube channels, videos, and playlists may be easily fetched and analysed with the YouTube Data Scraper. You may learn more about the performance of your channel, the engagement of your videos, and the opinions of your audience thanks to its many features and data analytic capabilities. Regardless of whether you work as a data analyst, researcher, or marketer, the YouTube Data Scraper may assist you in gathering insightful data that will guide your decision-making. 
