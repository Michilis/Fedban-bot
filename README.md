# Fedban Bot

A Telegram bot to manage federations, ban/unban users, transfer federation ownership, and other administrative tasks. Built with Pyrogram and PostgreSQL.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/fedban_bot.git
    cd fedban_bot
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure environment variables:
    - Create a `.env` file with the following content:
      ```plaintext
      BOT_TOKEN=your_bot_token
      DATABASE_URL=your_database_url
      LOG_GROUP_ID=your_log_group_id
      SUDOERS=comma_separated_list_of_sudoers
      ```

4. Run the bot:
    ```bash
    python -m bot.main
    ```

## Features

- Create, delete, and manage federations
- Ban/unban users across federations
- Transfer federation ownership
- Administrative commands and more

## License

This project is licensed under the MIT License - see the LICENSE file for details.
