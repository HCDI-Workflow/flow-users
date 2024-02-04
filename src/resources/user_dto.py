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
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password': user.password,
                'auth_type':user.auth_type
                # Exclude password, oath_token, and auth_type for security
            }
        except:
            return None
    @staticmethod
    def from_model_update(user):
        """
        Transforms a User model instance into a DTO format.
        """
        try:
            return {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password': user.password,
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
        print("to_model",data)
        try:
            if 'username' not in data or 'email' not in data or 'first_name' not in data or 'last_name' not in data:
                print("Missing mandatory user fields")
                raise ValueError("Missing mandatory user fields")

            password = data.get('password')
            print("Passed check")

            return User(
                id=data.get('id'),
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=password,
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
