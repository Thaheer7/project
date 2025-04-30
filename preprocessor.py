import re
import pandas as pd


def preprocess(data):

    data = data.replace('â¯', ' ')
    pattern = r'\d{1,2}\/\d{1,2}\/\d{2},\s\d{1,2}:\d{2}\s(?:AM|PM)\s-\s'

    # Split the messages and extract dates
    messages = re.split(pattern, data)[1:]  # Split by the pattern and ignore the first entry
    dates = re.findall(pattern, data)  # Extract the dates

    # Create DataFrame from messages and dates
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    df['cleaned_date'] = df['message_date'].str.replace(r'\s*-\s*$', '', regex=True).str.strip()

    df['formatted_datetime'] = pd.to_datetime(
        df['cleaned_date'],
        format='%m/%d/%y, %I:%M %p'
    )

    df['formatted_datetime'] = df['formatted_datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    df = df.drop(['message_date', 'cleaned_date'], axis=1)

    df.rename(columns={'formatted_datetime': 'date'}, inplace=True)

    # Initialize lists to store users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    # Drop the original 'user_message' column as it's no longer needed
    df.drop(columns=['user_message'], inplace=True)

    df['date'] = pd.to_datetime(df['date'])

    # Add new date-related columns for further analysis
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create periods based on the hour
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f'{hour}-{00}')  # Handle 23-00 case
        elif hour == 0:
            period.append(f'{00}-{hour + 1}')  # Handle 00-01 case
        else:
            period.append(f'{hour}-{hour + 1}')  # Regular case: e.g., 1-2, 2-3, etc.

    # Add 'period' column to the DataFrame
    df['period'] = period

    return df
