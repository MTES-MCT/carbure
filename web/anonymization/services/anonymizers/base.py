"""
Base class for anonymizers.

This abstract class defines the common interface for all anonymizers.
"""

from abc import ABC, abstractmethod


class Anonymizer(ABC):
    @abstractmethod
    def get_queryset(self):
        """
        Returns the queryset of objects to anonymize.

        Returns:
            QuerySet of objects to process
        """
        pass

    def get_model(self):
        """
        Returns the model name for display.

        Returns:
            Model name (model class name)
        """
        return self.get_queryset().model

    @abstractmethod
    def get_updated_fields(self):
        """
        Returns the list of fields that can be updated.

        Returns:
            List of field names to pass to bulk_update()
        """
        pass

    @abstractmethod
    def process(self, instance):
        """
        Processes a model instance to anonymize it.

        Args:
            instance: Model instance to anonymize

        Returns:
            Tuple (updated_instance, modifications) where modifications is a dict
            of changes made {field_name: (old_value, new_value)}
        """
        pass

    @abstractmethod
    def get_display_name(self):
        """
        Returns the display name for this anonymizer (used in logs).

        Returns:
            Display name (e.g., "utilisateurs", "entités", "sites")
        """
        pass

    @abstractmethod
    def get_emoji(self):
        """
        Returns the emoji for this anonymizer (used in logs).

        Returns:
            Emoji string (e.g., "📝", "🏢", "📍")
        """
        pass
