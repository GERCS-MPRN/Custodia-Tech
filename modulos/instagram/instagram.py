from datetime import datetime
import instaloader
import os
import re

def sanitize_filename(filename):
    invalid_chars = r'[\\/:*?"<>|]'
    sanitized_filename = re.sub(invalid_chars, '', filename)
    return sanitized_filename

def download_instagram_por_periodo(username, save_directory, start_date_str, end_date_str):
   
    try:
        
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")

        
        L = instaloader.Instaloader()

        
        formatted_start_date = start_date.strftime("%Y-%m-%d")
        formatted_end_date = end_date.strftime("%Y-%m-%d")

        
        sanitized_username = sanitize_filename(username)
        user_directory = os.path.join(save_directory, f"{sanitized_username}_{formatted_start_date}_{formatted_end_date}")
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)

        
        L.dirname_pattern = user_directory
        L.filename_pattern = f"{sanitized_username}_{formatted_start_date}_{formatted_end_date}_post_{{shortcode}}"

        
        profile = instaloader.Profile.from_username(L.context, username)

       
        found_post = False
        for post in profile.get_posts():
            if start_date <= post.date <= end_date:
                L.download_post(post, target=sanitized_username)
                found_post = True
            elif found_post:
                break

        print(f'Postagens de {start_date.date()} a {end_date.date()} baixadas com sucesso em {user_directory}')
        
    except Exception as e:
        print(f'Ocorreu um erro durante o download: {e}')
        raise  # Relevanta o erro para tratamento posterior
