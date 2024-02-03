from user import create_app
from controller import endpoints

from dotenv import load_dotenv
load_dotenv()

# App instance
app = create_app()
app.register_blueprint(endpoints.bp)



@app.route('/', methods=['GET'])
def home():
    return {'home': 'Please go to a specific endpoint'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9090)
