from rest_framework.response import Response
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer, OrganizationSerializer
from .models import CustomUser, Organisation
from rest_framework import status
from rest_framework.views import APIView
from .tokens import get_tokens_for_user
from django.shortcuts import get_object_or_404
from rest_framework import permissions


class RegisterAPI(generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response(
                {
                    "status": "success",
                    "message": "Registration successful",
                    "data": {
                        "accessToken": tokens.get("access"),
                        "user": {
                            "userId": user.userId,
                            "firstName": serializer.data["firstName"],
                            "lastName": serializer.data["lastName"],
                            "email": serializer.data["email"],
                            "phone": serializer.data["phone"],
                        },
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        else:

            return Response(
                {
                    "status": "Bad Request",
                    "message": "Registration unsuccessful",
                    "statusCode": 400,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            tokens = get_tokens_for_user(user)
            return Response(
                {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": tokens.get("access"),
                        "user": {
                            "userId": user.userId,
                            "firstName": user.firstName,
                            "lastName": user.lastName,
                            "email": user.email,
                            "phone": (
                                user.phone_number
                                if hasattr(user, "phone_number")
                                else None
                            ),
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Include validation errors in the response
            return Response(
                {
                    "status": "Bad Request",
                    "message": "Authentication failed",
                    "statusCode": 401,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UserDetail(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        response = {
            "status": "success",
            "message": "The user was retrieved successfully",
            "data": {
                "userId": user.userId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phone": user.phone if hasattr(user, "phone") else None,
            },
        }
        return Response(response, status=status.HTTP_200_OK)


class UserOrganizations(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Organisation.user_org.for_user(user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        organizations_data = []
        for org in serializer.data:
            org_data = {
                "orgId": org.get("orgId", "string"),
                "name": org.get("name", "string"),
                "description": org.get("description", "string"),
            }
            organizations_data.append(org_data)

        response_data = {
            "status": "success",
            "message": "Your organizations were retrieved successfully",
            "data": {"organizations": organizations_data},
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_organization(request, orgId):
    organization = get_object_or_404(Organisation, orgId=orgId)
    serializer = OrganizationSerializer(organization)
    response = {
        "status": "success",
        "message": "The organization was retrieved successfully",
        "data": {
            "orgId": organization.orgId,
            "name": organization.name,
            "description": organization.description,
        },
    }

    return Response(response, status=status.HTTP_200_OK)


# class CreateOrganization(generics.CreateAPIView):
#     queryset = Organisation.user_org.all()
#     serializer_class = OrganizationSerializer

#     def get_queryset(self):
#         # Filter the queryset based on the request user
#         return Organisation.objects.filter(users=self.request.user)

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             organization = serializer.save()
#             organization.users.add(request.user)
#             organization.save()
#             return Response(
#                 {
#                     "status": "success",
#                     "message": "Organization created successfully",
#                     "data": {
#                         "orgId": organization.orgId,
#                         "name": organization.name,
#                         "description": organization.description,
#                     },
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#         else:
#             return Response(
#                 {
#                     "status": "Bad Request",
#                     "message": "Client error",
#                     "statusCode": 400,
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_organization(request):
    data = request.data.copy()
    data["users"] = [request.user.id]

    serializer = OrganizationSerializer(data=data)
    if serializer.is_valid():
        organization = serializer.save()
        return Response(
            {
                "status": "success",
                "message": "Organization created successfully",
                "data": {
                    "orgId": organization.orgId,
                    "name": organization.name,
                    "description": organization.description,
                },
            },
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(
            {
                "status": "Bad Request",
                "message": "Client error",
                "errors": serializer.errors,
                "statusCode": 400,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def add_user_to_organization(request, orgId):
    user = get_object_or_404(CustomUser, userId=request.user.userId)
    userId = user.userId
    if not userId:
        return Response(
            {
                "status": "Bad Request",
                "message": "userId is required",
                "statusCode": 400,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        organization = get_object_or_404(Organisation, orgId=orgId)
    except Exception as e:
        return Response(
            {
                "status": "Not Found",
                "message": str(e),
                "statusCode": 404,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if user in organization.users.all():
        return Response(
            {
                "status": "Bad Request",
                "message": "User already exists in the organization",
                "statusCode": 400,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    organization.users.add(user)
    organization.save()

    return Response(
        {
            "status": "success",
            "message": "User added to organisation successfully",
        },
        status=status.HTTP_200_OK,
    )
