
# Route to serve the HTML form
  # Assumes 'index.html' is in the 'templates' folder

# Route to handle form submission

from app import app
DEBUG_FLAG = False # For detailed errors. False in production

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, ssl_context=("certs/cert.pem", "certs/key.pem"), debug=DEBUG_FLAG)
