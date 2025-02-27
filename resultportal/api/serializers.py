from rest_framework import serializers
from .models import User, Result, Complaint

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'student', 'subject', 'score', 'grade', 'remarks', 'uploaded_by']

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'student', 'subject', 'content', 'created_at', 'resolved']

class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()