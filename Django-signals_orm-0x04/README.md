# Messaging App

A Django-based real-time messaging application that allows users to create conversations and exchange messages.

## Features

- User authentication and management
- Create and manage conversations
- Real-time messaging between users
- Multiple participants in conversations
- Message read status tracking
- REST API for frontend integration

## Tech Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT-based authentication
- **API**: RESTful API endpoints

## Project Structure

```
messaging_app/
├── chats/                  # Main application
│   ├── models.py           # Data models
│   ├── serializers.py      # API serializers
│   ├── views.py            # API viewsets
│   └── urls.py             # API routing
├── messaging_app/          # Project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI configuration
└── manage.py               # Django management script
```

## API Endpoints

### Conversations
- `GET /conversations/` - List all conversations for the authenticated user
- `POST /conversations/` - Create a new conversation
- `GET /conversations/{id}/` - Get conversation details
- `POST /conversations/{id}/add_participant/` - Add a participant to a conversation

### Messages
- `GET /conversations/{conversation_id}/messages/` - List all messages in a conversation
- `POST /conversations/{conversation_id}/messages/` - Send a new message
- `GET /conversations/{conversation_id}/messages/{id}/` - Get specific message details

## Models

### User
- User authentication and profile information
- Fields: user_id, username, email, first_name, last_name, bio, avatar

### Conversation
- Represents a chat between multiple users
- Fields: conversation_id, participants (M2M), created_at, updated_at

### Message
- Individual messages within conversations
- Fields: message_id, conversation, sender, content, timestamp, is_read

## Installation

### Prerequisites
- Python 3.10+
- Django

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd messaging_app
```

### Option 1: Using UV (Recommended)

1. Install dependencies using UV:
```bash
uv install
```

2. For adding new dependencies:
```bash
uv add <package-name>
```

### Option 2: Using Virtual Environment & Pip

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies using pip:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

## Usage

### Creating a Conversation
```python
POST /conversations/
Content-Type: application/json
Authorization: Bearer <token>

{
  "participants": ["user_id_1", "user_id_2"]
}
```

### Sending a Message
```python
POST /conversations/{conversation_id}/messages/
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "Hello, how are you?"
}
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 guidelines for Python code style.

### Dependency Management

This project uses UV for dependency management with a `pyproject.toml` file:

- `uv.lock` - Lock file that stores exact versions of dependencies
- `pyproject.toml` - Defines project metadata and dependencies

#### Adding Dependencies

```bash
# With UV
uv add package_name

# With pip (will not update pyproject.toml)
pip install package_name
```

#### Updating Dependencies

```bash
# With UV
uv sync

# With pip
pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

MIT License
