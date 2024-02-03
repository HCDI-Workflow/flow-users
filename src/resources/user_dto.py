# user_dto.py
from model.user import User
# user_dto.py

class UserDTO:
    @staticmethod
    def from_model(user):
        """
        Transforms a User model instance into a DTO format.
        """
        try:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                # 'password': user.password,
                # 'oath_token': user.oath_token,
                # 'auth_type':user.auth_type
                # Exclude password, oath_token, and auth_type for security
            }
        except:
            return None

    @staticmethod
    def to_model(data):
        """
        Returns model if value, otherwise returns None
        """
        # Assuming a User class and a password hashing function exist
        try:
            if 'username' not in data or 'email' not in data or 'name' not in data:
                raise ValueError("Missing mandatory user fields")

            password = data.get('password')

            return User(
                id=data.get('id'),
                username=data['username'],
                email=data['email'],
                name=data['name'],
                password=password,
                oath_token=data.get('oath_token', None),
                auth_type=data.get('auth_type', 'local')
            )
        except:
            return None
# class UserDTO:
#     @staticmethod
#     def from_model(user):
#         """
#         Transforms a User model instance into a DTO format.
#         """
#         return {
#             'id': user.id,
#             'username': user.username,
#             'email': user.email,
#             'name': user.name
#             # Exclude password and oath_token for security
#         }

#     @staticmethod
#     def to_model(data):
#         """
#         Creates a User model instance from provided data.
#         """
#         return User(
#             id=data.get('id'),
#             username=data['username'],
#             email=data['email'],
#             name=data['name'],
#             password=data['password'],  # Ensure this is hashed appropriately
#             oath_token=data.get('oath_token', None)  # Optional field
#         )
