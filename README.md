# Smart Meeting Scheduler

Smart Meeting Scheduler is an AI-powered application designed to help you effortlessly schedule meetings. The platform integrates seamlessly with your existing calendars and provides intelligent suggestions for the best meeting times based on participants' availability.

## Features

- AI-Powered Suggestions: Our AI suggests the best meeting times based on participants' availability.
- Calendar Integration: Seamlessly integrate with your existing calendars to avoid conflicts.
- User-Friendly Interface: Enjoy a clean and intuitive interface for scheduling and managing meetings.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/smart-meeting-scheduler.git
    cd smart-meeting-scheduler
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Initialize the database:
    ```bash
    python database.py
    ```

## Usage

1. Run the application:
    ```bash
    python app.py
    ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

## Project Structure

```
smart-meeting-scheduler/
│
├── templates/
│   ├── availability.html
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── schedule.html
│
├── static/
│   └── styles.css
│
├── app.py
├── database.py
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or inquiries, please contact [yourname@example.com](mailto:yourname@example.com).
