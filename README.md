# Run facebook bot
python3 app.py

Wait until it fininish logging in Facebook and Flask app show successful message in terminal, then close the browser.
# Run celery
celery -A tasks worker -Q task_queue --concurrency=1 --loglevel INFO

# How to use 

JSON format  
1. Creating items

[
    {
        "title":"item_title",
        "category":"item_category",
        "photo_dir":"item_photo_dir",
        "photo_names":"item_photo_name_1;item_photo_name_2",
        "description":"item description",
        "condition":"item_condition",
        "price":0000
    },
    {
        "title":"item_title",
        "category":"item_category",
        "photo_dir":"item_photo_dir",
        "photo_names":"item_photo_name_1;item_photo_name_2",
        "description":"item description",
        "condition":"item_condition",
        "price":0000
    }
]

2. Update one or more fields in items

[
    {
        "name":"item_to_be_updated",
        "price": 0000,
        "condition":"new_condition",
        "location":"new_location"
    },
    {
        "name":"item_to_be_updated",
        "price": 0000,
        "condition":"new_condition",
        "location":"new_location"
    }
]

3. Delete items

[
    {
        "name":"item_to_be_deleted"
    },
    {
        "name":"item_to_be_deleted"
    }
]