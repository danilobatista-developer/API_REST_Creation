RESTful API Creation


The objective of this project is to develop a RESTful API for managing a vehicle inventory. The API includes the following endpoints:

GET /vehicles: Retrieves a list of all vehicles.
POST /vehicles: Creates a new vehicle entry.
GET /vehicles/{id}: Fetches the details of a specific vehicle by its ID.
PUT /vehicles/{id}: Updates the status of a vehicle to either "CONNECTED" or "DISCONNECTED".
DELETE /vehicles/{id}: Deletes a vehicle by its ID.
Authentication and Authorization
A robust authentication and authorization mechanism has been implemented. Only users who are authenticated and authorized can access the API endpoints.

API Documentation
Comprehensive documentation is provided for the API. It includes detailed descriptions of all endpoints, parameters, responses, and usage examples. This documentation is designed to be clear and accessible for users and developers.

Unit Testing
Unit tests are included to ensure the API functions correctly and maintains high quality. These tests cover the primary use cases and verify that each endpoint returns the expected responses.

Local Service Execution
Instructions are provided for running the service locally. These instructions ensure that users can set up and test the API endpoints on their own machines, performing CRUD operations as needed.
