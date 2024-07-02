from tasks import flask_app, update_item, create_item, delete_item
from flask import request,jsonify 

@flask_app.route('/facebook_bot/update', methods=['POST'])
def update():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    names = []
    for item in data:
        names.append(item["Name"])
        update_item.apply_async(args=[item], queue='task_queue')
    # Return a response immediately
    response = {
        'message': 'Updating in the background',
        'itemNames': names 
    }
    
    return jsonify(response), 200

@flask_app.route('/facebook_bot/delete', methods=['POST'])
def delete():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    names = []
    for item in data:
        names.append(item["Name"])
        delete_item.apply_async(args=[item], queue='task_queue')
    # Return a response immediately
    response = {
        'message': 'Deleting in the background',
        'itemNames': names 
    }
    
    return jsonify(response), 200

@flask_app.route('/facebook_bot/create', methods=['POST'])
def create():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    titles = []
    for item in data:
        titles.append(item["Title"])
        create_item.apply_async(args=[item], queue='task_queue')
    # Return a response immediately
    response = {
        'message': 'Creating in the background',
        'itemTitles': titles 
    }
    
    return jsonify(response), 200


if __name__ == '__main__':
    flask_app.run(port=5002)

