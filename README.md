# lambda-authorizer

![alt text](image.png)
# AWS API Gateway with Cognito Authentication and Group-Based Lambda Authorizer

This repository demonstrates how to set up an API Gateway secured with AWS Cognito for user authentication and a Lambda Authorizer for group-based authorization logic. The setup ensures that only authenticated users in specific groups (e.g., `admin` or `read-only`) can access your API with appropriate permissions.

---

## Features

1. **Cognito User Pool for Authentication**:

   * Users authenticate using AWS Cognito, which issues JSON Web Tokens (JWTs) upon successful login.

2. **Lambda Authorizer for Group-Based Authorization**:

   * API Gateway calls a Lambda Authorizer to validate the user's JWT and check their group membership.
   * Users in the `admin` group are granted admin-level access.
   * Users in the `read-only` group are granted limited access.
   * Unauthorized users are denied access.

3. **API Gateway**:

   * Serves as the entry point for client requests, secured with the Lambda Authorizer.

---

## Workflow

1. The user logs in using Cognito and receives an authenticated token (JWT).
2. The user sends a request to the API Gateway with the JWT in the `authorizationToken` header.
3. The API Gateway invokes the Lambda Authorizer:

   * The authorizer validates the token and checks the user's group membership.
   * If the user belongs to the `admin` or `read-only` group, the request is forwarded to the API backend with appropriate access permissions.
   * If the user is not in an authorized group, the API Gateway returns an "Unauthorized" response.
4. The backend returns the appropriate response to the user.

---

## Requirements

* AWS Account
* Cognito User Pool with group-based access control
* API Gateway
* Lambda Authorizer
* AWS CLI or AWS Management Console

---

## Setup

### 1. **Cognito User Pool**

* Create a Cognito User Pool and configure it with the desired settings.
* Define user groups such as `admin` and `read-only`.
* Assign users to these groups through the Cognito console.

### 2. **Lambda Authorizer**

* Deploy a Lambda function to serve as the authorizer.
* The function validates the token using Cognito's public keys and checks the user's group membership.


### 3. **API Gateway**

* Configure an API Gateway with the Lambda Authorizer as a custom authorizer.
* Set the `authorizationToken` header as required for all endpoints.

---

## Testing

1. Log in to Cognito to obtain a JWT token.
2. Send a request to the API Gateway with the JWT token in the `authorizationToken` header:

   ```bash
   curl -X GET https://your-api-id.execute-api.your-region.amazonaws.com/prod/resource \
        -H "authorizationToken: <your-jwt-token>"
   ```
3. **Responses**:

   * **200 OK**: If the Lambda Authorizer validates the token and the user is in an authorized group.
   * **403 Forbidden**: If the user is not in the `admin` or `read-only` group.
   * **401 Unauthorized**: If the token is invalid or missing.

---

## Notes

* Ensure the JWT token contains the `cognito:groups` claim by enabling it in the Cognito App Client settings.
* Update the Lambda Authorizer policy to reflect your API Gateway's specific resource ARNs.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
