# RestaurantApp

This project is a example of restaurant app. The project consists of a Telegram bot and a FastAPI application.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/evil-kekc/TestTask.git
   ```

2. Creating and activating a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Creating and activating settings
    * Create a new file named `.env` in the project directory.

    * Open the .env file and add the following lines, replacing `<ADMIN_ID>`, `<TOKEN>` and `<HOST_URL>` with your
      settings. To send messages through the form on the site, you need to specify `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`.

   ```plaintext
   ADMIN_ID=23456789
   TOKEN=123456789:OIXUGJKSGYAAf6SGES
   HOST_URL=https://example.com
   ADMIN_EMAIL=3371824@gmail.com
   ADMIN_EMAIL_PASSWORD=password_examle
   ```

2. Run app
   ```bash
   uvicorn app.main:app --reload
   ```
