import csv

from paths import POSTS_CSV, USERS_CSV


def user_posts(client, location):
    users = list(client.location_medias_v1_chunk(location[0].external_id, 10, "ranked"))

    posts_dict = []
    # business_dict = []
    i = 0
    for user in users:
        try:
            if user:
                for post in user:
                    if post:
                        # ig_user = user[i].user.username
                        # ig_user_info = client.user_info_by_username(ig_user)
                        # if ig_user_info.is_business and ig_user_info.business_category_name == "Food & Beverage":
                        #     businesses_dict = {
                        #         'pk': ig_user_info.pk,
                        #         'username': ig_user_info.username,
                        #         'followers': ig_user_info.follower_count
                        #     }
                        #     business_dict.append(businesses_dict)
                        # else:
                        user_dict = {
                            'pk': user[i].user.pk,
                            'username': user[i].user.username,
                            'likes': user[i].like_count,
                            'comments': user[i].comment_count,
                        }
                        posts_dict.append(user_dict)
                    i += 1
        except IndexError:
            break

    filename = POSTS_CSV
    # with open("business.csv", "w", newline="") as f:
    #     writer = csv.writer(f)
    #
    #     # Set the fieldnames argument to the list of column names
    #     writer.writerow(["pk", "username", "followers"])
    #
    #     # Write the rows of data to the file
    #     for user in business_dict:
    #         writer.writerow([user["pk"], user["username"], user["followers"]])

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pk", "username", "likes", "comments"])
        for user in posts_dict:
            writer.writerow([user["pk"], user["username"], user["likes"], user["comments"]])

    return filename


def location_data(client, locations):
    users = client.location_medias_v1_chunk(locations[0].external_id, 15, "ranked")

    users_dict = []
    for userr in users:
        try:
            if userr:
                for media in userr:
                    if media:
                        if media.user is not None:
                            ig_user = media.user.username
                            ig_user_info = client.user_info_by_username(ig_user)
                            if ig_user_info.username not in [user_dict['username'] for user_dict in users_dict]:
                                keywords = ['collab', 'collaborations', 'collabs', 'collaboration', 'dm', 'inquiries']
                                for_collab = 1 if any(keyword in ig_user_info.biography for keyword in keywords) else 0
                                user_dict = {
                                    'username': ig_user,
                                    'bio': ig_user_info.biography,
                                    'comment_count': media.comment_count,
                                    'like_count': media.like_count,
                                    'follower_count': ig_user_info.follower_count,
                                    'collab': for_collab
                                }
                                users_dict.append(user_dict)
        except IndexError:
            break

    filename = USERS_CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["username", "bio", "comment_count", "like_count", "follower_count", "collab"])
        for userr in users_dict:
            writer.writerow([userr["username"], userr["bio"], userr["comment_count"], userr["like_count"],
                             userr["follower_count"], userr["collab"]])
    return filename
