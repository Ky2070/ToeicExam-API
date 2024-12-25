from rest_framework import serializers
from typing import Dict, Any

class BaseSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True
        fields = ['id', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']

    def to_representation(self, instance) -> Dict[str, Any]:
        """
        Override to_representation to customize the serialized output
        """
        data = super().to_representation(instance)
        
        # Remove null values
        return {
            key: value for key, value in data.items() 
            if value is not None
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add common validation logic here
        """
        # Add your common validation logic
        return super().validate(attrs)

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """
        Add common create logic here
        """
        # Add your common create logic
        return super().create(validated_data)

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        """
        Add common update logic here
        """
        # Add your common update logic
        return super().update(instance, validated_data)

class BaseResponseSerializer(BaseSerializer):
    """
    Base serializer for standard API responses
    """
    class Meta(BaseSerializer.Meta):
        abstract = True

    def to_representation(self, instance) -> Dict[str, Any]:
        """
        Customize the response format
        """
        data = super().to_representation(instance)
        return {
            'status': 'success',
            'data': data,
            'message': None
        }

class BaseListSerializer(BaseSerializer):
    """
    Base serializer for list responses with pagination
    """
    class Meta(BaseSerializer.Meta):
        abstract = True

    def to_representation(self, instance) -> Dict[str, Any]:
        """
        Customize the list response format
        """
        data = super().to_representation(instance)
        return {
            'data': data,
            'total': len(data),
            'page': self.context.get('page', 1),
            'limit': self.context.get('limit', 10)
        }

class ErrorSerializer(serializers.Serializer):
    """
    Serializer for error responses
    """
    status = serializers.CharField(default='error')
    message = serializers.CharField()
    errors = serializers.DictField(required=False)

    class Meta:
        fields = ['status', 'message', 'errors']