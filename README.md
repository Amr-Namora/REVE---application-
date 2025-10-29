# REVE - Real Estate Mobile App Backend API

This repository contains the backend API for **REVE**, the mobile application component of our multi-platform real estate rental service. While the web platform (**AVAR**) uses Django's built-in templating, this project is a dedicated **Django REST Framework (DRF)** API that exclusively serves data to the REVE mobile app.

## Project Architecture

As the lead backend developer, I architected a **decoupled, service-oriented backend system** where:
- **AVAR**: Full-stack Django website with server-rendered templates
- **REVE**: This project - a pure JSON API built with Django REST Framework
- **Shared Data Model**: Both platforms operate against coherent business logic and data models

## Technical Implementation

### Core Features
- **RESTful API**: Complete set of endpoints for mobile app functionality
- **User Authentication**: Secure token-based auth system for mobile users
- **Property Management**: CRUD operations for property listings with advanced search and filtering
- **Booking System**: Complex booking calendar logic to manage availability and reservations
- **Review System**: User review and rating functionality

### Key Technical Achievements
- Designed **scalable database models** for properties, users, bookings, and reviews
- Implemented **secure API endpoints** with proper authentication and permissions
- Built **complex business logic** for availability management and booking conflicts
- Created **optimized database queries** for fast property search and filtering
- Established **consistent API response formats** and error handling

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/gallery/` | GET | List all real estate properties with search filters |
| `/gallery/<str:pk>/` | GET | Get detailed information about a specific property |
| `/reservation/<int:realestate_id>/` | POST | Create a new reservation for a specific property |
| `/account/token/` | POST | User authentication (login) to obtain access token |

## Technology Stack

- **Backend Framework**: Django + Django REST Framework
- **Authentication**: Token-based authentication
- **Database**: PostgreSQL
- **API Documentation**: Swagger/OpenAPI

## Related Projects

This API works in conjunction with:
- **[AVAR](https://github.com/Amr-Namora/AVAR---website)** - The full-stack web platform for the same real estate service
- **REVE Mobile App** - The frontend mobile application consuming this API
  - **[Download REVE App](https://www.mediafire.com/file/vkwpdkplh6u5gdz/REVE.apk/file)** - Install the mobile application

## Setup & Installation

```bash
# Installation steps
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
