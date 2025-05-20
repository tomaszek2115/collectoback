from app import create_app

# app running file

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)