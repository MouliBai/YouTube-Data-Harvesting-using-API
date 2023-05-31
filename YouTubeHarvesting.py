from pymongo import MongoClient
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import pandas as pd
import json
import re
import sqlite3
from sqlalchemy import create_engine
import plotly.graph_objects as go
from streamlit_scrollable_textbox import scrollableTextbox as text


st.set_page_config(layout="wide")
st.header("**:red[YouTube]** Data Harvesting and Warehousing")
col1, col2,col3 = st.columns(3)


col1.subheader(':violet[Data collection] from :red[YouTube]')
channel_id = col1.text_input("Channel Id")
col1.write("*To use the API to retrieve data from Youtube and put it all in MongoDB, click this button. ")
Json = col1.button("Get Data and Export to MongoDB")
col1.divider()
if "Json" not in st.session_state:
    st.session_state.Json = False
if Json or st.session_state.Json:
    st.session_state.Json = True

    API_KEY = '[Enter the API Key Here]'
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey = API_KEY)

    col3.warning("Fetching Data")

    def get_channel_data(youtube, channel_id):
        try:
            channel_request = youtube.channels().list(
                part = 'snippet,statistics,contentDetails,topicDetails',
                id = channel_id)
            channel_response = channel_request.execute()
            if 'items' not in channel_response:
                col3.warning(f"Invalid channel id: {channel_id}")
                return None
            return channel_response
        except HttpError as e:
            col3.warning(f"An error occurred: {e}")
            return None
        
    channel = get_channel_data(youtube, channel_id)
    channel_type = channel['items'][0]['topicDetails'].get('topicCategories', [])
    channel_type = channel_type[0].split('/')[-1]

    channel_name = channel['items'][0]['snippet']['title']
    channel_subscriber_count =  channel['items'][0]['statistics']['subscriberCount']
    channel_view_count = channel['items'][0]['statistics']['viewCount']
    channel_description = channel['items'][0]['snippet']['description']
    channel_country = channel['items'][0]['snippet'].get('country', 'N/A')
    channel_video_count = channel['items'][0]['statistics']['videoCount']
    channel_playlist_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    #channel_type = channel_type
    
    channel_data = {
        'channel_details':{
            'channel_name': channel_name,
            'channel_id': channel_id,
            'channel_subscriber_count': channel_subscriber_count,
            'channel_view_count': channel_view_count,
            'channel_description': channel_description,
            'channel_country': channel_country,
            'channel_video_count': channel_video_count,
            'channel_playlist_id': channel_playlist_id,
            'channel_type': channel_type
        }
    }
    
    def get_video_ids(youtube, channel_playlist_id):
        next_page_token = None
        video_id = []
        while True:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=channel_playlist_id,
                maxResults=50,
                pageToken=next_page_token)
            response = request.execute()
            for item in response['items']:
                video_id.append(item['contentDetails']['videoId'])
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        return video_id
    video_ids = get_video_ids(youtube, channel_playlist_id)
    
    def get_video_data(youtube, video_ids):
        video_data = []
        for video_id in video_ids:                      
            request = youtube.videos().list(
                part='snippet, statistics, contentDetails',
                id=video_id)
            response = request.execute()
            video = response['items'][0]
            try:
                video['comment_threads'] = get_video_comments(youtube, video_id, max_comments=2)
            except:
                video['comment_threads'] = None
            duration = video.get('contentDetails', {}).get('duration', 'Not Available')
            if duration != 'Not Available':
                duration = convert_duration(duration)
            video['contentDetails']['duration'] = duration
            video_data.append(video)
        return video_data
    
    def get_video_comments(youtube, video_id, max_comments):
        request = youtube.commentThreads().list(
            part='snippet',
            maxResults=max_comments,
            textFormat="plainText",
            videoId=video_id)
        response = request.execute()
        return response
    
    def convert_duration(duration):
        regex = r'PT(\d+H)?(\d+M)?(\d+S)?'
        match = re.match(regex, duration)
        if not match:
            return '00:00:00'
        hours, minutes, seconds = match.groups()
        hours = int(hours[:-1]) if hours else 0
        minutes = int(minutes[:-1]) if minutes else 0
        seconds = int(seconds[:-1]) if seconds else 0
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return '{:02d}:{:02d}:{:02d}'.format(int(total_seconds / 3600), int((total_seconds % 3600) / 60), int(total_seconds % 60))
    video_data = get_video_data(youtube, video_ids)

    videos = {}
    for i, video in enumerate (video_data):
        video_id = video['id']
        video_name = video['snippet']['title']
        video_description = video['snippet']['description']
        tags = video['snippet'].get('tags', [])
        published_at = video['snippet']['publishedAt']
        view_count = video['statistics']['viewCount']
        like_count = video['statistics'].get('likeCount', 0)
        dislike_count = video['statistics'].get('dislikeCount', 0)
        favorite_count = video['statistics'].get('favoriteCount', 0)
        comment_count = video['statistics'].get('commentCount', 0)
        duration = video.get('contentDetails', {}).get('duration', 'Not Available')
        thumbnail = video['snippet']['thumbnails']['high']['url']
        caption_status = video.get('contentDetails', {}).get('caption', 'Not Available')
        comments = 'Unavailable'
        dateandtime= published_at.split("T")
        date, time = dateandtime
        time = time[:-1]
        date_time = date + time

        if video['comment_threads'] is not None:
            comments = {}
            for index, comment_thread in enumerate(video['comment_threads']['items']):
                comment = comment_thread['snippet']['topLevelComment']['snippet']
                comment_id = comment_thread['id']
                comment_text = comment['textDisplay']
                comment_author = comment['authorDisplayName']
                comment_published_at = comment['publishedAt']
                comments[f"Comment_Id_{index + 1}"] = {
                    'Comment_Id': comment_id,
                    'Comment_Text': comment_text,
                    'Comment_Author': comment_author,
                    'Comment_PublishedAt': comment_published_at
                }               
        
        videos[f"Video_Id_{i + 1}"] = {
            'Video_Id': video_id,
            'Video_Name': video_name,
            'Video_Description': video_description,
            'Tags': tags,
            'PublishedAt': date_time,
            'View_Count': view_count,
            'Like_Count': like_count,
            'Dislike_Count': dislike_count,
            'Favorite_Count': favorite_count,
            'Comment_Count': comment_count,
            'Duration': duration,
            'Thumbnail': thumbnail,
            'Caption_Status': caption_status,
            'Comments': comments
        }
    
    whole_data = {**channel_data,**videos}
    
    whole_final_data={'Channel_Name': channel_name,'channel_data': whole_data}
    final_data = json.dumps(whole_final_data)
    with col2:
        text(final_data,height = 700)
    col3.warning("Exporting.... to **MongoDB**")

    #MongoDB 
    client = "####################USE YOUR MONGODB STRING CONNECTION#########################"
    try:
        conn = MongoClient(client)
    except:
        col2.warning("Error on Connection")
        exit()
    db = conn['YouTubeData']
    collection = db['Video_details']
    upload = collection.replace_one({'_id': channel_id}, whole_final_data, upsert=True)
    col3.warning("Data Exported To MongoDB")

    #MongoDB To  SQLite
    col1.subheader(":violet[Migrate] to :red[SQLite]")
    document_names = []
    a = collection.find()
    for document in collection.find():
        document_names.append(document["Channel_Name"])
    document_name = col1.selectbox('Select Channel available from :green[MongoDB]', options = document_names, key='document_names')
    Migrate = col1.button('Migrate to MySQL')
    col1.divider()
    if Migrate:
        result = collection.find_one({"Channel_Name": document_name})

        channel_details_to_sql = {
            "Channel_Name": result['Channel_Name'],
            "channel_id": result['_id'],
            "channel_country":result['channel_data']['channel_details']['channel_country'],
            "channel_view_count": result['channel_data']['channel_details']['channel_view_count'],
            "channel_video_count":result['channel_data']['channel_details']['channel_video_count'],
            "channel_subscriber_count": result['channel_data']['channel_details']['channel_subscriber_count'],
            "channel_description": result['channel_data']['channel_details']['channel_description'],
            "channel_playlist_id": result['channel_data']['channel_details']['channel_playlist_id'],
            "channel_type": result['channel_data']['channel_details']['channel_type']
            }
        channel_df = pd.DataFrame.from_dict(channel_details_to_sql, orient='index').T

        playlist_tosql = {"Channel_Id": result['_id'],
                        "channel_playlist_id": result['channel_data']['channel_details']['channel_playlist_id']
                        }
        playlist_df = pd.DataFrame.from_dict(playlist_tosql, orient='index').T
        
        video_details_list = []
        for i in range(1,len(result['channel_data'])-1):
            video_details_tosql = {
                'channel_playlist_id':result['channel_data']['channel_details']['channel_playlist_id'],
                'Video_Id': result['channel_data'][f"Video_Id_{i}"]['Video_Id'],
                'Video_Name': result['channel_data'][f"Video_Id_{i}"]['Video_Name'],
                'Video_Description': result['channel_data'][f"Video_Id_{i}"]['Video_Description'],
                'Published_date': result['channel_data'][f"Video_Id_{i}"]['PublishedAt'],
                'View_Count': result['channel_data'][f"Video_Id_{i}"]['View_Count'],
                'Like_Count': result['channel_data'][f"Video_Id_{i}"]['Like_Count'],
                'Dislike_Count': result['channel_data'][f"Video_Id_{i}"]['Dislike_Count'],
                'Favorite_Count': result['channel_data'][f"Video_Id_{i}"]['Favorite_Count'],
                'Comment_Count': result['channel_data'][f"Video_Id_{i}"]['Comment_Count'],
                'Duration': result['channel_data'][f"Video_Id_{i}"]['Duration'],
                'Thumbnail': result['channel_data'][f"Video_Id_{i}"]['Thumbnail'],
                'Caption_Status': result['channel_data'][f"Video_Id_{i}"]['Caption_Status']
                }
            video_details_list.append(video_details_tosql)
        video_df = pd.DataFrame(video_details_list)

        Comment_details_list = []
        for i in range(1, len(result['channel_data']) - 1):
            comments_access = result['channel_data'][f"Video_Id_{i}"]['Comments']
            if comments_access == 'Unavailable' or ('Comment_Id_1' not in comments_access or 'Comment_Id_2' not in comments_access) :
                Comment_details_tosql = {
                    'Video_Id': 'Unavailable',
                    'Comment_Id': 'Unavailable',
                    'Comment_Text': 'Unavailable',
                    'Comment_Author':'Unavailable',
                    'Comment_Published_date': 'Unavailable',
                    }
                Comment_details_list.append(Comment_details_tosql)
                
            else:
                for j in range(1,3):
                    Comment_details_tosql = {
                    'Video_Id': result['channel_data'][f"Video_Id_{i}"]['Video_Id'],
                    'Comment_Id': result['channel_data'][f"Video_Id_{i}"]['Comments'][f"Comment_Id_{j}"]['Comment_Id'],
                    'Comment_Text': result['channel_data'][f"Video_Id_{i}"]['Comments'][f"Comment_Id_{j}"]['Comment_Text'],
                    'Comment_Author': result['channel_data'][f"Video_Id_{i}"]['Comments'][f"Comment_Id_{j}"]['Comment_Author'],
                    'Comment_Published_date': result['channel_data'][f"Video_Id_{i}"]['Comments'][f"Comment_Id_{j}"]['Comment_PublishedAt'],
                    }
                    Comment_details_list.append(Comment_details_tosql)
        Comments_df = pd.DataFrame(Comment_details_list)
        
        conn = sqlite3.connect('YouTubeData.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel (
        Channel_Name TEXT,
        channel_id TEXT PRIMARY KEY,
        channel_video_count INTEGER,
        channel_view_count INTEGER,
        channel_subscriber_count INTEGER,
        channel_description TEXT,
        channel_playlist_id TEXT,
        channel_type TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist (
        channel_id TEXT,
        channel_playlist_id TEXT PRIMARY KEY,
        FOREIGN KEY (channel_id) REFERENCES channel(channel_id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS video (
        channel_playlist_id TEXT,
        Video_Id TEXT PRIMARY KEY,
        Video_Name TEXT,
        Video_Description TEXT,
        Published_date TEXT,
        View_Count INTEGER,
        Like_Count INTEGER,
        Dislike_Count INTEGER,
        Favorite_Count INTEGER,
        Comment_Count INTEGER,
        Duration TEXT,
        Thumbnail TEXT,
        Caption_Status TEXT,
        FOREIGN KEY (channel_playlist_id) REFERENCES playlist(channel_playlist_id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
        Video_Id TEXT,
        Comment_Id TEXT,
        Comment_Text TEXT,
        Comment_Author TEXT,
        Comment_Published_date TEXT,
        FOREIGN KEY (Video_Id) REFERENCES video(Video_Id)
        )
        ''')
        
        for _, row in channel_df.iterrows():
            try:
                cursor.execute("INSERT INTO channel (Channel_Name, channel_id, channel_video_count, channel_subscriber_count, channel_view_count, channel_description, channel_playlist_id) VALUES (?, ?, ?, ?, ?, ?, ?)",(row['Channel_Name'], row['channel_id'], row['channel_video_count'], row['channel_subscriber_count'], row['channel_view_count'], row['channel_description'], row['channel_playlist_id']))
                conn.commit()
            except sqlite3.IntegrityError:
                col3.warning(f"Already added channel_id: {row['channel_id']}")

        for _, row in playlist_df.iterrows():
            try:
                cursor.execute("INSERT INTO playlist (Channel_Id, channel_playlist_id) VALUES (?, ?)",(row['Channel_Id'], row['channel_playlist_id']))
                conn.commit()
            except sqlite3.IntegrityError:
                col1.write("")

        for _, row in video_df.iterrows():
            try:
                cursor.execute("INSERT INTO video (channel_playlist_id, Video_Id, Video_Name, Video_Description, Published_date, View_Count, Like_Count, Dislike_Count, Favorite_Count, Comment_Count, Duration, Thumbnail, Caption_Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(row['channel_playlist_id'], row['Video_Id'], row['Video_Name'], row['Video_Description'], row['Published_date'], row['View_Count'], row['Like_Count'], row['Dislike_Count'], row['Favorite_Count'], row['Comment_Count'], row['Duration'], row['Thumbnail'], row['Caption_Status']))
                conn.commit()
            except sqlite3.IntegrityError:
                col1.write("")

        for _, row in Comments_df.iterrows():
            try:
                cursor.execute("INSERT INTO comments (Video_Id, Comment_Id, Comment_Text, Comment_Author, Comment_Published_date) VALUES (?, ?, ?, ?, ?)",(row['Video_Id'], row['Comment_Id'], row['Comment_Text'], row['Comment_Author'], row['Comment_Published_date']))
                conn.commit()
            except sqlite3.IntegrityError:
                col1.write("")
        col3.warning("SQL Connected")
        conn.commit()
        cursor.close()
        conn.close()

        col1.subheader("List Of channel available in SQLite")
        engine = create_engine('sqlite:///YoutubeData.db')
        query = "SELECT Channel_Name FROM channel;"
        results = pd.read_sql(query, engine)
        channel_names_fromsql = list(results['Channel_Name'])
        df_at_sql = pd.DataFrame(channel_names_fromsql, columns=['Available channel data']).reset_index(drop=True)
        df_at_sql.index += 1  
        col1.dataframe(df_at_sql)
        st.divider()


    st.header("Channel Analysis")
    conn = sqlite3.connect('YoutubeData.db')
    cursor = conn.cursor()

    Q1 = st.checkbox("1.What are the names of all the videos and their corresponding channels?")
    if Q1:
        cursor.execute("SELECT channel.Channel_Name, video.Video_Name FROM channel JOIN playlist JOIN video ON channel.channel_Id = playlist.Channel_Id AND playlist.channel_playlist_id = video.channel_playlist_id;")
        result_1 = cursor.fetchall()
        df1 = pd.DataFrame(result_1, columns=['Channel Name', 'Video Name']).reset_index(drop=True)
        df1.index += 1
        st.dataframe(df1)
    st.divider()

    Q2 = st.checkbox("2.Which channels have the most number of videos, and how many videos do they have?")
    if Q2:
        colq21,colq22= st.columns(2)
        cursor.execute("SELECT Channel_Name, channel_video_count FROM channel ORDER BY channel_video_count DESC;")
        result_2 = cursor.fetchall()
        df2 = pd.DataFrame(result_2,columns=['Channel Name','Video Count']).reset_index(drop=True)
        df2.index += 1
        colq21.dataframe(df2)
        figure_q2 = go.Figure(data=[go.Bar(x=df2['Channel Name'], y=df2['Video Count'], marker=dict(color='#E6064A'))])
        figure_q2.update_layout(title="Most number of videos", title_font=dict(size=25), title_font_color='#1308C2')
        #figure_q2.update_traces(texttemplate='%{text:.2s}', textfont_size=16)
        colq22.plotly_chart(figure_q2,use_container_width=True)
    st.divider()

    Q3 = st.checkbox("3.What are the top 10 most viewed videos and their respective channels?")
    if Q3:
        colq31,colq32 = st.columns(2)
        cursor.execute("SELECT channel.Channel_Name, video.Video_Name, video.View_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.channel_playlist_id = video.channel_playlist_id ORDER BY video.View_Count DESC LIMIT 10;")
        result_3 = cursor.fetchall()
        df3 = pd.DataFrame(result_3,columns=['Channel Name', 'Video Name', 'View count']).reset_index(drop=True)
        df3.index += 1
        df_3 = df3.sort_values(by=['View count'], ascending=False)
        st.dataframe(df_3)
        figure_q3 = go.Figure(data =[go.Bar(x=df3['Video Name'],y=df3['View count'],marker_color='#E6064A')])
        figure_q3.update_layout(title="Top 10 Most Viewed Videos",title_font_color='#1308C2',title_font=dict(size=25),yaxis_title="Video Count",xaxis_title="View Name")
        figure_q3.update_traces(textfont_size=16)
        st.plotly_chart(figure_q3,use_container_width=True)
    st.divider()

    Q4 = st.checkbox("4.How many comments were made on each video, and what are their corresponding video names?")
    if Q4:
        cursor.execute("SELECT channel.Channel_Name, video.Video_Name, video.Comment_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.channel_playlist_id = video.channel_playlist_id ORDER BY video.Comment_Count DESC;")
        result_4 = cursor.fetchall()
        df4 = pd.DataFrame(result_4,columns=['Channel Name', 'Video Name', 'Comment count']).reset_index(drop=True)
        df4.index += 1
        #df_4 = df4.sort_values(by=['Comment count'], ascending=False)
        st.dataframe(df4)
    st.divider()

    Q5 = st.checkbox("5.Which videos have the highest number of likes, and what are their corresponding channel names?")
    if Q5:
        cursor.execute("SELECT channel.Channel_Name, video.Video_Name, video.Like_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.channel_playlist_id = video.channel_playlist_id ORDER BY video.Like_Count DESC;")
        result_5= cursor.fetchall()
        df5 = pd.DataFrame(result_5,columns=['Channel Name', 'Video Name', 'Like count']).reset_index(drop=True)
        #df5.sort_values(by=[""])
        df5.index += 1
        st.dataframe(df5)
    st.divider()

    Q6 = st.checkbox("6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?")
    if Q6:
        st.write('**Note:- In November 2021, YouTube removed the public dislike count from all of its videos.**')
        cursor.execute("SELECT channel.Channel_Name, video.Video_Name, video.Like_Count, video.Dislike_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.channel_playlist_id = video.channel_playlist_id;")
        result_6= cursor.fetchall()
        df6 = pd.DataFrame(result_6,columns=['Channel Name', 'Video Name', 'Like count','Dislike count']).reset_index(drop=True)
        df6.index += 1
        st.dataframe(df6)
    st.divider()

    Q7 = st.checkbox("7.What is the total number of views for each channel, and what are their corresponding channel names?")
    if Q7:
        cursor.execute("SELECT Channel_Name, channel_view_count FROM channel ORDER BY channel_view_count DESC;")
        result_7= cursor.fetchall()
        df7 = pd.DataFrame(result_7,columns=['Channel Name', 'Total number of views']).reset_index(drop=True)
        df7.index += 1
        st.dataframe(df7)
    st.divider()

    Q8 = st.checkbox("8.What are the names of all the channels that have published videos in the year 2022?")
    if Q8:
        cursor.execute("SELECT channel.Channel_Name, video.Video_Name, video.Published_date FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.channel_playlist_id = video.channel_playlist_id WHERE published_date BETWEEN '2022-01-01' AND '2022-12-31'")
        result_8= cursor.fetchall()
        df8 = pd.DataFrame(result_8,columns=['Channel Name','Video Name', 'Year 2022 only']).reset_index(drop=True)
        df8.index += 1
        st.dataframe(df8)
    st.divider()

    Q9 = st.checkbox("9.What is the average duration of all videos in each channel, and what are their corresponding channel names?")
    if Q9:
        cursor.execute("SELECT c.Channel_Name, AVG(v.Duration) AS average_duration FROM channel c JOIN playlist p ON c.channel_id = p.channel_id JOIN video v ON p.channel_playlist_id = v.channel_playlist_id GROUP BY c.Channel_Name ORDER BY average_duration;")
        result_9 = cursor.fetchall()
        df9 = pd.DataFrame(result_9,columns=['Channel Name','Average duration of videos (HH:MM:SS)']).reset_index(drop=True)
        df9.index += 1
        st.dataframe(df9)
    st.divider()

    Q10 = st.checkbox("10.Which videos have the highest number of comments, and what are their corresponding channel names?")
    if Q10:
        cursor.execute("SELECT channel.Channel_Name, video.Video_Name, video.Comment_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.channel_playlist_id = video.channel_playlist_id ORDER BY video.Comment_Count DESC;")
        result_10= cursor.fetchall()
        df10 = pd.DataFrame(result_10,columns=['Channel Name','Video Name', 'Number of comments']).reset_index(drop=True)
        df10.index += 1
        st.dataframe(df10)
