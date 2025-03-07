"""
Base model for ArubaCloud resources.

This module provides a base model class for ArubaCloud resources,
with common functionality for serialization, validation, and attribute access.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Type, TypeVar, ClassVar, List, Set

T = TypeVar('T', bound='BaseModel')


class BaseModel:
    """
    Base model for ArubaCloud resources.
    
    This class provides common functionality for all ArubaCloud resource models,
    including serialization, validation, and attribute access.
    
    Attributes:
        id (Optional[str]): The resource ID.
        created_at (Optional[datetime]): The creation timestamp.
        updated_at (Optional[datetime]): The last update timestamp.
    """
    
    # Class variables for field definitions
    _required_fields: ClassVar[Set[str]] = set()
    _optional_fields: ClassVar[Set[str]] = {'id', 'created_at', 'updated_at'}
    _readonly_fields: ClassVar[Set[str]] = {'id', 'created_at', 'updated_at'}
    _field_types: ClassVar[Dict[str, Type]] = {
        'id': str,
        'created_at': datetime,
        'updated_at': datetime
    }
    _field_mappings: ClassVar[Dict[str, str]] = {
        'id': 'Id',
        'created_at': 'CreationDate',
        'updated_at': 'UpdatedDate'
    }
    
    def __init__(self, **kwargs):
        """
        Initialize the model.
        
        Args:
            **kwargs: Model attributes.
        """
        self.id: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        # Set attributes from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """
        Get a string representation of the model.
        
        Returns:
            A string representation of the model.
        """
        attrs = []
        for field in self._get_all_fields():
            if hasattr(self, field):
                value = getattr(self, field)
                if value is not None:
                    attrs.append(f"{field}={value!r}")
        
        return f"{self.__class__.__name__}({', '.join(attrs)})"
    
    @classmethod
    def _get_all_fields(cls) -> Set[str]:
        """
        Get all fields defined for the model.
        
        Returns:
            A set of all field names.
        """
        return cls._required_fields.union(cls._optional_fields)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create a model instance from a dictionary.
        
        Args:
            data: A dictionary of model attributes.
            
        Returns:
            A new model instance.
            
        Raises:
            ValueError: If required fields are missing.
        """
        # Check for required fields
        missing_fields = [field for field in cls._required_fields if cls._field_mappings.get(field, field) not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Create a dictionary of model attributes
        kwargs = {}
        for field in cls._get_all_fields():
            api_field = cls._field_mappings.get(field, field)
            if api_field in data:
                value = data[api_field]
                
                # Convert value to the expected type
                field_type = cls._field_types.get(field)
                if field_type and value is not None:
                    if field_type == datetime and isinstance(value, str):
                        try:
                            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except ValueError:
                            # If ISO format fails, try other common formats
                            try:
                                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                            except ValueError:
                                # Keep the original value if parsing fails
                                pass
                    elif field_type == bool and isinstance(value, str):
                        value = value.lower() == 'true'
                    elif field_type == int and isinstance(value, str):
                        try:
                            value = int(value)
                        except ValueError:
                            # Keep the original value if parsing fails
                            pass
                
                kwargs[field] = value
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary.
        
        Returns:
            A dictionary representation of the model.
        """
        result = {}
        for field in self._get_all_fields():
            if hasattr(self, field) and getattr(self, field) is not None:
                value = getattr(self, field)
                
                # Convert datetime to ISO format
                if isinstance(value, datetime):
                    value = value.isoformat()
                
                api_field = self._field_mappings.get(field, field)
                result[api_field] = value
        
        return result
    
    def validate(self) -> List[str]:
        """
        Validate the model.
        
        Returns:
            A list of validation error messages, or an empty list if valid.
        """
        errors = []
        
        # Check for required fields
        for field in self._required_fields:
            if not hasattr(self, field) or getattr(self, field) is None:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        for field, field_type in self._field_types.items():
            if hasattr(self, field) and getattr(self, field) is not None:
                value = getattr(self, field)
                if not isinstance(value, field_type):
                    errors.append(f"Invalid type for field {field}: expected {field_type.__name__}, got {type(value).__name__}")
        
        return errors
    
    def is_valid(self) -> bool:
        """
        Check if the model is valid.
        
        Returns:
            True if the model is valid, False otherwise.
        """
        return len(self.validate()) == 0
    
    def update(self, **kwargs) -> None:
        """
        Update model attributes.
        
        Args:
            **kwargs: Model attributes to update.
            
        Raises:
            ValueError: If attempting to update a readonly field.
        """
        for key, value in kwargs.items():
            if key in self._readonly_fields:
                raise ValueError(f"Cannot update readonly field: {key}")
            
            if hasattr(self, key):
                setattr(self, key, value)